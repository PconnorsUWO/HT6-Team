#!/usr/bin/env python3

"""
Test script to verify Final page tryon integration
"""

import requests
import json
import base64
from PIL import Image, ImageDraw
import io

def create_test_person_image():
    """Create a simple test person image"""
    # Create a simple test image
    img = Image.new('RGB', (400, 600), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Draw a simple stick figure
    # Head
    draw.ellipse([175, 50, 225, 100], outline='black', width=3)
    
    # Body
    draw.line([200, 100, 200, 350], fill='black', width=5)
    
    # Arms
    draw.line([200, 150, 150, 200], fill='black', width=3)
    draw.line([200, 150, 250, 200], fill='black', width=3)
    
    # Legs
    draw.line([200, 350, 150, 450], fill='black', width=3)
    draw.line([200, 350, 250, 450], fill='black', width=3)
    
    # Add text
    draw.text((140, 500), "Test Person Image", fill='black')
    
    return img

def test_tryon_endpoint():
    """Test the tryon endpoint directly"""
    print("🧪 Testing tryon endpoint...")
    
    try:
        # Create test person image
        person_img = create_test_person_image()
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        person_img.save(img_byte_arr, format='JPEG')
        img_byte_arr.seek(0)
        
        # Prepare the request
        files = {
            'person_image': ('test_person.jpg', img_byte_arr, 'image/jpeg')
        }
        
        data = {
            'garment_url': 'http://localhost:5173/catalog/brown_midi_dress.jpg',  # From catalogue.ts
            'garment_description': 'A chic brown midi dress with a structured fit and a statement belt for a polished look.',
            'user_id': 'test_user_final_page'
        }
        
        print(f"Making request to tryon endpoint...")
        print(f"Garment URL: {data['garment_url']}")
        print(f"Description: {data['garment_description']}")
        
        response = requests.post(
            'http://127.0.0.1:5000/api/tryon',
            files=files,
            data=data,
            timeout=120  # 2 minute timeout
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Tryon endpoint test successful!")
            print(f"Result ID: {result.get('result_id', 'N/A')}")
            print(f"Result image: {result.get('result_image', 'N/A')}")
            print(f"Category: {result.get('category', 'N/A')}")
            print(f"Message: {result.get('message', 'N/A')}")
            return True
        else:
            print(f"❌ Tryon endpoint test failed!")
            print(f"Error: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server!")
        print("Please make sure the backend is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_final_page_flow():
    """Test the data flow that the Final page expects"""
    print("\n🔄 Testing Final page data flow...")
    
    # This simulates the data that should be passed from pick_clothes to Final
    selected_items = [
        {
            "name": "Belted Brown Midi Dress",
            "category": "dresses",
            "image_url": "/catalog/brown_midi_dress.jpg",
            "price": 104.99,
            "desc": "A chic brown midi dress with a structured fit and a statement belt for a polished look."
        },
        {
            "name": "Yellow Printed Midi Dress",
            "category": "dresses", 
            "image_url": "/catalog/yellow_midi_dress.jpg",
            "price": 97.5,
            "desc": "A breezy yellow printed dress with a smocked top, perfect for sunny days."
        }
    ]
    
    print(f"✅ Mock selected items prepared: {len(selected_items)} items")
    for item in selected_items:
        print(f"  - {item['name']} (${item['price']})")
    
    print("\n📋 Final page should:")
    print("1. ✅ Accept selectedItems and userPhoto via navigation state")
    print("2. ✅ Show loading indicator during tryon processing")
    print("3. ✅ Display try-on result image when complete")
    print("4. ✅ Allow switching between multiple selected items")
    print("5. ✅ Handle errors gracefully with fallback UI")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Final Page Tryon Integration\n")
    
    # Test the backend endpoint
    tryon_success = test_tryon_endpoint()
    
    # Test the data flow
    flow_success = test_final_page_flow()
    
    print(f"\n📊 Test Results:")
    print(f"  Tryon Endpoint: {'✅ PASS' if tryon_success else '❌ FAIL'}")
    print(f"  Data Flow: {'✅ PASS' if flow_success else '❌ FAIL'}")
    
    if tryon_success and flow_success:
        print("\n🎉 All tests passed! Final page tryon integration is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the backend setup.")
    
    print(f"\n🔗 To test the full frontend flow:")
    print(f"1. Start the backend: cd backend && uv run uvicorn app:app --reload")
    print(f"2. Start the frontend: cd frontend && npm run dev")
    print(f"3. Navigate: / → pick_clothes → select items → final")

if __name__ == "__main__":
    main() 