import sys
import os
from config import Config

# Add the parent directory to the Python path to access style_service module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from style_service import VellumStyleService, UserStyleProfile, CatalogueItem
    STYLE_SERVICE_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import style service: {e}")
    VellumStyleService = None
    UserStyleProfile = None
    CatalogueItem = None
    STYLE_SERVICE_AVAILABLE = False

def generate_recommendations(garment_url, garment_description, user_id, catalogue_items=None):
    """Generate clothing recommendations using Vellum AI with full catalog context"""
    try:
        if not STYLE_SERVICE_AVAILABLE or not VellumStyleService:
            print("Warning: Style service not available for recommendations")
            return []
            
        if not Config.VELLUM_API_KEY:
            print("Warning: VELLUM_API_KEY not configured")
            return []
        
        # Create a basic user profile for recommendations
        # In a real app, this would come from user data/preferences
        user_profile_data = {
            'session_id': f"tryon_{user_id}",
            'date': '',
            'style_words': ['modern', 'comfortable', 'stylish'],
            'style_message': 'Looking for complementary pieces',
            'style_inspiration': '',
            'daily_needs': ['casual'],
            'occasion': 'casual',
            'avoid_styles': [],
            'avoid_materials': [],
            'material_sensitivities': [],
            'dominant_colors': [],
            'accessory_preferences': [],
            'budget_range': '$50-150',
            'notes': f'Finding items to complement selected garment',
            'standard_sizes': {},
            'body_measurements': {},
            'fit_preferences': [],
            'skin_tone': '',
            'hair': '',
            'eyes': '',
            'location': '',
            'weather_snapshot': '',
            'weather_tags': []
        }
        
        # Use provided catalogue items (should come from frontend with full catalogue.ts data)
        if not catalogue_items:
            print("Warning: No catalogue items provided - recommendations will be limited")
            return []
        
        # Create VellumStyleService instance
        service = VellumStyleService()
        
        # Create user profile and catalogue items
        user_profile = service.create_user_profile_from_dict(user_profile_data)
        catalogue_list = service.create_catalogue_items_from_list(catalogue_items)
        
        # Execute the style workflow
        recommendations = service.execute_style_workflow(user_profile, catalogue_list)
        
        # Extract recommendation items from the response
        if recommendations and 'final-output' in recommendations:
            if 'top_10' in recommendations['final-output']:
                items = recommendations['final-output']['top_10'][:3]  # Get top 3
                return [
                    {
                        "name": item.get('item', {}).get('name', 'Recommended Item'),
                        "description": item.get('item', {}).get('desc', 'Stylish recommendation'),
                        "style_category": item.get('item', {}).get('category', 'clothing'),
                        "color_suggestion": "Coordinated colors"
                    }
                    for item in items
                ]
        
        # Fallback format
        return []
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return [] 