#!/usr/bin/env python3
"""
Test script to verify the try-on endpoint is working correctly
"""
import requests
import os
from PIL import Image
import io

def create_test_image():
    """Create a simple test image"""
    # Create a 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_tryon_endpoint():
    """Test the try-on endpoint"""
    url = "http://127.0.0.1:5000/api/tryon"
    
    # Create test image
    test_image = create_test_image()
    
    # Prepare form data
    files = {
        'person_image': ('test_person.jpg', test_image, 'image/jpeg')
    }
    
    data = {
        'garment_id': 'blue_shirt',  # Use a preset garment
        'user_id': 'test_user_123'
    }
    
    print("Testing try-on endpoint...")
    print(f"URL: {url}")
    print(f"Files: {list(files.keys())}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, files=files, data=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Success!")
            print(f"Response: {result}")
        else:
            print("❌ Error!")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_tryon_endpoint() 