#!/usr/bin/env python3
"""
Test script for Segmind API implementation
"""
import os
import sys
import time

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_key_configuration():
    """Test if the Segmind API key is configured"""
    print("🧪 Testing API Key Configuration")
    print("=" * 40)
    
    api_key = os.getenv('SEGMIND_API_KEY')
    
    if not api_key or api_key == 'YOUR_API_KEY':
        print("❌ Segmind API key not configured")
        print("   Please set SEGMIND_API_KEY environment variable")
        return False
    else:
        print("✅ Segmind API key is configured")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
        return True

def test_image_conversion_functions():
    """Test image conversion utility functions"""
    print("\n🧪 Testing Image Conversion Functions")
    print("=" * 40)
    
    try:
        from services.tryon import image_file_to_base64, image_url_to_base64
        
        # Test file to base64 conversion
        if os.path.exists("person.jpg"):
            b64_data = image_file_to_base64("person.jpg")
            if b64_data and len(b64_data) > 100:
                print("✅ File to base64 conversion works")
            else:
                print("❌ File to base64 conversion failed")
                return False
        else:
            print("⚠️  person.jpg not found, skipping file conversion test")
        
        # Test URL to base64 conversion
        test_url = "https://segmind-sd-models.s3.amazonaws.com/display_images/idm-ip.png"
        try:
            b64_data = image_url_to_base64(test_url)
            if b64_data and len(b64_data) > 100:
                print("✅ URL to base64 conversion works")
            else:
                print("❌ URL to base64 conversion failed")
                return False
        except Exception as e:
            print(f"❌ URL to base64 conversion failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing image conversion: {e}")
        return False

def test_category_determination():
    """Test garment category determination"""
    print("\n🧪 Testing Category Determination")
    print("=" * 40)
    
    try:
        from services.tryon import determine_category
        from config import Config
        
        # Test with preset garments
        for garment in Config.PRESET_GARMENTS[:3]:  # Test first 3
            category = determine_category(garment['id'])
            print(f"✅ {garment['name']}: {category}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing category determination: {e}")
        return False

def test_garment_description():
    """Test garment description extraction"""
    print("\n🧪 Testing Garment Description")
    print("=" * 40)
    
    try:
        from services.tryon import get_garment_description
        from config import Config
        
        # Test with preset garments
        for garment in Config.PRESET_GARMENTS[:3]:  # Test first 3
            description = get_garment_description(garment['id'])
            print(f"✅ {garment['name']}: '{description}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing garment description: {e}")
        return False

def test_segmind_api_with_preset():
    """Test actual Segmind API call with preset garment"""
    print("\n🧪 Testing Segmind API with Preset Garment")
    print("=" * 40)
    
    # Check if API key is configured
    api_key = os.getenv('SEGMIND_API_KEY')
    if not api_key or api_key == 'YOUR_API_KEY':
        print("❌ Cannot test API without valid key")
        return False
    
    try:
        from services.tryon import perform_virtual_tryon
        from config import Config
        
        # Use local person image if available, otherwise use URL
        if os.path.exists("person.jpg"):
            person_path = "person.jpg"
            print(f"✅ Using local person image: {person_path}")
        else:
            person_path = "https://segmind-sd-models.s3.amazonaws.com/display_images/idm-ip.png"
            print(f"✅ Using remote person image: {person_path}")
        
        # Use first preset garment
        garment_id = Config.PRESET_GARMENTS[0]['id']
        print(f"✅ Using preset garment: {Config.PRESET_GARMENTS[0]['name']}")
        
        # Run the try-on
        start_time = time.time()
        result = perform_virtual_tryon(person_path, garment_id, "test_user_segmind")
        end_time = time.time()
        
        print(f"⏱️  API call time: {end_time - start_time:.2f} seconds")
        
        if result["success"]:
            print("✅ Segmind API call successful!")
            print(f"   Result ID: {result['result_id']}")
            print(f"   Result image: {result['result_image']}")
            print(f"   Category: {result.get('category', 'unknown')}")
            print(f"   API Provider: {result.get('api_provider', 'unknown')}")
            
            # Check if result file exists
            if os.path.exists(result['result_image']):
                print(f"✅ Result file created: {result['result_image']}")
                return True
            else:
                print(f"❌ Result file not found: {result['result_image']}")
                return False
        else:
            print("❌ Segmind API call failed!")
            print(f"   Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ Exception during API test: {e}")
        return False

def cleanup_test_files():
    """Clean up test result files"""
    print("\n🧹 Cleaning up test files")
    print("=" * 30)
    
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        for filename in os.listdir(uploads_dir):
            if filename.startswith("tryon_result_") and filename.endswith(".png"):
                filepath = os.path.join(uploads_dir, filename)
                try:
                    os.remove(filepath)
                    print(f"🗑️  Removed: {filepath}")
                except Exception as e:
                    print(f"❌ Failed to remove {filepath}: {e}")

def main():
    """Run all tests"""
    print("🧪 Testing Segmind API Implementation")
    print("=" * 60)
    
    # Track test results
    # test_results = []
    
    # # Test 1: API key configuration
    # test_results.append(("API Key Configuration", test_api_key_configuration()))
    
    # # Test 2: Image conversion functions
    # test_results.append(("Image Conversion Functions", test_image_conversion_functions()))
    
    # # Test 3: Category determination
    # test_results.append(("Category Determination", test_category_determination()))
    
    # # Test 4: Garment description
    # test_results.append(("Garment Description", test_garment_description()))
    
    # Test 5: Actual API call (only if API key is configured)
    if os.getenv('SEGMIND_API_KEY') and os.getenv('SEGMIND_API_KEY') != 'YOUR_API_KEY':
        test_results.append(("Segmind API Call", test_segmind_api_with_preset()))
    else:
        print("\n⚠️  Skipping API call test (no valid API key)")
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Segmind API implementation is working correctly.")
    elif passed >= 3:
        print("✅ Most tests passed! Core functionality is working.")
    else:
        print("⚠️  Many tests failed. Check implementation and API key.")
    
    # Cleanup
    cleanup_test_files()
    
    return passed >= 3

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 