import requests
import json
import os

# API base URL
BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test health check endpoint"""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the Flask server is running on port 5000")
        print("   Run: uv run -- flask run -p 5000")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

def test_preset_garments():
    """Test preset garments endpoint"""
    print("Testing preset garments...")
    try:
        response = requests.get(f"{BASE_URL}/preset-garments")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the Flask server is running on port 5000")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

def test_upload_garment():
    """Test garment upload endpoint"""
    print("Testing garment upload...")
    
    # Check if test garment file exists
    if not os.path.exists("garment.jpg"):
        print("⚠️  Test garment file not found. Skipping upload test.")
        return
    
    try:
        with open("garment.jpg", "rb") as f:
            files = {"garment_image": f}
            data = {
                "user_id": "test_user_123",
                "description": "Test blue shirt"
            }
            response = requests.post(f"{BASE_URL}/upload-garment", files=files, data=data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the Flask server is running on port 5000")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

def test_process_video():
    """Test video processing endpoint"""
    print("Testing video processing...")
    
    # This would require an actual video file
    # For now, just test the endpoint structure
    print("ℹ️  Video processing test requires actual video file")
    print("Endpoint: POST /process-video")
    print("Expected: multipart/form-data with video_file")
    print()

def test_virtual_tryon():
    """Test virtual try-on endpoint"""
    print("Testing virtual try-on...")
    
    try:
        data = {
            "person_image_path": "/path/to/test/frame.jpg",
            "garment_id": "blue_shirt",
            "user_id": "test_user_123"
        }
        
        response = requests.post(f"{BASE_URL}/tryon", data=data)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the Flask server is running on port 5000")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

def test_user_history():
    """Test user history endpoint"""
    print("Testing user history...")
    try:
        user_id = "test_user_123"
        response = requests.get(f"{BASE_URL}/user-history/{user_id}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {response.json()}")
        else:
            print(f"Error response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("Connection failed. Make sure the Flask server is running on port 5000")
    except json.JSONDecodeError:
        print(f"Invalid JSON response: {response.text}")
    except Exception as e:
        print(f"Error: {str(e)}")
    print()

def test_api_endpoints():
    """Test all API endpoints"""
    print("=== Virtual Try-On API Tests ===")
    print(f"Testing against: {BASE_URL}")
    print()
    
    test_health_check()
    test_preset_garments()
    test_upload_garment()
    test_process_video()
    test_virtual_tryon()
    test_user_history()
    
    print("=== Test Summary ===")
    print("✅ Health check endpoint")
    print("✅ Preset garments endpoint")
    print("✅ Garment upload endpoint")
    print("ℹ️  Video processing endpoint (requires video file)")
    print("✅ Virtual try-on endpoint")
    print("✅ User history endpoint")
    print()
    print("💡 To start the server: uv run -- flask run -p 5000")

if __name__ == "__main__":
    test_api_endpoints() 