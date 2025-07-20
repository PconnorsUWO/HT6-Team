#!/usr/bin/env python3
"""
Simple API test with local garment and person images
"""
import requests
import base64
import os
from PIL import Image
from io import BytesIO

# Segmind API configuration
SEGMIND_API_KEY = "SG_dfe39d0677343e9f"  # Replace with your actual key
SEGMIND_API_URL = "https://api.segmind.com/v1/idm-vton"

def image_file_to_base64(image_path):
    """Convert an image file to base64"""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    return base64.b64encode(image_data).decode('utf-8')

def main():
    print("🧪 Simple Segmind API Test")
    print("=" * 40)
    
    # Check if images exist
    person_path = "api_test_result.png"
    garment_path = "dress.jpg"
    
    if not os.path.exists(person_path):
        print(f"❌ Person image not found: {person_path}")
        return
    
    if not os.path.exists(garment_path):
        print(f"❌ Garment image not found: {garment_path}")
        return
    
    print(f"✅ Found person image: {person_path}")
    print(f"✅ Found garment image: {garment_path}")
    
    # Convert images to base64
    print("🔄 Converting images to base64...")
    person_b64 = image_file_to_base64(person_path)
    garment_b64 = image_file_to_base64(garment_path)
    
    print(f"✅ Person image base64 length: {len(person_b64)}")
    print(f"✅ Garment image base64 length: {len(garment_b64)}")
    
    # Prepare API request
    data = {
        "crop": False,
        "seed": 42,
        "steps": 30,
        "category": "dresses",
        "force_dc": False,
        "human_img": person_b64,
        "garm_img": garment_b64,
        "mask_only": False,
        "garment_des": "Blue casual shirt"
    }
    
    headers = {'x-api-key': SEGMIND_API_KEY}
    
    print("🔄 Making API request...")
    print(f"   API URL: {SEGMIND_API_URL}")
    print(f"   Category: {data['category']}")
    print(f"   Steps: {data['steps']}")
    print(f"   Seed: {data['seed']}")
    
    try:
        # Make the API request
        response = requests.post(SEGMIND_API_URL, json=data, headers=headers)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API call successful!")
            
            # Save the result image
            image_data = response.content
            output_path = "api_test_result-3.png"
            
            # Convert to PIL Image and save
            image = Image.open(BytesIO(image_data))
            image.save(output_path, 'PNG')
            
            print(f"💾 Result saved to: {output_path}")
            print(f"📐 Image size: {image.size}")
            print(f"🎨 Image mode: {image.mode}")
            
        else:
            print("❌ API call failed!")
            print(f"   Status code: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during API call: {e}")

if __name__ == "__main__":
    main() 