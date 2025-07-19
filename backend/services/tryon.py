from gradio_client import Client, file
from config import Config
from models import save_tryon_result
from datetime import datetime
import uuid

# Initialize try-on client
try:
    tryon_client = Client("yisol/IDM-VTON")
    print("✅ Try-on client initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize try-on client: {e}")
    tryon_client = None

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

def perform_virtual_tryon(person_image_path, garment_id, user_id='anonymous'):
    """Perform virtual try-on operation"""
    try:
        # Check if try-on client is available
        if not tryon_client:
            raise Exception("Try-on service is currently unavailable. Please try again later.")
        
        # Get garment image path
        garment_path = get_garment_path(garment_id)
        
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
        
        # Generate result ID and save to database
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
        
        save_tryon_result(result_data)
        
        return {
            "success": True,
            "result_id": result_id,
            "result_image": output_path,
            "public_url": result_data['public_url'],
            "message": "Virtual try-on completed successfully"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        } 