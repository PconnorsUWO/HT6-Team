from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from config import Config
from models import save_garment_to_db
from utils import allowed_file, ensure_upload_folder

garments_bp = Blueprint('garments', __name__)

@garments_bp.route('/preset-garments', methods=['GET'])
def get_preset_garments():
    """Get available preset garments"""
    return jsonify({
        "success": True,
        "garments": Config.PRESET_GARMENTS
    })

@garments_bp.route('/upload-garment', methods=['POST'])
def upload_garment():
    """Upload a custom garment to MongoDB"""
    try:
        if 'garment_image' not in request.files:
            return jsonify({"error": "No garment image provided"}), 400
        
        garment_file = request.files['garment_image']
        if garment_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(garment_file.filename):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Generate unique filename
        garment_id = str(uuid.uuid4())
        filename = secure_filename(f"garment_{garment_id}.jpg")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file
        garment_file.save(filepath)
        
        # Store in MongoDB
        garment_data = {
            "id": garment_id,
            "filename": filename,
            "filepath": filepath,
            "uploaded_at": datetime.utcnow(),
            "user_id": request.form.get('user_id', 'anonymous'),  # Will be replaced with actual auth
            "description": request.form.get('description', 'Custom garment')
        }
        
        save_garment_to_db(garment_data)
        
        return jsonify({
            "success": True,
            "garment_id": garment_id,
            "message": "Garment uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 