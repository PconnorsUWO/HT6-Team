"""
Example usage of the Vellum Style Service module

This file demonstrates how to use the VellumStyleService to get style recommendations
"""

import os
from dotenv import load_dotenv
from vellum_style_service import VellumStyleService, get_style_recommendations

# Load environment variables from .env file
load_dotenv()

# Example user data (based on Ted's profile from your example)
ted_profile_data = {
    "session_id": "sty_ted_001",
    "date": "2025-07-19",
    "style_words": ["clean", "versatile", "modern"],
    "style_message": "I want to look put-together and approachable without seeming overdressed.",
    "style_inspiration": "Neil Patrick Harris casual suits; Scandinavian minimalism",
    "daily_needs": ["hybrid office", "casual remote days", "evening meetup events", "weekend brunches"],
    "occasion": "networking mixer",
    "avoid_styles": ["neon", "extra baggy fits", "loud logos", "heavy distressed denim"],
    "avoid_materials": ["polyester"],
    "material_sensitivities": ["wool"],
    "dominant_colors": ["navy", "charcoal", "white", "olive"],
    "accessory_preferences": ["minimal watch", "leather belt"],
    "budget_range": "$50–$180",
    "notes": "Commutes by bike; prefers breathable stretch fabrics.",
    "standard_sizes": {
        "top": "M",
        "bottom": "32×32",
        "shoe": "US 11"
    },
    "body_measurements": {
        "chest": 102,
        "waist": 84,
        "hip": 100,
        "inseam": 81
    },
    "fit_preferences": ["tailored", "regular"],
    "skin_tone": "light / cool",
    "hair": "light brown, short textured",
    "eyes": "blue",
    "location": "Toronto, CA",
    "weather_snapshot": "26 °C, partly sunny, humidity 55%, wind 12 kph",
    "weather_tags": ["warm", "dry", "breezy"]
}

# Example catalogue data (subset of your full catalogue)
example_catalogue = [
    {
        "desc": "Lightweight premium cotton crewneck in a cool slate tone; breathable for warm days and easy layering.",
        "name": "Slate Supima Crew Tee",
        "price": 32,
        "sizes_available": ["XS", "S", "M", "L", "XL"]
    },
    {
        "desc": "Moisture-wicking stretch chino with a clean tapered leg—desk to dinner versatility.",
        "name": "Tapered Tech Chino",
        "price": 78,
        "sizes_available": ["30x30", "30x32", "32x30", "32x32", "34x32"]
    },
    {
        "desc": "Soft knit blazer with minimal shoulder padding for a tailored yet relaxed silhouette.",
        "name": "Unstructured Knit Blazer",
        "price": 148,
        "sizes_available": ["S", "M", "L", "XL"]
    },
    {
        "desc": "Low-profile full-grain leather sneaker with clean lines for smart-casual pairing.",
        "name": "Minimal Leather Sneaker (White)",
        "price": 120,
        "sizes_available": ["US 8", "US 9", "US 10", "US 11", "US 12"]
    }
]


def example_using_service_class():
    """Example using the VellumStyleService class directly"""
    print("=== Using VellumStyleService class ===")
    
    try:
        # Initialize the service
        service = VellumStyleService()
        
        # Create user profile from dictionary
        user_profile = service.create_user_profile_from_dict(ted_profile_data)
        
        # Create catalogue items from list
        catalogue_items = service.create_catalogue_items_from_list(example_catalogue)
        
        # Execute the workflow
        result = service.execute_style_workflow(user_profile, catalogue_items)
        
        print("Style recommendations received:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")


def example_using_convenience_function():
    """Example using the convenience function"""
    print("\n=== Using convenience function ===")
    
    try:
        # Use the convenience function
        result = get_style_recommendations(ted_profile_data, example_catalogue)
        
        print("Style recommendations received:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_custom_api_key():
    """Example with API key from environment variables"""
    print("\n=== Using API key from .env file ===")
    
    try:
        # Get API key from environment variables
        api_key = os.getenv('VELLUM_API_KEY')
        
        if not api_key:
            print("Error: VELLUM_API_KEY not found in environment variables")
            print("Make sure you have a .env file with VELLUM_API_KEY defined")
            return
        
        # Use the API key from environment
        result = get_style_recommendations(
            ted_profile_data, 
            example_catalogue, 
            api_key=api_key
        )
        
        print("Style recommendations received:")
        print(result)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Vellum Style Service Examples")
    print("=" * 40)
    
    # Run examples
    example_using_service_class()
    example_using_convenience_function()
    example_with_custom_api_key()  # Now using API key from .env file
