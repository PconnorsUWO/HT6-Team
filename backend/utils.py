import os
from werkzeug.utils import secure_filename
from config import Config

def allowed_file(filename):
    """Check if file extension is allowed"""
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        # Check if it's a video extension
        if ext in Config.VIDEO_EXTENSIONS:
            return True
        # Check if it's an image extension
        if ext in Config.IMAGE_EXTENSIONS:
            return True
    return False

def get_file_extension(filename):
    """Get file extension from filename"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return None

def ensure_upload_folder():
    """Ensure upload folder exists"""
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER) 