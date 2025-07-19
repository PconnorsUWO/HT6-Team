from flask import Blueprint, request, jsonify
from services.tryon import perform_virtual_tryon
from services.recommendations import generate_recommendations
from models import get_user_history

tryon_bp = Blueprint('tryon', __name__)

@tryon_bp.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint with MongoDB storage and Vellum recommendations"""
    try:
        # Get parameters
        person_image_path = request.form.get('person_image_path')
        garment_id = request.form.get('garment_id')  # Can be preset or custom
        user_id = request.form.get('user_id', 'anonymous')
        
        if not person_image_path or not garment_id:
            return jsonify({"error": "person_image_path and garment_id are required"}), 400
        
        # Perform virtual try-on
        result = perform_virtual_tryon(person_image_path, garment_id, user_id)
        
        if not result['success']:
            return jsonify({"error": result['error']}), 500
        
        # Generate recommendations using Vellum
        recommendations = generate_recommendations(garment_id, user_id)
        
        # Add recommendations to result
        result['recommendations'] = recommendations
        
        return jsonify(result)
        
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