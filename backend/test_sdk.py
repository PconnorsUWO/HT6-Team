#!/usr/bin/env python3
"""
Test script for TwelveLabs SDK integration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_sdk_import():
    """Test if the TwelveLabs SDK can be imported"""
    try:
        from twelvelabs import TwelveLabs
        print("✓ TwelveLabs SDK imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Failed to import TwelveLabs SDK: {e}")
        return False

def test_sdk_initialization():
    """Test if the SDK can be initialized with API key"""
    try:
        from twelvelabs import TwelveLabs
        
        api_key = os.getenv('TWELVELABS_API_KEY')
        if not api_key:
            print("⚠ TWELVELABS_API_KEY not found in environment variables")
            return False
        
        client = TwelveLabs(api_key=api_key)
        print("✓ TwelveLabs client initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to initialize TwelveLabs client: {e}")
        return False

def test_index_operations():
    """Test basic index operations"""
    try:
        from twelvelabs import TwelveLabs
        
        api_key = os.getenv('TWELVELABS_API_KEY')
        if not api_key:
            print("⚠ Skipping index operations test - no API key")
            return False
        
        client = TwelveLabs(api_key=api_key)
        
        # List indexes
        indexes = client.index.list()
        print(f"✓ Found {len(indexes)} existing indexes")
        
        return True
    except Exception as e:
        print(f"✗ Index operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("=== TwelveLabs SDK Integration Test ===\n")
    
    # Test SDK import
    import_success = test_sdk_import()
    
    if import_success:
        # Test SDK initialization
        init_success = test_sdk_initialization()
        
        if init_success:
            # Test index operations
            test_index_operations()
    
    print("\n=== Test Complete ===") 