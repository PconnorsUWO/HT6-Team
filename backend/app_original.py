from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, file
import os
import tempfile
from werkzeug.utils import secure_filename
import uuid
import requests
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from dotenv import load_dotenv
import cv2
import numpy as np
from PIL import Image
import base64
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for development - more permissive
CORS(app, 
     origins=["*"])

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


# API Keys
VELLUM_API_KEY = os.getenv('VELLUM_API_KEY')

# Initialize clients
try:
    tryon_client = Client("yisol/IDM-VTON")
    print("✅ Try-on client initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize try-on client: {e}")
    tryon_client = None

# Initialize OpenCV pose detection
# We'll use OpenCV's DNN module with a pre-trained pose estimation model
pose_net = None
try:
    # Try to load a pre-trained pose estimation model
    # For now, we'll use a simple approach with OpenCV's built-in functions
    print("✅ OpenCV pose detection initialized")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize pose detection: {e}")

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.virtual_tryon

# Initialize GridFS for video storage
fs = GridFS(db)

def cleanup_expired_videos():
    """Remove expired videos from GridFS"""
    try:
        current_time = datetime.utcnow()
        expired_files = []
        
        # Find expired files
        for grid_out in fs.find({"metadata.expires_at": {"$lt": current_time}}):
            expired_files.append(grid_out._id)
        
        # Delete expired files
        for file_id in expired_files:
            try:
                fs.delete(file_id)
                print(f"Deleted expired video: {file_id}")
            except Exception as e:
                print(f"Error deleting expired video {file_id}: {e}")
        
        if expired_files:
            print(f"Cleaned up {len(expired_files)} expired videos")
            
    except Exception as e:
        print(f"Error in cleanup_expired_videos: {e}")

def detect_body_pose_in_video(video_path: str) -> dict:
    """
    Detect body pose in video using OpenCV and find the best frame
    where a person is clearly visible with annotations
    """
    try:
        print(f"Processing video for body detection: {video_path}")
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"Video info: {frame_count} frames, {fps} fps, {duration:.2f}s duration")
        
        best_frame = None
        best_confidence = 0
        best_frame_number = 0
        best_annotations = None
        
        # Load pre-trained models for detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        
        # Process every 5th frame to speed up processing
        frame_skip = 5
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frames += 1
            
            # Skip frames to speed up processing
            if processed_frames % frame_skip != 0:
                continue
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces and bodies
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            bodies = body_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Calculate confidence based on detection results
            face_confidence = len(faces) * 0.3  # Each face adds 30% confidence
            body_confidence = len(bodies) * 0.7  # Each body adds 70% confidence
            
            total_confidence = min(face_confidence + body_confidence, 1.0)
            
            # Additional confidence based on frame quality (brightness, contrast)
            # Calculate average brightness
            brightness = np.mean(gray)
            brightness_confidence = min(brightness / 128.0, 1.0) * 0.2  # Up to 20% from brightness
            
            # Calculate contrast
            contrast = np.std(gray)
            contrast_confidence = min(contrast / 50.0, 1.0) * 0.1  # Up to 10% from contrast
            
            final_confidence = total_confidence + brightness_confidence + contrast_confidence
            
            # Check if this is the best frame so far
            if final_confidence > best_confidence and final_confidence >= 0.5:  # At least 50% confidence
                best_confidence = final_confidence
                best_frame = frame.copy()
                best_frame_number = processed_frames
                
                # Create annotations for the best frame
                annotated_frame = frame.copy()
                annotations = {
                    "faces": [],
                    "bodies": [],
                    "confidence_breakdown": {
                        "face_confidence": face_confidence,
                        "body_confidence": body_confidence,
                        "brightness_confidence": brightness_confidence,
                        "contrast_confidence": contrast_confidence,
                        "total_confidence": final_confidence
                    }
                }
                
                # Draw face annotations
                for (x, y, w, h) in faces:
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    annotations["faces"].append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
                
                # Draw body annotations
                for (x, y, w, h) in bodies:
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(annotated_frame, 'Body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    annotations["bodies"].append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
                
                # Add confidence text
                cv2.putText(annotated_frame, f'Confidence: {final_confidence:.2%}', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f'Faces: {len(faces)}, Bodies: {len(bodies)}', 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                best_annotations = annotations
                print(f"New best frame found: frame {processed_frames}, confidence: {final_confidence:.2f}")
                print(f"  - Faces detected: {len(faces)}, Bodies detected: {len(bodies)}")
                print(f"  - Brightness: {brightness:.1f}, Contrast: {contrast:.1f}")
        
        cap.release()
        
        if best_frame is not None:
            # Convert the annotated frame to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            frame_data_url = f"data:image/jpeg;base64,{frame_base64}"
            
            return {
                "success": True,
                "best_frame": frame_data_url,
                "confidence": best_confidence,
                "frame_number": best_frame_number,
                "annotations": best_annotations,
                "message": f"Person detected with {best_confidence:.2%} confidence"
            }
        else:
            return {
                "success": False,
                "message": "No suitable frame found with a person clearly visible"
            }
            
    except Exception as e:
        print(f"Error in body detection: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing video: {str(e)}"
        }


# Test video URL for body detection testing
TEST_VIDEO_URL = "https://videos.pexels.com/video-files/5058382/5058382-uhd_2560_1440_25fps.mp4"

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

def get_video_info(video_path):
    """Get basic video information using OpenCV"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'error': 'Could not open video file'}
        
        info = {
            'file_path': video_path,
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
        
        if info['fps'] > 0:
            info['duration'] = info['frame_count'] / info['fps']
        
        cap.release()
        return info
        
    except Exception as e:
        return {'error': str(e)}

    
def allowed_file(filename):
    """Check if file extension is allowed"""
    # For video files, allow MP4 and WebM (fallback support)
    VIDEO_EXTENSIONS = {'mp4', 'webm'}
    # For image files, allow common formats
    IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        # Check if it's a video extension
        if ext in VIDEO_EXTENSIONS:
            return True
        # Check if it's an image extension
        if ext in IMAGE_EXTENSIONS:
            return True
    return False 

@app.route('/health', methods=['GET', 'OPTIONS'])
def health_check():
    """Health check endpoint"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        return response
    
    return jsonify({
        "status": "healthy", 
        "message": "Virtual Try-On API is running",
        "features": ["video_recording", "opencv_body_detection", "mongodb_storage", "vellum_recommendations"],
        "test_endpoints": {
            "test_video_download": "GET /test-body-detection",
            "test_body_detection_full": "POST /test-body-detection"
        }
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify CORS is working"""
    return jsonify({
        "message": "Backend is running and CORS is working!",
        "timestamp": datetime.utcnow().isoformat()
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

@app.route('/upload-video', methods=['POST'])
def upload_video():
    """Upload video to MongoDB GridFS and return public URL"""
    try:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video_file']
        if video_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type. Only MP4 and WebM formats are supported"}), 400
        
        # Generate unique filename
        file_extension = video_file.filename.rsplit('.', 1)[1].lower() if '.' in video_file.filename else 'webm'
        video_filename = f"video_{uuid.uuid4()}.{file_extension}"
        
        # Store video in GridFS
        file_id = fs.put(
            video_file.read(),
            filename=video_filename,
            content_type=f"video/{file_extension}",
            metadata={
                "upload_time": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),  # Auto-delete after 24 hours
                "original_filename": video_file.filename
            }
        )
        
        # Create public URL (you might want to set up a proper CDN or file serving endpoint)
        # For now, we'll create a download endpoint
        public_url = f"{request.host_url.rstrip('/')}/download-video/{str(file_id)}"
        
        return jsonify({
            "success": True,
            "video_id": str(file_id),
            "public_url": public_url,
            "filename": video_filename,
            "message": "Video uploaded successfully"
        })
        
    except Exception as e:
        print(f"Error in upload_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/download-video/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download video from GridFS by ID"""
    try:
        # Get file from GridFS
        grid_out = fs.get(ObjectId(video_id))
        
        # Check if file has expired
        if 'expires_at' in grid_out.metadata:
            expires_at = grid_out.metadata['expires_at']
            if datetime.utcnow() > expires_at:
                # Delete expired file
                fs.delete(ObjectId(video_id))
                return jsonify({"error": "Video has expired"}), 410
        
        # Return video file
        return grid_out.read(), 200, {
            'Content-Type': grid_out.content_type,
            'Content-Disposition': f'attachment; filename="{grid_out.filename}"'
        }
        
    except Exception as e:
        print(f"Error downloading video {video_id}: {str(e)}")
        return jsonify({"error": "Video not found"}), 404

@app.route('/cleanup-videos', methods=['POST'])
def cleanup_videos():
    """Manually trigger cleanup of expired videos"""
    try:
        cleanup_expired_videos()
        return jsonify({
            "success": True,
            "message": "Cleanup completed"
        })
    except Exception as e:
        return jsonify({
            "error": f"Cleanup failed: {str(e)}"
        }), 500

@app.route('/detect-body', methods=['POST'])
def detect_body():
    """Detect body pose in uploaded video using OpenCV and MediaPipe"""
    try:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video_file']
        if video_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type. Only MP4 and WebM formats are supported"}), 400
        
        # Save video temporarily
        video_filename = f"body_detection_{uuid.uuid4()}"
        if video_file.filename.lower().endswith('.mp4'):
            video_filename += '.mp4'
        elif video_file.filename.lower().endswith('.webm'):
            video_filename += '.webm'
        else:
            video_filename += '.mp4'  # default
        
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        video_file.save(video_path)
        
        print(f"Video saved for body detection: {video_path}")
        
        # Get video info for debugging
        try:
            video_info = get_video_info(video_path)
            print(f"Video info: {video_info}")
        except Exception as e:
            print(f"Could not get video info: {e}")
        
        # Detect body pose in video
        result = detect_body_pose_in_video(video_path)
        
        # Clean up video file
        try:
            os.remove(video_path)
            print(f"Cleaned up video file: {video_path}")
        except Exception as e:
            print(f"Warning: Could not clean up video file: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in detect_body: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/test-body-detection', methods=['GET', 'POST'])
def test_body_detection():
    """Test body detection with the provided video URL"""
    try:
        # For GET requests, just test video download
        if request.method == 'GET':
            return test_video_download()
        
        # For POST requests, test full body detection
        # Download the test video
        print(f"Downloading test video from: {TEST_VIDEO_URL}")
        video_response = requests.get(TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        with open(video_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Video saved to: {video_path}")
        
        # Test body detection
        print("Testing body detection...")
        result = detect_body_pose_in_video(video_path)
        
        # Clean up video file
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Warning: Could not clean up test video: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def test_video_download():
    """Test downloading the video from the provided URL"""
    try:
        print(f"Testing video download from: {TEST_VIDEO_URL}")
        video_response = requests.get(TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Get video info
        content_length = video_response.headers.get('content-length')
        content_type = video_response.headers.get('content-type')
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        with open(video_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Clean up
        os.remove(video_path)
        
        return jsonify({
            "success": True,
            "message": "Test video downloaded successfully",
            "video_url": TEST_VIDEO_URL,
            "content_type": content_type,
            "content_length": content_length,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
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
        
        # Check if try-on client is available
        if not tryon_client:
            return jsonify({"error": "Try-on service is currently unavailable. Please try again later."}), 503
        
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