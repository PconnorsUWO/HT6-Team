from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime
from config import Config
from utils import ensure_upload_folder

# Import blueprints
from routes.garments import garments_bp
from routes.videos import videos_bp
from routes.tryon import tryon_bp
from routes.interview import interview_bp
from routes.recommendations import recommendations_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS for development - more permissive
    CORS(app, origins=["*"])
    
    # Configure upload folder
    ensure_upload_folder()
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Register blueprints
    app.register_blueprint(garments_bp, url_prefix='/api')
    app.register_blueprint(videos_bp, url_prefix='/api')
    app.register_blueprint(tryon_bp, url_prefix='/api')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    
    # Health check endpoint
    @app.route('/health', methods=['GET', 'OPTIONS'])
    def health_check():
        """Health check endpoint"""
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify({})
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
            return response
        
        return jsonify({
            "status": "healthy", 
            "message": "Virtual Try-On API is running",
            "features": [
                "video_recording", 
                "opencv_body_detection", 
                "mongodb_storage", 
                "vellum_recommendations",
                "ribbon_interviews",
                "style_recommendations"
            ],
            "endpoints": {
                "garments": "/api/preset-garments, /api/upload-garment",
                "video": "/api/record-video, /api/test-body-detection",
                "tryon": "/api/virtual-tryon",
                "interviews": "/api/interview/create-flow, /api/interview/create-interview",
                "recommendations": "/api/recommendations/style-recommendations"
            }
        })
    
    # Simple test endpoint
    @app.route('/test', methods=['GET'])
    def test_endpoint():
        """Simple test endpoint to verify CORS is working"""
        return jsonify({
            "message": "Backend is running and CORS is working!",
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 