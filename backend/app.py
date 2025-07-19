from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, file
import os
import tempfile
from werkzeug.utils import secure_filename
import uuid
import requests
import json
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize clients
tryon_client = Client("yisol/IDM-VTON")

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb+srv://dbUser:1234567890@cluster0.iic7hii.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.virtual_tryon

# API Keys
VELLUM_API_KEY = os.getenv('VELLUM_API_KEY')
TWELVELABS_API_KEY = os.getenv('TWELVELABS_API_KEY')

# Preset garments (to be expanded)
PRESET_GARMENTS = [
    {
        "id": "blue_shirt",
        "name": "Blue Casual Shirt",
        "description": "A comfortable blue casual shirt perfect for everyday wear",
        "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=400&fit=crop"
    },
    {
        "id": "red_dress",
        "name": "Red Evening Dress",
        "description": "An elegant red evening dress for special occasions",
        "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop"
    },
    {
        "id": "white_blouse",
        "name": "White Blouse",
        "description": "A classic white blouse for professional settings",
        "image_url": "https://images.unsplash.com/photo-1564257631407-3deb5d3d3b3b?w=300&h=400&fit=crop"
    },
    {
        "id": "black_jacket",
        "name": "Black Leather Jacket",
        "description": "A stylish black leather jacket for a cool look",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=400&fit=crop"
    },
    {
        "id": "denim_jeans",
        "name": "Blue Denim Jeans",
        "description": "Classic blue denim jeans for casual comfort",
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=400&fit=crop"
    },
    {
        "id": "summer_dress",
        "name": "Floral Summer Dress",
        "description": "A beautiful floral summer dress for warm days",
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=300&h=400&fit=crop"
    }
]

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "message": "Virtual Try-On API is running",
        "features": ["video_recording", "twelvelabs_integration", "mongodb_storage", "vellum_recommendations"]
    })

@app.route('/preset-garments', methods=['GET'])
def get_preset_garments():
    """Get available preset garments"""
    return jsonify({
        "success": True,
        "garments": PRESET_GARMENTS
    })

@app.route('/upload-garment', methods=['POST'])
def upload_garment():
    """Upload a custom garment to MongoDB"""
    try:
        if 'garment_image' not in request.files:
            return jsonify({"error": "No garment image provided"}), 400
        
        garment_file = request.files['garment_image']
        if garment_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(garment_file.filename):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
        
        # Generate unique filename
        garment_id = str(uuid.uuid4())
        filename = secure_filename(f"garment_{garment_id}.jpg")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save file
        garment_file.save(filepath)
        
        # Store in MongoDB
        garment_data = {
            "id": garment_id,
            "filename": filename,
            "filepath": filepath,
            "uploaded_at": datetime.utcnow(),
            "user_id": request.form.get('user_id', 'anonymous'),  # Will be replaced with actual auth
            "description": request.form.get('description', 'Custom garment')
        }
        
        db.garments.insert_one(garment_data)
        
        return jsonify({
            "success": True,
            "garment_id": garment_id,
            "message": "Garment uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/process-video', methods=['POST'])
def process_video():
    """Process video recording with TwelveLabs to find best frames"""
    try:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video_file']
        if video_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type. Only MP4, MOV, AVI are allowed"}), 400
        
        # Save video temporarily
        video_filename = secure_filename(f"video_{uuid.uuid4()}.mp4")
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        
        # Upload to TwelveLabs for processing
        headers = {
            'Authorization': f'Bearer {TWELVELABS_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Upload video to TwelveLabs
        with open(video_path, 'rb') as f:
            files = {'file': f}
            upload_response = requests.post(
                'https://api.twelvelabs.io/v1.1/tasks',
                headers={'Authorization': f'Bearer {TWELVELABS_API_KEY}'},
                files=files,
                data={'index_id': 'your_index_id'}  # You'll need to create an index
            )
        
        if upload_response.status_code != 200:
            return jsonify({"error": "Failed to upload video to TwelveLabs"}), 500
        
        # Search for frames where person is standing still
        search_payload = {
            "query": "person standing still, full body visible, good lighting",
            "video_id": upload_response.json()['video_id'],
            "search_options": ["visual", "conversation", "text_in_video"]
        }
        
        search_response = requests.post(
            'https://api.twelvelabs.io/v1.1/search',
            headers=headers,
            json=search_payload
        )
        
        if search_response.status_code != 200:
            return jsonify({"error": "Failed to search video frames"}), 500
        
        # Get the best frame
        search_results = search_response.json()
        best_frame = search_results['data'][0] if search_results['data'] else None
        
        # Clean up video file
        os.remove(video_path)
        
        if not best_frame:
            return jsonify({"error": "No suitable frames found in video"}), 400
        
        return jsonify({
            "success": True,
            "best_frame": best_frame,
            "message": "Video processed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint with MongoDB storage and Vellum recommendations"""
    try:
        # Get parameters
        person_image_path = request.form.get('person_image_path')
        garment_id = request.form.get('garment_id')  # Can be preset or custom
        user_id = request.form.get('user_id', 'anonymous')
        
        if not person_image_path or not garment_id:
            return jsonify({"error": "person_image_path and garment_id are required"}), 400
        
        # Get garment image path
        garment_path = None
        if garment_id in [g['id'] for g in PRESET_GARMENTS]:
            # Use preset garment
            garment = next(g for g in PRESET_GARMENTS if g['id'] == garment_id)
            garment_path = garment['image_url']
        else:
            # Get custom garment from MongoDB
            garment_doc = db.garments.find_one({"id": garment_id})
            if not garment_doc:
                return jsonify({"error": "Garment not found"}), 404
            garment_path = garment_doc['filepath']
        
        # Run virtual try-on
        result = tryon_client.predict(
            {"background": file(person_image_path), "layers": [], "composite": None},
            file(garment_path),
            "Virtual try-on",
            True,  # is_checked
            False,  # is_checked_crop
            30,  # denoise_steps
            42,  # seed
            api_name="/tryon"
        )
        
        output_path, masked_output_path = result
        
        # Upload result to MongoDB and get public URL
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "user_id": user_id,
            "garment_id": garment_id,
            "original_image": person_image_path,
            "result_image": output_path,
            "masked_image": masked_output_path,
            "created_at": datetime.utcnow(),
            "public_url": f"https://your-domain.com/results/{result_id}.jpg"  # You'll need to implement file hosting
        }
        
        db.tryon_results.insert_one(result_data)
        
        # Generate recommendations using Vellum
        recommendations = generate_recommendations(garment_id, user_id)
        
        return jsonify({
            "success": True,
            "result_id": result_id,
            "result_image": output_path,
            "public_url": result_data['public_url'],
            "recommendations": recommendations,
            "message": "Virtual try-on completed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def generate_recommendations(garment_id, user_id):
    """Generate clothing recommendations using Vellum AI"""
    try:
        if not VELLUM_API_KEY:
            return []
        
        # Get garment info for context
        garment_info = None
        if garment_id in [g['id'] for g in PRESET_GARMENTS]:
            garment_info = next(g for g in PRESET_GARMENTS if g['id'] == garment_id)
        else:
            garment_doc = db.garments.find_one({"id": garment_id})
            if garment_doc:
                garment_info = garment_doc
        
        if not garment_info:
            return []
        
        # Call Vellum API for recommendations
        vellum_payload = {
            "input": {
                "garment_description": garment_info.get('description', ''),
                "user_preferences": "modern, comfortable, stylish",
                "occasion": "casual"
            },
            "prompt": """
            Based on the garment description and user preferences, suggest 3 complementary clothing items 
            that would go well with this piece. Consider style, color coordination, and occasion.
            Return as JSON array with items containing: name, description, style_category, color_suggestion
            """
        }
        
        headers = {
            'Authorization': f'Bearer {VELLUM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.vellum.ai/v1/generate',
            headers=headers,
            json=vellum_payload
        )
        
        if response.status_code == 200:
            recommendations = response.json().get('recommendations', [])
            return recommendations
        else:
            return []
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return []

@app.route('/user-history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Get user's try-on history"""
    try:
        results = list(db.tryon_results.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(10))
        
        return jsonify({
            "success": True,
            "history": results
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 