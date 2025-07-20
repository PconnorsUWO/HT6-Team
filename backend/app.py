from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from datetime import datetime
from config import Config
from utils import ensure_upload_folder
from services.realtime_detection import RealtimeBodyDetector

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
    
    # Configure SocketIO
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
    
    # Configure upload folder
    ensure_upload_folder()
    app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Initialize real-time body detector
    detector = RealtimeBodyDetector()
    
    # Store detector instance for access from endpoints
    app.detector = detector
    
    # Register blueprints
    app.register_blueprint(garments_bp, url_prefix='/api')
    app.register_blueprint(videos_bp, url_prefix='/api')
    app.register_blueprint(tryon_bp, url_prefix='/api')
    app.register_blueprint(interview_bp, url_prefix='/api/interview')
    app.register_blueprint(recommendations_bp, url_prefix='/api/recommendations')
    
    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        print(f"Client connected: {request.sid}")
        emit('connected', {'status': 'connected', 'message': 'Connected to real-time body detection service'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('start_stream')
    def handle_start_stream(data):
        """Handle stream start request"""
        try:
            print(f"Starting stream for client: {request.sid}")
            detector.reset()  # Reset detection state
            emit('stream_started', {
                'status': 'success',
                'message': 'Real-time body detection stream started',
                'detection_mode': data.get('detection_mode', 'realtime'),
                'confidence_threshold': data.get('confidence_threshold', 0.7)
            })
        except Exception as e:
            print(f"Error starting stream: {str(e)}")
            emit('stream_error', {'error': f'Failed to start stream: {str(e)}'})
    
    @socketio.on('video_frame')
    def handle_video_frame(data):
        """Handle incoming video frame for real-time processing"""
        try:
            frame_data = data.get('frame')
            if not frame_data:
                emit('frame_error', {'error': 'No frame data provided'})
                return
            
            print(f"🔄 Processing frame from client {request.sid}")
            
            # Process frame with body detection
            result = detector.process_frame(frame_data)
            
            if 'error' in result:
                print(f"❌ Frame processing error: {result['error']}")
                emit('frame_error', result)
            else:
                print(f"✅ Frame processed successfully - Confidence: {result['confidence']:.3f}")
                # Send both annotated frame (for display) and clean frame (for try-on) back to client
                emit('annotated_frame', {
                    'annotated_frame': result['annotated_frame'],
                    'clean_frame': result['clean_frame'],  # Clean frame without annotations for try-on
                    'confidence': result['confidence'],
                    'frame_number': result['frame_number'],
                    'timestamp': result['timestamp'],
                    'detection_quality': result['detection_quality'],
                    'essential_landmarks': result['essential_landmarks']
                })
                
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            emit('frame_error', {'error': f'Frame processing error: {str(e)}'})
    
    @socketio.on('stop_stream')
    def handle_stop_stream():
        """Handle stream stop request"""
        try:
            print(f"Stopping stream for client: {request.sid}")
            emit('stream_stopped', {
                'status': 'success',
                'message': 'Real-time body detection stream stopped'
            })
        except Exception as e:
            print(f"Error stopping stream: {str(e)}")
            emit('stream_error', {'error': f'Failed to stop stream: {str(e)}'})
    
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
                "style_recommendations",
                "realtime_streaming"
            ],
            "endpoints": {
                "garments": "/api/preset-garments, /api/upload-garment",
                "video": "/api/record-video, /api/test-body-detection",
                "tryon": "/api/virtual-tryon",
                "interviews": "/api/interview/create-flow, /api/interview/create-interview",
                "recommendations": "/api/recommendations/style-recommendations"
            },
            "test_endpoints": {
                "test_video_download": "GET /api/test-body-detection",
                "test_body_detection_full": "POST /api/test-body-detection"
            },
            "websocket_endpoints": {
                "connect": "WebSocket connection to /",
                "start_stream": "Emit 'start_stream' event",
                "video_frame": "Emit 'video_frame' event with frame data",
                "stop_stream": "Emit 'stop_stream' event"
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
    
    # Get best frame endpoint
    @app.route('/api/best-frame', methods=['GET'])
    def get_best_frame():
        """Get the best frame captured during real-time detection (clean frame without annotations for try-on)"""
        try:
            best_frame, best_confidence = detector.get_best_frame()
            
            if best_frame is None:
                return jsonify({
                    "success": False,
                    "error": "No frames have been processed yet"
                }), 404
            
            # Convert frame to base64
            import cv2
            import base64
            _, buffer = cv2.imencode('.jpg', best_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_b64 = base64.b64encode(buffer).decode('utf-8')
            
            return jsonify({
                "success": True,
                "best_frame": f"data:image/jpeg;base64,{frame_b64}",
                "confidence": best_confidence,
                "message": "Best frame retrieved successfully"
            })
            
        except Exception as e:
            print(f"Error getting best frame: {str(e)}")
            return jsonify({
                "success": False,
                "error": f"Failed to get best frame: {str(e)}"
            }), 500
    
    return app, socketio

# Create the app instance
app, socketio = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 