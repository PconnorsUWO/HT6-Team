from flask import Blueprint, request, jsonify
import sys
import os

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

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/style-recommendations', methods=['POST'])
def get_style_recommendations():
    """Get personalized style recommendations based on user profile and catalogue"""
    try:
        if not STYLE_SERVICE_AVAILABLE or VellumStyleService is None:
            return jsonify({"error": "Style service not available. Please check your environment setup."}), 503
        
        data = request.get_json()
        
        # Validate required fields
        if 'user_profile' not in data:
            return jsonify({"error": "Missing required field: user_profile"}), 400
        
        if 'catalogue_items' not in data:
            return jsonify({"error": "Missing required field: catalogue_items"}), 400
        
        # Create VellumStyleService instance
        service = VellumStyleService()
        
        # Create user profile from data
        user_profile = service.create_user_profile_from_dict(data['user_profile'])
        
        # Create catalogue items from data
        catalogue_items = service.create_catalogue_items_from_list(data['catalogue_items'])
        
        # Execute the style workflow
        recommendations = service.execute_style_workflow(user_profile, catalogue_items)
        
        return jsonify({
            "success": True,
            "user_session_id": user_profile.session_id,
            "recommendations": recommendations,
            "catalogue_count": len(catalogue_items),
            "message": "Style recommendations generated successfully"
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to generate recommendations: {str(e)}"}), 500


@recommendations_bp.route('/quick-recommendations', methods=['POST'])
def get_quick_recommendations():
    """Get quick style recommendations with simplified input"""
    try:
        data = request.get_json()
        
        # Required fields for quick recommendations
        required_fields = ['session_id', 'style_words', 'occasion', 'budget_range']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Require catalogue_items to be provided from frontend
        if 'catalogue_items' not in data or not data['catalogue_items']:
            return jsonify({"error": "catalogue_items is required and cannot be empty"}), 400
        
        # Create a simplified user profile
        user_data = {
            'session_id': data['session_id'],
            'date': data.get('date', ''),
            'style_words': data['style_words'],
            'style_message': data.get('style_message', ''),
            'style_inspiration': data.get('style_inspiration', ''),
            'daily_needs': data.get('daily_needs', []),
            'occasion': data['occasion'],
            'avoid_styles': data.get('avoid_styles', []),
            'avoid_materials': data.get('avoid_materials', []),
            'material_sensitivities': data.get('material_sensitivities', []),
            'dominant_colors': data.get('dominant_colors', []),
            'accessory_preferences': data.get('accessory_preferences', []),
            'budget_range': data['budget_range'],
            'notes': data.get('notes', ''),
            'standard_sizes': data.get('standard_sizes', {}),
            'body_measurements': data.get('body_measurements', {}),
            'fit_preferences': data.get('fit_preferences', []),
            'skin_tone': data.get('skin_tone', ''),
            'hair': data.get('hair', ''),
            'eyes': data.get('eyes', ''),
            'location': data.get('location', ''),
            'weather_snapshot': data.get('weather_snapshot', ''),
            'weather_tags': data.get('weather_tags', [])
        }
        
        # Use the catalogue items provided from frontend (from catalogue.ts)
        catalogue_data = data['catalogue_items']
        
        # Create VellumStyleService instance
        service = VellumStyleService()
        
        # Create user profile and catalogue items
        user_profile = service.create_user_profile_from_dict(user_data)
        catalogue_items = service.create_catalogue_items_from_list(catalogue_data)
        
        # Execute the style workflow
        recommendations = service.execute_style_workflow(user_profile, catalogue_items)
        
        return jsonify({
            "success": True,
            "user_session_id": user_profile.session_id,
            "recommendations": recommendations,
            "catalogue_count": len(catalogue_items),
            "message": "Quick style recommendations generated successfully"
        })
        
    except ValueError as e:
        return jsonify({"error": f"Configuration error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to generate quick recommendations: {str(e)}"}), 500


@recommendations_bp.route('/validate-profile', methods=['POST'])
def validate_user_profile():
    """Validate user profile data before generating recommendations"""
    try:
        data = request.get_json()
        
        if 'user_profile' not in data:
            return jsonify({"error": "Missing user_profile data"}), 400
        
        user_data = data['user_profile']
        
        # Check required fields
        required_fields = ['session_id']
        missing_fields = []
        
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                missing_fields.append(field)
        
        # Check recommended fields
        recommended_fields = ['style_words', 'occasion', 'budget_range']
        missing_recommended = []
        
        for field in recommended_fields:
            if field not in user_data or not user_data[field]:
                missing_recommended.append(field)
        
        # Create user profile to test validity
        service = VellumStyleService()
        user_profile = service.create_user_profile_from_dict(user_data)
        
        validation_result = {
            "valid": len(missing_fields) == 0,
            "missing_required": missing_fields,
            "missing_recommended": missing_recommended,
            "profile_completeness": calculate_profile_completeness(user_data),
            "session_id": user_profile.session_id
        }
        
        return jsonify({
            "success": True,
            "validation": validation_result
        })
        
    except Exception as e:
        return jsonify({"error": f"Failed to validate profile: {str(e)}"}), 500


@recommendations_bp.route('/profile-template', methods=['GET'])
def get_profile_template():
    """Get a template for user profile data structure"""
    template = {
        "session_id": "user_12345",
        "date": "2024-01-15",
        "style_words": ["casual", "modern", "comfortable"],
        "style_message": "I prefer comfortable yet stylish clothing",
        "style_inspiration": "Minimalist with a touch of elegance",
        "daily_needs": ["work", "casual outings"],
        "occasion": "business casual",
        "avoid_styles": ["overly formal", "very tight fitting"],
        "avoid_materials": ["wool", "synthetic fabrics"],
        "material_sensitivities": ["latex"],
        "dominant_colors": ["navy", "white", "gray"],
        "accessory_preferences": ["minimal jewelry", "quality bags"],
        "budget_range": "$50-150 per item",
        "notes": "Prefer sustainable brands when possible",
        "standard_sizes": {
            "top": "M",
            "bottom": "32",
            "shoe": "9"
        },
        "body_measurements": {
            "chest": 92,
            "waist": 82,
            "hip": 95,
            "height": 175
        },
        "fit_preferences": ["relaxed fit", "not too tight"],
        "skin_tone": "warm undertone",
        "hair": "dark brown",
        "eyes": "brown",
        "location": "New York, NY",
        "weather_snapshot": "Cool autumn weather, 15°C",
        "weather_tags": ["layering weather", "light jacket needed"]
    }
    
    return jsonify({
        "success": True,
        "template": template,
        "description": "Complete user profile template with all available fields"
    })


@recommendations_bp.route('/catalogue-template', methods=['GET'])
def get_catalogue_template():
    """Get a template for catalogue item data structure"""
    template = [
        {
            "name": "Classic White Button-Down Shirt",
            "desc": "Timeless white cotton button-down shirt, perfect for professional and casual settings. Made from premium cotton with a comfortable fit.",
            "price": 79,
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        },
        {
            "name": "Slim Fit Dark Jeans",
            "desc": "Dark wash denim jeans with a modern slim fit, versatile for many occasions. Stretch denim for comfort.",
            "price": 89,
            "sizes_available": ["28", "30", "32", "34", "36", "38"]
        },
        {
            "name": "Black Blazer",
            "desc": "Elegant black blazer suitable for business meetings and evening events. Tailored fit with quality construction.",
            "price": 149,
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        }
    ]
    
    return jsonify({
        "success": True,
        "template": template,
        "description": "Sample catalogue items structure"
    })


@recommendations_bp.route('/style-preferences', methods=['GET'])
def get_style_preferences():
    """Get available style preference options"""
    preferences = {
        "style_words": [
            "casual", "formal", "business", "sporty", "elegant", "modern", 
            "classic", "trendy", "minimalist", "bohemian", "edgy", "romantic",
            "comfortable", "sophisticated", "relaxed", "polished"
        ],
        "occasions": [
            "work", "business meetings", "casual outings", "date night",
            "formal events", "travel", "weekend", "gym", "home", "parties",
            "networking events", "conferences"
        ],
        "budget_ranges": [
            "Under $25", "$25-50", "$50-100", "$100-200", "$200-500", "Over $500"
        ],
        "fit_preferences": [
            "tight fit", "slim fit", "regular fit", "relaxed fit", "oversized",
            "tailored", "loose", "form-fitting", "comfortable"
        ],
        "colors": [
            "black", "white", "navy", "gray", "beige", "brown", "red", "blue",
            "green", "pink", "purple", "yellow", "orange", "cream", "khaki"
        ],
        "materials_to_avoid": [
            "wool", "silk", "leather", "synthetic fabrics", "polyester",
            "nylon", "spandex", "cotton blends", "denim", "linen"
        ]
    }
    
    return jsonify({
        "success": True,
        "preferences": preferences,
        "description": "Available options for style preferences"
    })


def calculate_profile_completeness(user_data):
    """Calculate the completeness percentage of a user profile"""
    all_fields = [
        'session_id', 'style_words', 'style_message', 'occasion', 'budget_range',
        'dominant_colors', 'fit_preferences', 'skin_tone', 'location'
    ]
    
    completed_fields = 0
    for field in all_fields:
        if field in user_data and user_data[field]:
            completed_fields += 1
    
    return round((completed_fields / len(all_fields)) * 100, 1)
