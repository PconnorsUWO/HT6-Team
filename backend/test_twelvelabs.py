#!/usr/bin/env python3
"""
Test script for TwelveLabs integration with the provided video URL
Uses the official TwelveLabs Python SDK
"""

import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:5000"

def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_video_download():
    """Test video download functionality"""
    print("Testing video download...")
    response = requests.get(f"{BASE_URL}/test-twelvelabs")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_twelvelabs_full():
    """Test full TwelveLabs integration"""
    print("Testing full TwelveLabs integration...")
    response = requests.post(f"{BASE_URL}/test-twelvelabs")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=== TwelveLabs Testing Script ===\n")
    
    # Test health endpoint
    test_health()
    
    # Test video download
    test_video_download()
    
    # Test full integration (requires API key)
    print("Note: Full TwelveLabs integration requires TWELVELABS_API_KEY environment variable")
    print("The integration now uses the official TwelveLabs Python SDK")
    test_twelvelabs_full() 