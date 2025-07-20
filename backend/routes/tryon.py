from flask import Blueprint, request, jsonify
import os
import uuid
import requests
import base64
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
from models import save_tryon_result, get_garment_by_id
from services.recommendations import generate_recommendations
from models import get_user_history
from utils import ensure_upload_folder, allowed_file
from config import Config
from datetime import datetime

tryon_bp = Blueprint('tryon', __name__)

# Segmind API configuration
SEGMIND_API_KEY = os.getenv('SEGMIND_API_KEY', 'SG_dfe39d0677343e9f')
SEGMIND_API_URL = "https://api.segmind.com/v1/idm-vton"

def image_file_to_base64(image_path):
    """Convert an image file to base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

def image_url_to_base64(image_url):
    """Fetch an image from a URL and convert it to base64"""
    response = requests.get(image_url)
    response.raise_for_status()
    image_data = response.content
    return base64.b64encode(image_data).decode('utf-8')

def get_garment_path(garment_id):
    """Get garment image path from preset or database"""
    if garment_id in [g['id'] for g in Config.PRESET_GARMENTS]:
        # Use preset garment
        garment = next(g for g in Config.PRESET_GARMENTS if g['id'] == garment_id)
        return garment['image_url']
    else:
        # Get custom garment from MongoDB
        garment_doc = get_garment_by_id(garment_id)
        if not garment_doc:
            raise ValueError("Garment not found")
        return garment_doc['filepath']

def get_garment_description(garment_id):
    """Get garment description for better try-on results"""
    if garment_id in [g['id'] for g in Config.PRESET_GARMENTS]:
        # Use preset garment description
        garment = next(g for g in Config.PRESET_GARMENTS if g['id'] == garment_id)
        return garment.get('description', garment['name'])
    else:
        # Get custom garment from MongoDB
        garment_doc = get_garment_by_id(garment_id)
        if garment_doc:
            return garment_doc.get('description', 'Clothing item')
        return 'Clothing item'

def determine_category(garment_id):
    """Determine the category of the garment for the API"""
    # Default category mapping based on garment names/descriptions
    category_keywords = {
        'upper_body': ['shirt', 'blouse', 'jacket', 'blazer', 'top', 'sweater'],
        'lower_body': ['jeans', 'pants', 'trousers', 'skirt'],
        'dresses': ['dress', 'gown']
    }
    
    if garment_id in [g['id'] for g in Config.PRESET_GARMENTS]:
        garment = next(g for g in Config.PRESET_GARMENTS if g['id'] == garment_id)
        garment_name = garment['name'].lower()
        garment_desc = garment.get('description', '').lower()
    else:
        garment_doc = get_garment_by_id(garment_id)
        if garment_doc:
            garment_name = garment_doc.get('name', '').lower()
            garment_desc = garment_doc.get('description', '').lower()
        else:
            return 'upper_body'  # Default fallback
    
    text_to_check = f"{garment_name} {garment_desc}"
    
    for category, keywords in category_keywords.items():
        if any(keyword in text_to_check for keyword in keywords):
            return category
    
    return 'upper_body'  # Default fallback

@tryon_bp.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint using Segmind API"""
    try:
        # Check for uploaded person image
        if 'person_image' not in request.files:
            return jsonify({"error": "person_image file is required"}), 400
        
        person_image_file = request.files['person_image']
        if person_image_file.filename == '':
            return jsonify({"error": "No person image file selected"}), 400
        
        if not allowed_file(person_image_file.filename):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
        
        garment_id = request.form.get('garment_id')  # Can be preset or custom
        user_id = request.form.get('user_id', 'anonymous')
        
        if not garment_id:
            return jsonify({"error": "garment_id is required"}), 400
        
        # Check if API key is configured
        if SEGMIND_API_KEY == 'YOUR_API_KEY':
            return jsonify({"error": "Segmind API key not configured"}), 500
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Save the person image temporarily
        person_image_id = str(uuid.uuid4())
        filename = secure_filename(f"person_{person_image_id}.jpg")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file
        person_image_file.save(filepath)
        
        try:
            # Get garment information
            garment_path = get_garment_path(garment_id)
            garment_description = get_garment_description(garment_id)
            category = determine_category(garment_id)
            
            # Convert images to base64
            person_b64 = image_file_to_base64(filepath)
            
            if garment_path.startswith('http'):
                garment_b64 = image_url_to_base64(garment_path)
            else:
                garment_b64 = image_file_to_base64(garment_path)
            
            # Prepare API request data
            data = {
                "crop": False,
                "seed": 42,
                "steps": 30,
                "category": category,
                "force_dc": False,
                "human_img": person_b64,
                "garm_img": garment_b64,
                "mask_only": False,
                "garment_des": garment_description
            }
            
            headers = {'x-api-key': SEGMIND_API_KEY}
            
            print(f"🔄 Making Segmind API request for category: {category}")
            
            # Make the API request
            response = requests.post(SEGMIND_API_URL, json=data, headers=headers)
            
            if response.status_code != 200:
                return jsonify({
                    "error": f"Segmind API error: {response.status_code} - {response.text}"
                }), 500
            
            # Save the result image
            result_id = str(uuid.uuid4())
            output_path = f"uploads/tryon_result_{result_id}.png"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Convert response to PIL Image and save
            image_data = response.content
            image = Image.open(BytesIO(image_data))
            image.save(output_path, 'PNG')
            
            # Save to database
            result_data = {
                "id": result_id,
                "user_id": user_id,
                "garment_id": garment_id,
                "original_image": filepath,
                "result_image": output_path,
                "masked_image": output_path,
                "created_at": datetime.utcnow(),
                "public_url": f"https://your-domain.com/results/{result_id}.png",
                "api_provider": "segmind",
                "category": category,
                "garment_description": garment_description
            }
            
            save_tryon_result(result_data)
            
            # Generate recommendations using Vellum with real catalog
            # TODO: In production, get the real catalog from database or frontend
            # For now, using preset garments as catalog
            try:
                recommendations = generate_recommendations(garment_id, user_id)
            except Exception as e:
                print(f"Warning: Could not generate recommendations: {e}")
                recommendations = []
            
            print(f"✅ Virtual try-on completed successfully using Segmind API")
            
            # Return success response
            return jsonify({
                "success": True,
                "result_id": result_id,
                "result_image": output_path,
                "public_url": result_data['public_url'],
                "category": category,
                "api_provider": "segmind",
                "garment_description": garment_description,
                "recommendations": recommendations,
                "message": "Virtual try-on completed successfully"
            })
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Segmind API request failed: {str(e)}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    error_msg += f" - HTTP {e.response.status_code}"
            
            return jsonify({"error": error_msg}), 500
            
        except Exception as e:
            return jsonify({"error": f"Try-on processing failed: {str(e)}"}), 500
            
        finally:
            # Clean up the temporary person image file
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Warning: Could not clean up temporary file {filepath}: {e}")
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@tryon_bp.route('/user-history/<user_id>', methods=['GET'])
def get_user_history_route(user_id):
    """Get user's try-on history"""
    try:
        history = get_user_history(user_id)
        
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 