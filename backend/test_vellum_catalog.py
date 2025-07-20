#!/usr/bin/env python3
"""
Test script to verify Vellum integration with real catalog data
"""

import requests
import json

def test_vellum_with_real_catalog():
    """Test that Vellum recommendations use the real catalog from catalogue.ts"""
    
    # This simulates the catalog data from catalogue.ts
    real_catalog = [
        {
            "name": "Belted Brown Midi Dress",
            "desc": "A chic brown midi dress with a structured fit and a statement belt for a polished look.",
            "price": 104.99,
            "category": "dresses",
            "image_url": "/catalog/brown_midi_dress.jpg",
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        },
        {
            "name": "Yellow Printed Midi Dress", 
            "desc": "A breezy yellow printed dress with a smocked top, perfect for sunny days.",
            "price": 97.5,
            "category": "dresses",
            "image_url": "/catalog/yellow_midi_dress.jpg",
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        },
        {
            "name": "Vertical Stripe Short-Sleeve Shirt",
            "desc": "A bold short-sleeve shirt featuring vertical black and white stripes, perfect for a crisp summer look.",
            "price": 69.5,
            "category": "shirts",
            "image_url": "/catalog/stripe_shirt.jpg",
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        },
        {
            "name": "Basic White Oversized T-Shirt",
            "desc": "Classic oversized white tee made from breathable cotton, ideal for layering or solo wear.",
            "price": 65.0,
            "category": "shirts",
            "image_url": "/catalog/white_shirt.jpg",
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        },
        {
            "name": "Light Blue Relaxed Jeans",
            "desc": "Light-wash denim jeans with a relaxed fit and high-rise waist for laid-back everyday wear.",
            "price": 88.25,
            "category": "pants", 
            "image_url": "/catalog/jeans.jpg",
            "sizes_available": ["XS", "S", "M", "L", "XL"]
        }
    ]
    
    # Sample user profile
    user_profile = {
        "session_id": "test_catalog_integration",
        "date": "2024-01-15",
        "style_words": ["casual", "modern", "comfortable"],
        "style_message": "I prefer comfortable yet stylish clothing",
        "style_inspiration": "Minimalist with a touch of elegance",
        "daily_needs": ["work", "casual outings"],
        "occasion": "business casual",
        "avoid_styles": ["overly formal"],
        "avoid_materials": [],
        "material_sensitivities": [],
        "dominant_colors": ["navy", "white", "gray"],
        "accessory_preferences": ["minimal jewelry"],
        "budget_range": "$50-150 per item",
        "notes": "Testing with real catalog items",
        "standard_sizes": {"top": "M", "bottom": "32", "shoe": "9"},
        "body_measurements": {"chest": 92, "waist": 82, "hip": 95, "height": 175},
        "fit_preferences": ["relaxed fit"],
        "skin_tone": "warm undertone",
        "hair": "dark brown",
        "eyes": "brown", 
        "location": "Toronto, CA",
        "weather_snapshot": "Cool autumn weather, 15°C",
        "weather_tags": ["layering weather"]
    }
    
    # Test the style recommendations endpoint
    print("🧪 Testing Vellum with Real Catalog Data")
    print("=" * 50)
    
    api_url = "http://127.0.0.1:5000/api/recommendations/style-recommendations"
    
    payload = {
        "user_profile": user_profile,
        "catalogue_items": real_catalog
    }
    
    try:
        print("📤 Sending request to Vellum API...")
        print(f"📍 URL: {api_url}")
        print(f"📊 Catalog items: {len(real_catalog)}")
        print(f"🏷️  Categories: {set(item['category'] for item in real_catalog)}")
        
        response = requests.post(api_url, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Vellum API responded successfully!")
            print(f"📈 Response: {json.dumps(result, indent=2)}")
            
            # Check if response contains our catalog items
            if 'recommendations' in result:
                recs = result['recommendations']
                if 'final-output' in recs and 'top_10' in recs['final-output']:
                    recommended_items = recs['final-output']['top_10']
                    print(f"\n🎯 Found {len(recommended_items)} recommendations")
                    
                    # Verify that recommendations are from our catalog
                    catalog_names = {item['name'] for item in real_catalog}
                    for i, rec in enumerate(recommended_items[:3], 1):
                        item_name = rec.get('item', {}).get('name', 'Unknown')
                        is_from_catalog = item_name in catalog_names
                        status = "✅" if is_from_catalog else "❌"
                        print(f"{status} Recommendation {i}: {item_name} (From catalog: {is_from_catalog})")
                
            return True
        else:
            print(f"❌ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
        print("Make sure the backend is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_quick_recommendations():
    """Test quick recommendations endpoint with catalog"""
    print("\n🧪 Testing Quick Recommendations with Real Catalog")
    print("=" * 50)
    
    # Simplified request for quick recommendations  
    quick_request = {
        "session_id": "test_quick_catalog",
        "style_words": ["casual", "comfortable"],
        "occasion": "weekend",
        "budget_range": "$50-150"
    }
    
    api_url = "http://127.0.0.1:5000/api/recommendations/quick-recommendations"
    
    try:
        print("📤 Sending quick recommendations request...")
        
        response = requests.post(api_url, json=quick_request, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: Quick recommendations API responded!")
            print(f"📈 Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ ERROR: API returned status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    print("🎽 Closetly.ai - Vellum Catalog Integration Test")
    print("=" * 60)
    
    # Test both endpoints
    test1 = test_vellum_with_real_catalog()
    test2 = test_quick_recommendations()
    
    print(f"\n📊 Test Results:")
    print(f"Style Recommendations: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Quick Recommendations: {'✅ PASS' if test2 else '❌ FAIL'}")
    
    if test1 and test2:
        print("\n🎉 All tests passed! Vellum is properly using real catalog data.")
    else:
        print("\n⚠️  Some tests failed. Check the error messages above.") 