from flask import Blueprint, request, jsonify
import os
import uuid
from werkzeug.utils import secure_filename
from services.tryon import perform_virtual_tryon
from services.recommendations import generate_recommendations
from models import get_user_history
from utils import ensure_upload_folder, allowed_file
from config import Config

tryon_bp = Blueprint('tryon', __name__)

@tryon_bp.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint with MongoDB storage and Vellum recommendations"""
    try:
        # Check for uploaded person image
        if 'person_image' not in request.files:
            return jsonify({"error": "person_image file is required"}), 400
        
        person_image_file = request.files['person_image']
        if person_image_file.filename == '':
            return jsonify({"error": "No person image file selected"}), 400
        
        if not allowed_file(person_image_file.filename):
            return jsonify({"error": "Invalid file type. Only PNG, JPG, JPEG, GIF are allowed"}), 400
        
        garment_id = request.form.get('garment_id')  # Can be preset or custom
        user_id = request.form.get('user_id', 'anonymous')
        
        if not garment_id:
            return jsonify({"error": "garment_id is required"}), 400
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Save the person image temporarily
        person_image_id = str(uuid.uuid4())
        filename = secure_filename(f"person_{person_image_id}.jpg")
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Save file
        person_image_file.save(filepath)
        
        try:
            # Perform virtual try-on
            result = perform_virtual_tryon(filepath, garment_id, user_id)
            
            if not result['success']:
                return jsonify({"error": result['error']}), 500
            
            # Generate recommendations using Vellum
            recommendations = generate_recommendations(garment_id, user_id)
            
            # Add recommendations to result
            result['recommendations'] = recommendations
            
            return jsonify(result)
            
        finally:
            # Clean up the temporary person image file
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Warning: Could not clean up temporary file {filepath}: {e}")
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@tryon_bp.route('/user-history/<user_id>', methods=['GET'])
def get_user_history_route(user_id):
    """Get user's try-on history"""
    try:
        history = get_user_history(user_id)
        
        return jsonify({
            "success": True,
            "history": history
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 