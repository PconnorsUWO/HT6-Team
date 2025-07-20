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
    
    # File extensions
    VIDEO_EXTENSIONS = {'mp4', 'webm'}
    IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'} 