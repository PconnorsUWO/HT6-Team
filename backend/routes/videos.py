from flask import Blueprint, request, jsonify
import os
import uuid
import requests
from datetime import datetime, timedelta
from bson import ObjectId
from config import Config
from models import (
    save_video_to_gridfs, 
    get_video_from_gridfs, 
    delete_video_from_gridfs,
    cleanup_expired_videos
)
from services.body_detection import detect_body_pose_in_video, get_video_info
from utils import allowed_file, ensure_upload_folder, get_file_extension

videos_bp = Blueprint('videos', __name__)

@videos_bp.route('/upload-video', methods=['POST'])
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
        file_extension = get_file_extension(video_file.filename) or 'webm'
        video_filename = f"video_{uuid.uuid4()}.{file_extension}"
        
        # Store video in GridFS
        file_id = save_video_to_gridfs(
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

@videos_bp.route('/download-video/<video_id>', methods=['GET'])
def download_video(video_id):
    """Download video from GridFS by ID"""
    try:
        # Get file from GridFS
        grid_out = get_video_from_gridfs(video_id)
        
        # Check if file has expired
        if 'expires_at' in grid_out.metadata:
            expires_at = grid_out.metadata['expires_at']
            if datetime.utcnow() > expires_at:
                # Delete expired file
                delete_video_from_gridfs(video_id)
                return jsonify({"error": "Video has expired"}), 410
        
        # Return video file
        return grid_out.read(), 200, {
            'Content-Type': grid_out.content_type,
            'Content-Disposition': f'attachment; filename="{grid_out.filename}"'
        }
        
    except Exception as e:
        print(f"Error downloading video {video_id}: {str(e)}")
        return jsonify({"error": "Video not found"}), 404

@videos_bp.route('/cleanup-videos', methods=['POST'])
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

@videos_bp.route('/detect-body', methods=['POST'])
def detect_body():
    """Detect body pose in uploaded video using OpenCV and MediaPipe"""
    try:
        if 'video_file' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video_file']
        if video_file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(video_file.filename):
            return jsonify({"error": "Invalid file type. Only MP4 and WebM formats are supported"}), 400
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Save video temporarily
        video_filename = f"body_detection_{uuid.uuid4()}"
        if video_file.filename.lower().endswith('.mp4'):
            video_filename += '.mp4'
        elif video_file.filename.lower().endswith('.webm'):
            video_filename += '.webm'
        else:
            video_filename += '.mp4'  # default
        
        video_path = os.path.join(Config.UPLOAD_FOLDER, video_filename)
        video_file.save(video_path)
        
        print(f"Video saved for body detection: {video_path}")
        
        # Get video info for debugging
        try:
            video_info = get_video_info(video_path)
            print(f"Video info: {video_info}")
        except Exception as e:
            print(f"Could not get video info: {e}")
        
        # Detect body pose in video
        result = detect_body_pose_in_video(video_path)
        
        # Clean up video file
        try:
            os.remove(video_path)
            print(f"Cleaned up video file: {video_path}")
        except Exception as e:
            print(f"Warning: Could not clean up video file: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error in detect_body: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@videos_bp.route('/test-body-detection', methods=['GET', 'POST'])
def test_body_detection():
    """Test body detection with the provided video URL"""
    try:
        # For GET requests, just test video download
        if request.method == 'GET':
            return test_video_download()
        
        # For POST requests, test full body detection
        # Download the test video
        print(f"Downloading test video from: {Config.TEST_VIDEO_URL}")
        video_response = requests.get(Config.TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(Config.UPLOAD_FOLDER, video_filename)
        
        with open(video_path, 'wb') as f:
            for chunk in video_response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Video saved to: {video_path}")
        
        # Test body detection
        print("Testing body detection...")
        result = detect_body_pose_in_video(video_path)
        
        # Clean up video file
        try:
            os.remove(video_path)
        except Exception as e:
            print(f"Warning: Could not clean up test video: {e}")
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

def test_video_download():
    """Test downloading the video from the provided URL"""
    try:
        print(f"Testing video download from: {Config.TEST_VIDEO_URL}")
        video_response = requests.get(Config.TEST_VIDEO_URL, stream=True)
        
        if video_response.status_code != 200:
            return jsonify({"error": "Failed to download test video"}), 500
        
        # Get video info
        content_length = video_response.headers.get('content-length')
        content_type = video_response.headers.get('content-type')
        
        # Ensure upload folder exists
        ensure_upload_folder()
        
        # Save video temporarily
        video_filename = f"test_video_{uuid.uuid4()}.mp4"
        video_path = os.path.join(Config.UPLOAD_FOLDER, video_filename)
        
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
            "video_url": Config.TEST_VIDEO_URL,
            "content_type": content_type,
            "content_length": content_length,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size / (1024 * 1024), 2)
        })
        
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500 