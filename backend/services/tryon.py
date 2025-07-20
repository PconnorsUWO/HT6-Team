import requests
import base64
from config import Config
from models import save_tryon_result
from datetime import datetime
import uuid
import os
from PIL import Image
from io import BytesIO

# Segmind API configuration
SEGMIND_API_KEY = os.getenv('SEGMIND_API_KEY')
SEGMIND_API_URL = "https://api.segmind.com/v1/idm-vton"

def image_file_to_base64(image_path):
    """Convert an image file from the filesystem to base64"""
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
    from models import get_garment_by_id
    
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
    from models import get_garment_by_id
    
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
    from models import get_garment_by_id
    
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

def perform_virtual_tryon(person_image_path, garment_id, user_id='anonymous'):
    """Perform virtual try-on operation using Segmind API"""
    try:
        # Check if API key is configured
        if SEGMIND_API_KEY == 'YOUR_API_KEY':
            raise Exception("Segmind API key not configured. Please set SEGMIND_API_KEY environment variable.")
        
        # Get garment image path
        garment_path = get_garment_path(garment_id)
        
        # Get garment description and category
        garment_description = get_garment_description(garment_id)
        category = determine_category(garment_id)
        
        # Convert images to base64
        if person_image_path.startswith('http'):
            human_img_b64 = image_url_to_base64(person_image_path)
        else:
            human_img_b64 = image_file_to_base64(person_image_path)
        
        if garment_path.startswith('http'):
            garm_img_b64 = image_url_to_base64(garment_path)
        else:
            garm_img_b64 = image_file_to_base64(garment_path)
        
        # Prepare API request
        data = {
            "crop": False,
            "seed": 42,
            "steps": 30,
            "category": category,
            "force_dc": False,
            "human_img": human_img_b64,
            "garm_img": garm_img_b64,
            "mask_only": False,
            "garment_des": garment_description
        }
        
        headers = {'x-api-key': SEGMIND_API_KEY}
        
        # Make API request
        print(f"🔄 Making Segmind API request for category: {category}")
        response = requests.post(SEGMIND_API_URL, json=data, headers=headers)
        response.raise_for_status()
        
        # The response content is the generated image
        image_data = response.content
        
        # Save the result image
        result_id = str(uuid.uuid4())
        output_path = f"uploads/tryon_result_{result_id}.png"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Convert response to PIL Image and save
        image = Image.open(BytesIO(image_data))
        image.save(output_path, 'PNG')
        
        # Generate result data and save to database
        result_data = {
            "id": result_id,
            "user_id": user_id,
            "garment_id": garment_id,
            "original_image": person_image_path,
            "result_image": output_path,
            "masked_image": output_path,  # Segmind API returns the final result
            "created_at": datetime.utcnow(),
            "public_url": f"https://your-domain.com/results/{result_id}.png",
            "api_provider": "segmind",
            "category": category,
            "garment_description": garment_description
        }
        
        save_tryon_result(result_data)
        
        print(f"✅ Virtual try-on completed successfully using Segmind API")
        
        return {
            "success": True,
            "result_id": result_id,
            "result_image": output_path,
            "public_url": result_data['public_url'],
            "category": category,
            "api_provider": "segmind",
            "message": "Virtual try-on completed successfully"
        }
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Segmind API request failed: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                error_msg += f" - {error_detail}"
            except:
                error_msg += f" - HTTP {e.response.status_code}"
        
        return {
            "success": False,
            "error": error_msg
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 