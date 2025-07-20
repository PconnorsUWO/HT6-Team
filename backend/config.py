import os
from dotenv import load_dotenv

# Load environment variables from root .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    """Application configuration"""
    
    # Flask settings
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Keys
    VELLUM_API_KEY = os.getenv('VELLUM_API_KEY')
    RIBBON_API_KEY = os.getenv('RIBBON_API_KEY')
    
    # MongoDB settings
    MONGODB_URI = os.getenv('MONGODB_URI')
    
    # Test video URL for body detection testing
    TEST_VIDEO_URL = "https://videos.pexels.com/video-files/5058382/5058382-uhd_2560_1440_25fps.mp4"
    
    # Preset garments
    PRESET_GARMENTS = [
        {
            "id": "blue_shirt",
            "name": "Blue Casual Shirt",
            "description": "A comfortable blue casual shirt perfect for everyday wear",
            "image_url": "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=300&h=400&fit=crop"
        },
        {
            "id": "red_dress",
            "name": "Red Evening Dress",
            "description": "An elegant red evening dress for special occasions",
            "image_url": "https://images.unsplash.com/photo-1515372039744-b8f02a3ae446?w=300&h=400&fit=crop"
        },
        {
            "id": "white_blouse",
            "name": "White Blouse",
            "description": "A classic white blouse for professional settings",
            "image_url": "https://images.unsplash.com/photo-1564257631407-3deb5d3d3b3b?w=300&h=400&fit=crop"
        },
        {
            "id": "black_jacket",
            "name": "Black Leather Jacket",
            "description": "A stylish black leather jacket for a cool look",
            "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=300&h=400&fit=crop"
        },
        {
            "id": "denim_jeans",
            "name": "Blue Denim Jeans",
            "description": "Classic blue denim jeans for casual comfort",
            "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=300&h=400&fit=crop"
        },
        {
            "id": "summer_dress",
            "name": "Floral Summer Dress",
            "description": "A beautiful floral summer dress for warm days",
            "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=300&h=400&fit=crop"
        }
    ]
    
    # File extensions
    VIDEO_EXTENSIONS = {'mp4', 'webm'}
    IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 