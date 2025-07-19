from flask import Flask, request, jsonify
from flask_cors import CORS
from gradio_client import Client, file
import os
import tempfile
from werkzeug.utils import secure_filename
import uuid
import requests
import json
from datetime import datetime, timedelta
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from dotenv import load_dotenv
from twelvelabs import TwelveLabs
import ffmpeg

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS for development - more permissive
CORS(app, 
     origins=["*"])

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size


# API Keys
VELLUM_API_KEY = os.getenv('VELLUM_API_KEY')
TWELVELABS_API_KEY = os.getenv('TWELVELABS_API_KEY')

# Initialize clients
try:
    tryon_client = Client("yisol/IDM-VTON")
    print("✅ Try-on client initialized successfully")
except Exception as e:
    print(f"⚠️ Warning: Could not initialize try-on client: {e}")
    tryon_client = None

# Initialize TwelveLabs client
twelvelabs_client = TwelveLabs(api_key=TWELVELABS_API_KEY) if TWELVELABS_API_KEY else None

# MongoDB connection
MONGODB_URI = os.getenv('MONGODB_URI')
mongo_client = MongoClient(MONGODB_URI)
db = mongo_client.virtual_tryon

# Initialize GridFS for video storage
fs = GridFS(db)

def cleanup_expired_videos():
    """Remove expired videos from GridFS"""
    try:
        current_time = datetime.utcnow()
        expired_files = []
        
        # Find expired files
        for grid_out in fs.find({"metadata.expires_at": {"$lt": current_time}}):
            expired_files.append(grid_out._id)
        
        # Delete expired files
        for file_id in expired_files:
            try:
                fs.delete(file_id)
                print(f"Deleted expired video: {file_id}")
            except Exception as e:
                print(f"Error deleting expired video {file_id}: {e}")
        
        if expired_files:
            print(f"Cleaned up {len(expired_files)} expired videos")
            
    except Exception as e:
        print(f"Error in cleanup_expired_videos: {e}")

def convert_video_to_mp4(input_path: str, output_path: str = None) -> str:
    """
    Convert video to MP4 format using FFmpeg
    Ensures compatibility with TwelveLabs
    """
    try:
        if output_path is None:
            output_path = input_path.replace('.webm', '.mp4').replace('.mov', '.mp4')
            if not output_path.endswith('.mp4'):
                output_path = input_path + '.mp4'
        
        print(f"Converting video: {input_path} -> {output_path}")
        
        # Check if input file exists and has content
        if not os.path.exists(input_path):
            raise Exception(f"Input file does not exist: {input_path}")
        
        input_size = os.path.getsize(input_path)
        if input_size < 1024:  # Less than 1KB
            print(f"Warning: Input file is very small ({input_size} bytes)")
        
        # Try to get input video info
        try:
            probe = ffmpeg.probe(input_path)
            if 'format' in probe and 'duration' in probe['format']:
                duration = float(probe['format']['duration'])
                print(f"Input video duration: {duration} seconds")
                
                if duration < 4.0:
                    print(f"Warning: Input video is too short ({duration}s)")
            else:
                print("Warning: Could not determine input video duration")
        except Exception as e:
            print(f"Warning: Could not probe input video: {e}")
        
        # Convert to MP4 with H.264 codec (widely supported)
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path,
                                 vcodec='libx264',  # H.264 codec
                                 acodec='aac',      # AAC audio codec
                                 video_bitrate='2M', # 2 Mbps video bitrate
                                 audio_bitrate='128k', # 128 kbps audio bitrate
                                 preset='fast',     # Fast encoding preset
                                 movflags='+faststart', # Optimize for streaming
                                 f='mp4')           # Force MP4 format
            
            # Run the conversion
            ffmpeg.run(stream, overwrite_output=True, quiet=True)
            
        except Exception as e:
            print(f"FFmpeg conversion failed: {e}")
            # If conversion fails, try a simpler approach
            try:
                print("Trying simpler conversion...")
                stream = ffmpeg.input(input_path)
                stream = ffmpeg.output(stream, output_path, vcodec='libx264', preset='ultrafast')
                ffmpeg.run(stream, overwrite_output=True, quiet=True)
            except Exception as e2:
                print(f"Simple conversion also failed: {e2}")
                # If all conversion fails, return original path
                return input_path
        
        # Verify the output file
        if os.path.exists(output_path):
            output_size = os.path.getsize(output_path)
            print(f"Conversion successful: {output_path} ({output_size} bytes)")
            
            # Verify the converted video
            try:
                output_probe = ffmpeg.probe(output_path)
                if 'format' in output_probe and 'duration' in output_probe['format']:
                    output_duration = float(output_probe['format']['duration'])
                    print(f"Output video duration: {output_duration} seconds")
                    
                    if output_duration < 4.0:
                        print(f"Warning: Converted video is too short ({output_duration}s)")
                    
                    return output_path
                else:
                    print("Warning: Could not verify converted video duration")
                    return output_path
            except Exception as e:
                print(f"Warning: Could not verify converted video: {e}")
                return output_path
        else:
            print("Warning: Output file was not created, returning original")
            return input_path
            
    except Exception as e:
        print(f"Error in video conversion: {e}")
        # If conversion fails, return original path
        return input_path


# Test video URL for TwelveLabs testing
TEST_VIDEO_URL = "https://videos.pexels.com/video-files/5058382/5058382-uhd_2560_1440_25fps.mp4"

# Preset garments (to be expanded)
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

def get_full_video_metadata(file_path: str) -> dict:
    """Get complete video metadata using ffprobe"""
    import subprocess
    import json
    
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-print_format', 'json',
        '-show_format',
        '-show_streams',
        file_path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    if result.returncode != 0:
        raise RuntimeError(f"ffprobe error: {result.stderr}")

    return json.loads(result.stdout)


def get_video_info(video_path):
    """Get comprehensive video information for debugging"""
    try:
        metadata = get_full_video_metadata(video_path)
        
        # Extract video stream info
        video_stream = next((s for s in metadata['streams'] if s.get('codec_type') == 'video'), None)
        
        info = {
            'file_path': video_path,
            'format': metadata.get('format', {}),
            'video_stream': video_stream,
            'all_streams': metadata.get('streams', [])
        }
        
        if video_stream:
            info.update({
                'codec': video_stream.get('codec_name'),
                'resolution': f"{video_stream.get('width')}x{video_stream.get('height')}",
                'fps': video_stream.get('r_frame_rate'),
                'duration_from_stream': video_stream.get('duration'),
                'tags': video_stream.get('tags', {})
            })
        
        return info
        
    except Exception as e:
        return {'error': str(e)}

    
def allowed_file(filename):
    """Check if file extension is allowed"""
    # For video files, allow MP4 and WebM (fallback support)
    VIDEO_EXTENSIONS = {'mp4', 'webm'}
    # For image files, allow common formats
    IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    if '.' in filename:
        ext = filename.rsplit('.', 1)[1].lower()
        # Check if it's a video extension
        if ext in VIDEO_EXTENSIONS:
            return True
        # Check if it's an image extension
        if ext in IMAGE_EXTENSIONS:
            return True
    return False 

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
        "features": ["video_recording", "twelvelabs_integration", "mongodb_storage", "vellum_recommendations"],
        "test_endpoints": {
            "test_video_download": "GET /test-twelvelabs",
            "test_twelvelabs_full": "POST /test-twelvelabs"
        }
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify CORS is working"""
    return jsonify({
        "message": "Backend is running and CORS is working!",
        "timestamp": datetime.utcnow().isoformat()
    })

@app.route('/preset-garments', methods=['GET'])
def get_preset_garments():
    """Get available preset garments"""
    return jsonify({
        "success": True,
        "garments": PRESET_GARMENTS
    })



@app.route('/upload-garment', methods=['POST'])
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
        
        # Generate unique filename
        garment_id = str(uuid.uuid4())
        filename = secure_filename(f"garment_{garment_id}.jpg")
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
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
        
        db.garments.insert_one(garment_data)
        
        return jsonify({
            "success": True,
            "garment_id": garment_id,
            "message": "Garment uploaded successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/upload-video', methods=['POST'])
def upload_video():
    """Upload video to MongoDB GridFS and return public URL"""
    try:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video_file']
        if video_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type. Only MP4 and WebM formats are supported"}), 400
        
        # Generate unique filename
        file_extension = video_file.filename.rsplit('.', 1)[1].lower() if '.' in video_file.filename else 'webm'
        video_filename = f"video_{uuid.uuid4()}.{file_extension}"
        
        # Store video in GridFS
        file_id = fs.put(
            video_file.read(),
            filename=video_filename,
            content_type=f"video/{file_extension}",
            metadata={
                "upload_time": datetime.utcnow(),
                "expires_at": datetime.utcnow() + timedelta(hours=24),  # Auto-delete after 24 hours
                "original_filename": video_file.filename
            }
        )
        
        # Create public URL (you might want to set up a proper CDN or file serving endpoint)
        # For now, we'll create a download endpoint
        public_url = f"{request.host_url.rstrip('/')}/download-video/{str(file_id)}"
        
        return jsonify({
            "success": True,
            "video_id": str(file_id),
            "public_url": public_url,
            "filename": video_filename,
            "message": "Video uploaded successfully"
        })
        
    except Exception as e:
        print(f"Error in upload_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/download-video/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download video from GridFS by ID"""
    try:
        # Get file from GridFS
        grid_out = fs.get(ObjectId(video_id))
        
        # Check if file has expired
        if 'expires_at' in grid_out.metadata:
            expires_at = grid_out.metadata['expires_at']
            if datetime.utcnow() > expires_at:
                # Delete expired file
                fs.delete(ObjectId(video_id))
                return jsonify({"error": "Video has expired"}), 410
        
        # Return video file
        return grid_out.read(), 200, {
            'Content-Type': grid_out.content_type,
            'Content-Disposition': f'attachment; filename="{grid_out.filename}"'
        }
        
    except Exception as e:
        print(f"Error downloading video {video_id}: {str(e)}")
        return jsonify({"error": "Video not found"}), 404

@app.route('/cleanup-videos', methods=['POST'])
def cleanup_videos():
    """Manually trigger cleanup of expired videos"""
    try:
        cleanup_expired_videos()
        return jsonify({
            "success": True,
            "message": "Cleanup completed"
        })
    except Exception as e:
        return jsonify({
            "error": f"Cleanup failed: {str(e)}"
        }), 500

@app.route('/process-video', methods=['POST'])
def process_video():
    """Process video using MongoDB URL with TwelveLabs to find best frames"""
    try:
        data = request.get_json()
        if not data or 'video_url' not in data:
            return jsonify({"error": "No video URL provided"}), 400
        
        video_url = data['video_url']
        print(f"Processing video from URL: {video_url}")
        
        # Download video from MongoDB URL
        try:
            video_response = requests.get(video_url, stream=True)
            if video_response.status_code != 200:
                return jsonify({"error": "Failed to download video from MongoDB"}), 500
            
            # Get content info for debugging
            content_type = video_response.headers.get('content-type', 'unknown')
            content_length = video_response.headers.get('content-length', 'unknown')
            print(f"Downloaded video - Content-Type: {content_type}, Content-Length: {content_length}")
            
            # Save video temporarily with original extension
            original_filename = f"temp_video_{uuid.uuid4()}"
            if 'webm' in content_type.lower():
                original_filename += '.webm'
            elif 'mp4' in content_type.lower():
                original_filename += '.mp4'
            else:
                original_filename += '.mp4'  # default
            
            original_video_path = os.path.join(app.config['UPLOAD_FOLDER'], original_filename)
            
            total_bytes = 0
            with open(original_video_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive chunks
                        f.write(chunk)
                        total_bytes += len(chunk)
            
            print(f"Original video saved to {original_video_path}, total bytes: {total_bytes}")
            
            # Validate the downloaded video file
            if total_bytes < 1024:  # Less than 1KB is suspicious
                os.remove(original_video_path)
                return jsonify({"error": f"Downloaded video is too small ({total_bytes} bytes)"}), 400
            
            # Convert video to MP4 format for TwelveLabs compatibility
            print("Converting video to MP4 format...")
            video_path = convert_video_to_mp4(original_video_path)
            
            # Clean up original file if it's different from converted file
            if original_video_path != video_path and os.path.exists(original_video_path):
                os.remove(original_video_path)
                print(f"Cleaned up original file: {original_video_path}")
            
            # Try to get video info for debugging
            try:
                video_info = get_video_info(video_path)
                print(f"Converted video info: {video_info}")
            except Exception as e:
                print(f"Could not get video info: {e}")
                    
        except Exception as e:
            return jsonify({"error": f"Failed to download video: {str(e)}"}), 500

        # Upload to TwelveLabs using the SDK
        if not twelvelabs_client:
            print("TwelveLabs API key not configured, returning mock response")
            # Clean up video file
            os.remove(video_path)
            # Return a mock response for testing
            return jsonify({
                "success": True,
                "best_frame": {
                    "video_id": "mock_video_123",
                    "score": 0.95,
                    "start": 2.0,
                    "end": 2.5
                },
                "message": "Video processed successfully (mock response)"
            })
        
        # Get or create an index
        try:
            indexes = twelvelabs_client.index.list()
            if indexes and len(indexes) > 0:
                index_id = indexes[0].id
            else:
                # Create a new index if none exists
                index = twelvelabs_client.index.create(
                    name="virtual-tryon-index",
                    engine_id="marengo2.5",
                    model="gpt-4"
                )
                index_id = index.id
            print(f"Using index ID: {index_id}")
        except Exception as e:
            print(f"Error with index: {e}")
            index_id = "default"
        
        # Upload the video
        try:
            print(f"Uploading video to TwelveLabs: {video_path}")
            task = twelvelabs_client.task.create(
                index_id=index_id,
                file=video_path
            )
            
            print(f"Upload task created: {task.id}")
            
            # Wait for the task to complete
            import time
            while True:
                task_status = twelvelabs_client.task.retrieve(task.id)
                print(f"Task status: {task_status.status}")
                
                if task_status.status == "ready":
                    video_id = task_status.video_id
                    break
                elif task_status.status == "failed":
                    error_details = getattr(task_status, 'error', 'Unknown error')
                    print(f"Task failed: {error_details}")
                    return jsonify({"error": f"Video upload failed: {error_details}"}), 500
                
                time.sleep(2)
            
            print(f"Video uploaded successfully with ID: {video_id}")
            
        except Exception as e:
            print(f"Exception during TwelveLabs upload: {str(e)}")
            return jsonify({"error": f"Failed to upload video to TwelveLabs: {str(e)}"}), 500
        
        # Search for frames where person is standing still
        try:
            print("Searching for suitable frames...")
            search_results = twelvelabs_client.search.query(
                index_id=index_id,
                query_text="person standing still, full body visible, good lighting",
                options=["visual"]
            )
            print(f"Search completed, found {len(search_results.data) if hasattr(search_results, 'data') else 0} results")
            # write to a file
            with open('search_results.json', 'w') as f:
                json.dump(search_results, f)
                
        except Exception as e:
            return jsonify({"error": f"Failed to search video frames: {str(e)}"}), 500
        
        # Get the best frame and convert to dict
        best_frame = None
        if hasattr(search_results, 'data') and search_results.data:
            # Convert SearchData object to dictionary
            raw_frame = search_results.data[0]
            best_frame = {
                'video_id': getattr(raw_frame, 'video_id', None),
                'score': getattr(raw_frame, 'score', None),
                'start': getattr(raw_frame, 'start', None),
                'end': getattr(raw_frame, 'end', None),
                'thumbnail_url': getattr(raw_frame, 'thumbnail_url', None),
                'text': getattr(raw_frame, 'text', None)
            }
        
        # Clean up video file
        os.remove(video_path)
        
        if not best_frame:
            return jsonify({"error": "No suitable frames found in video"}), 400
        
        return jsonify({
            "success": True,
            "best_frame": best_frame,
            "message": "Video processed successfully"
        })
        
    except Exception as e:
        print(f"Error in process_video: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/test-twelvelabs', methods=['GET', 'POST'])
def test_twelvelabs():
    """Test TwelveLabs with the provided video URL"""
    try:
        # For GET requests, just test video download
        if request.method == 'GET':
            return test_video_download()
        
        # For POST requests, test full TwelveLabs integration
        if not TWELVELABS_API_KEY:
            return jsonify({"error": "TwelveLabs API key not configured"}), 500
        
        # Download the test video
        print(f"Downloading test video from: {TEST_VIDEO_URL}")
        video_response = requests.get(TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        with open(video_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Video saved to: {video_path}")
        
        # Upload to TwelveLabs using the SDK
        print("Uploading video to TwelveLabs...")
        
        # First, get or create an index
        try:
            indexes = twelvelabs_client.index.list()
            if indexes and len(indexes) > 0:
                index_id = indexes[0].id
            else:
                # Create a new index if none exists
                index = twelvelabs_client.index.create(
                    name="virtual-tryon-index",
                    engine_id="marengo2.5",
                    model="gpt-4"
                )
                index_id = index.id
            print(f"Using index ID: {index_id}")
        except Exception as e:
            print(f"Error with index: {e}")
            # Use a default index ID
            index_id = "default"
        
        # Upload the video
        try:
            task = twelvelabs_client.task.create(
                index_id=index_id,
                file=video_path
            )
            
            print(f"Upload task created: {task.id}")
            
            # Wait for the task to complete
            import time
            while True:
                task_status = twelvelabs_client.task.retrieve(task.id)
                print(f"Task status: {task_status.status}")
                
                if task_status.status == "ready":
                    video_id = task_status.video_id
                    break
                elif task_status.status == "failed":
                    return jsonify({
                        "error": "Video upload failed",
                        "details": task_status
                    }), 500
                
                time.sleep(2)
            
            print(f"Video uploaded successfully with ID: {video_id}")
            
        except Exception as e:
            return jsonify({
                "error": "Failed to upload video to TwelveLabs",
                "details": str(e)
            }), 500
        
        # Search for frames where person is standing still
        try:
            print("Searching for suitable frames...")
            search_results = twelvelabs_client.search.query(
                index_id=index_id,
                query="person standing still, full body visible, good lighting",
                video_ids=[video_id],
                search_options=["visual"]
            )
            
            print(f"Search completed, found {len(search_results.data) if hasattr(search_results, 'data') else 0} results")
            
        except Exception as e:
            return jsonify({
                "error": "Failed to search video frames",
                "details": str(e)
            }), 500
        
        # Get the best frame and convert to dict
        best_frame = None
        if hasattr(search_results, 'data') and search_results.data:
            # Convert SearchData object to dictionary
            raw_frame = search_results.data[0]
            best_frame = {
                'video_id': getattr(raw_frame, 'video_id', None),
                'score': getattr(raw_frame, 'score', None),
                'start': getattr(raw_frame, 'start', None),
                'end': getattr(raw_frame, 'end', None),
                'thumbnail_url': getattr(raw_frame, 'thumbnail_url', None),
                'text': getattr(raw_frame, 'text', None)
            }
        
        # Clean up video file
        os.remove(video_path)
        
        if not best_frame:
            return jsonify({
                "success": False,
                "message": "No suitable frames found in video"
            }), 400
        
        return jsonify({
            "success": True,
            "best_frame": best_frame,
            "video_id": video_id,
            "message": "Test video processed successfully with TwelveLabs"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def test_video_download():
    """Test downloading the video from the provided URL"""
    try:
        print(f"Testing video download from: {TEST_VIDEO_URL}")
        video_response = requests.get(TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Get video info
        content_length = video_response.headers.get('content-length')
        content_type = video_response.headers.get('content-type')
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], video_filename)
        
        with open(video_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Clean up
        os.remove(video_path)
        
        return jsonify({
            "success": True,
            "message": "Test video downloaded successfully",
            "video_url": TEST_VIDEO_URL,
            "content_type": content_type,
            "content_length": content_length,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route('/tryon', methods=['POST'])
def virtual_tryon():
    """Virtual try-on endpoint with MongoDB storage and Vellum recommendations"""
    try:
        # Get parameters
        person_image_path = request.form.get('person_image_path')
        garment_id = request.form.get('garment_id')  # Can be preset or custom
        user_id = request.form.get('user_id', 'anonymous')
        
        if not person_image_path or not garment_id:
            return jsonify({"error": "person_image_path and garment_id are required"}), 400
        
        # Get garment image path
        garment_path = None
        if garment_id in [g['id'] for g in PRESET_GARMENTS]:
            # Use preset garment
            garment = next(g for g in PRESET_GARMENTS if g['id'] == garment_id)
            garment_path = garment['image_url']
        else:
            # Get custom garment from MongoDB
            garment_doc = db.garments.find_one({"id": garment_id})
            if not garment_doc:
                return jsonify({"error": "Garment not found"}), 404
            garment_path = garment_doc['filepath']
        
        # Check if try-on client is available
        if not tryon_client:
            return jsonify({"error": "Try-on service is currently unavailable. Please try again later."}), 503
        
        # Run virtual try-on
        result = tryon_client.predict(
            {"background": file(person_image_path), "layers": [], "composite": None},
            file(garment_path),
            "Virtual try-on",
            True,  # is_checked
            False,  # is_checked_crop
            30,  # denoise_steps
            42,  # seed
            api_name="/tryon"
        )
        
        output_path, masked_output_path = result
        
        # Upload result to MongoDB and get public URL
        result_id = str(uuid.uuid4())
        result_data = {
            "id": result_id,
            "user_id": user_id,
            "garment_id": garment_id,
            "original_image": person_image_path,
            "result_image": output_path,
            "masked_image": masked_output_path,
            "created_at": datetime.utcnow(),
            "public_url": f"https://your-domain.com/results/{result_id}.jpg"  # You'll need to implement file hosting
        }
        
        db.tryon_results.insert_one(result_data)
        
        # Generate recommendations using Vellum
        recommendations = generate_recommendations(garment_id, user_id)
        
        return jsonify({
            "success": True,
            "result_id": result_id,
            "result_image": output_path,
            "public_url": result_data['public_url'],
            "recommendations": recommendations,
            "message": "Virtual try-on completed successfully"
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def generate_recommendations(garment_id, user_id):
    """Generate clothing recommendations using Vellum AI"""
    try:
        if not VELLUM_API_KEY:
            return []
        
        # Get garment info for context
        garment_info = None
        if garment_id in [g['id'] for g in PRESET_GARMENTS]:
            garment_info = next(g for g in PRESET_GARMENTS if g['id'] == garment_id)
        else:
            garment_doc = db.garments.find_one({"id": garment_id})
            if garment_doc:
                garment_info = garment_doc
        
        if not garment_info:
            return []
        
        # Call Vellum API for recommendations
        vellum_payload = {
            "input": {
                "garment_description": garment_info.get('description', ''),
                "user_preferences": "modern, comfortable, stylish",
                "occasion": "casual"
            },
            "prompt": """
            Based on the garment description and user preferences, suggest 3 complementary clothing items 
            that would go well with this piece. Consider style, color coordination, and occasion.
            Return as JSON array with items containing: name, description, style_category, color_suggestion
            """
        }
        
        headers = {
            'Authorization': f'Bearer {VELLUM_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            'https://api.vellum.ai/v1/generate',
            headers=headers,
            json=vellum_payload
        )
        
        if response.status_code == 200:
            recommendations = response.json().get('recommendations', [])
            return recommendations
        else:
            return []
            
    except Exception as e:
        print(f"Error generating recommendations: {str(e)}")
        return []

@app.route('/user-history/<user_id>', methods=['GET'])
def get_user_history(user_id):
    """Get user's try-on history"""
    try:
        results = list(db.tryon_results.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).limit(10))
        
        return jsonify({
            "success": True,
            "history": results
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)