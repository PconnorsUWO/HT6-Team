from flask import Blueprint, request, jsonify
import os
import uuid
import requests
import base64
from PIL import Image
from io import BytesIO
from werkzeug.utils import secure_filename
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

def determine_category_from_url(garment_url, garment_description=""):
    """Determine the category of the garment from URL and description"""
    # Default category mapping based on URL path and description
    category_keywords = {
        'upper_body': ['shirt', 'blouse', 'jacket', 'blazer', 'top', 'sweater', 'polo', 'button'],
        'lower_body': ['jeans', 'pants', 'trousers', 'skirt', 'shorts'],
        'dresses': ['dress', 'gown', 'jumpsuit']
    }
    
    text_to_check = f"{garment_url} {garment_description}".lower()
    
    for category, keywords in category_keywords.items():
        if any(keyword in text_to_check for keyword in keywords):
            return category
    
    return 'upper_body'  # Default fallback

@tryon_bp.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint using Segmind API with direct garment URL"""
    try:
        # Check for uploaded person image
        if 'person_image' not in request.files:
            return jsonify({"error": "person_image file is required"}), 400
        
        person_image_file = request.files['person_image']
        if person_image_file.filename == '':
            return jsonify({"error": "No person image file selected"}), 400
        
        if not allowed_file(person_image_file.filename):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
        
        # Get garment URL instead of garment_id
        garment_url = request.form.get('garment_url')  
        garment_description = request.form.get('garment_description', 'Clothing item')
        user_id = request.form.get('user_id', 'anonymous')

        # print info received
        print("garment_url", garment_url)
        print("garment_description", garment_description)
        print("user_id", user_id)   
        print("person_image_file", person_image_file.filename)
        
        if not garment_url:
            return jsonify({"error": "garment_url is required"}), 400
        
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
            # Determine category from URL and description
            category = determine_category_from_url(garment_url, garment_description)
            
            # Convert images to base64
            person_b64 = image_file_to_base64(filepath)
            
            # Always treat garment_url as a URL (since it comes from frontend)
            print(f"🔄 Fetching garment image from URL: {garment_url}")
            garment_b64 = image_url_to_base64(garment_url)
            
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
            
            # Create result data (no database save since we're not using MongoDB)
            result_data = {
                "id": result_id,
                "user_id": user_id,
                "garment_url": garment_url,
                "garment_description": garment_description,
                "original_image": filepath,
                "result_image": output_path,
                "created_at": datetime.utcnow().isoformat(),
                "public_url": f"https://your-domain.com/results/{result_id}.png",
                "api_provider": "segmind",
                "category": category
            }
            
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
                "garment_url": garment_url,
                "message": "Virtual try-on completed successfully"
            })
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
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