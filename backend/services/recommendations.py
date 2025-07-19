import requests
from config import Config
from models import get_garment_by_id

def generate_recommendations(garment_id, user_id):
    """Generate clothing recommendations using Vellum AI"""
    try:
        if not Config.VELLUM_API_KEY:
            return []
        
        # Get garment info for context
        garment_info = None
        if garment_id in [g['id'] for g in Config.PRESET_GARMENTS]:
            garment_info = next(g for g in Config.PRESET_GARMENTS if g['id'] == garment_id)
        else:
            garment_doc = get_garment_by_id(garment_id)
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
            'Authorization': f'Bearer {Config.VELLUM_API_KEY}',
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