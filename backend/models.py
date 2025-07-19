from datetime import datetime, timedelta
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId
from config import Config

# MongoDB connection
mongo_client = MongoClient(Config.MONGODB_URI)
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

def save_garment_to_db(garment_data):
    """Save garment data to MongoDB"""
    return db.garments.insert_one(garment_data)

def get_garment_by_id(garment_id):
    """Get garment from MongoDB by ID"""
    return db.garments.find_one({"id": garment_id})

def save_video_to_gridfs(video_data, metadata):
    """Save video to GridFS"""
    return fs.put(video_data, **metadata)

def get_video_from_gridfs(video_id):
    """Get video from GridFS by ID"""
    return fs.get(ObjectId(video_id))

def delete_video_from_gridfs(video_id):
    """Delete video from GridFS by ID"""
    return fs.delete(ObjectId(video_id))

def save_tryon_result(result_data):
    """Save try-on result to MongoDB"""
    return db.tryon_results.insert_one(result_data)

def get_user_history(user_id, limit=10):
    """Get user's try-on history"""
    return list(db.tryon_results.find(
        {"user_id": user_id},
        {"_id": 0}
    ).sort("created_at", -1).limit(limit)) 