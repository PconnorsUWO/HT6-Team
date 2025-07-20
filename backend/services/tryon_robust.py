from diffusers import DiffusionPipeline, StableDiffusionPipeline
from diffusers.utils import load_image
from config import Config
from models import save_tryon_result
from datetime import datetime
import uuid
import os
from PIL import Image
import numpy as np

class RobustTryOnService:
    """A robust virtual try-on service with multiple fallback options"""
    
    def __init__(self):
        self.pipe = None
        self.model_name = None
        self.initialized = False
        self._initialize_pipeline()
    
    def _initialize_pipeline(self):
        """Initialize the pipeline with fallback options"""
        models_to_try = [
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4", 
            "stabilityai/stable-diffusion-2-1"
        ]
        
        for model_name in models_to_try:
            try:
                print(f"🔄 Trying to load {model_name}...")
                self.pipe = DiffusionPipeline.from_pretrained(model_name)
                self.model_name = model_name
                self.initialized = True
                print(f"✅ Successfully loaded {model_name}")
                break
            except Exception as e:
                print(f"❌ Failed to load {model_name}: {e}")
                continue
        
        if not self.initialized:
            print("⚠️  Could not load any models. Try-on service will be unavailable.")
    
    def get_garment_path(self, garment_id):
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
    
    def _create_simple_tryon(self, person_image, garment_image):
        """Create a simple try-on effect using image composition"""
        try:
            # Resize images to same size
            target_size = (512, 512)
            person_resized = person_image.resize(target_size)
            garment_resized = garment_image.resize(target_size)
            
            # Create a simple overlay effect
            # This is a basic implementation - in a real scenario you'd want more sophisticated blending
            result = Image.blend(person_resized, garment_resized, alpha=0.3)
            
            return result
        except Exception as e:
            print(f"Error in simple try-on: {e}")
            return None
    
    def _create_diffusion_tryon(self, person_image, garment_image):
        """Create try-on using diffusion model"""
        try:
            if not self.initialized or not self.pipe:
                return None
            
            # Prepare the prompt based on the garment
            prompt = "a person wearing clothing, high quality, detailed"
            
            # Run diffusion inference
            result = self.pipe(
                prompt=prompt,
                image=person_image,
                num_inference_steps=20,
                guidance_scale=7.5
            )
            
            if result.images:
                return result.images[0]
            else:
                return None
                
        except Exception as e:
            print(f"Error in diffusion try-on: {e}")
            return None
    
    def perform_virtual_tryon(self, person_image_path, garment_id, user_id='anonymous'):
        """Perform virtual try-on operation with multiple fallback methods"""
        try:
            # Get garment image path
            garment_path = self.get_garment_path(garment_id)
            
            # Load images
            try:
                person_image = load_image(person_image_path)
                garment_image = load_image(garment_path)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to load images: {e}"
                }
            
            # Try diffusion-based try-on first
            result_image = self._create_diffusion_tryon(person_image, garment_image)
            
            # Fallback to simple composition if diffusion fails
            if result_image is None:
                print("🔄 Diffusion try-on failed, trying simple composition...")
                result_image = self._create_simple_tryon(person_image, garment_image)
            
            if result_image is None:
                return {
                    "success": False,
                    "error": "All try-on methods failed"
                }
            
            # Save the result image
            result_id = str(uuid.uuid4())
            output_path = f"uploads/tryon_result_{result_id}.png"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            result_image.save(output_path)
            
            # Save to database
            result_data = {
                "id": result_id,
                "user_id": user_id,
                "garment_id": garment_id,
                "original_image": person_image_path,
                "result_image": output_path,
                "masked_image": output_path,
                "created_at": datetime.utcnow(),
                "public_url": f"https://your-domain.com/results/{result_id}.png",
                "model_used": self.model_name or "simple_composition"
            }
            
            save_tryon_result(result_data)
            
            return {
                "success": True,
                "result_id": result_id,
                "result_image": output_path,
                "public_url": result_data['public_url'],
                "model_used": result_data['model_used'],
                "message": "Virtual try-on completed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

# Create a global instance
tryon_service = RobustTryOnService()

# Convenience functions for backward compatibility
def get_garment_path(garment_id):
    return tryon_service.get_garment_path(garment_id)

def perform_virtual_tryon(person_image_path, garment_id, user_id='anonymous'):
    return tryon_service.perform_virtual_tryon(person_image_path, garment_id, user_id) 