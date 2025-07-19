# Backend Modular Structure

The backend has been refactored into a modular structure for better maintainability and organization.

## File Structure

```
backend/
├── app.py                 # Main Flask application (simplified)
├── app_original.py        # Original monolithic app (backup)
├── config.py              # Configuration and constants
├── models.py              # Database operations and models
├── utils.py               # Utility functions
├── services/              # Business logic services
│   ├── __init__.py
│   ├── body_detection.py  # OpenCV body detection logic
│   ├── tryon.py          # Virtual try-on operations
│   └── recommendations.py # AI recommendations
└── routes/                # API route handlers
    ├── __init__.py
    ├── garments.py        # Garment-related endpoints
    ├── videos.py          # Video-related endpoints
    └── tryon.py           # Try-on endpoints
```

## Module Descriptions

### `config.py`

- Centralized configuration management
- Environment variables
- Constants and preset data
- File extension definitions

### `models.py`

- MongoDB connection and operations
- GridFS file storage functions
- Database cleanup utilities
- Data access layer functions

### `utils.py`

- File validation utilities
- Upload folder management
- Helper functions for file operations

### `services/`

- **body_detection.py**: OpenCV-based body pose detection
- **tryon.py**: Virtual try-on operations using Gradio client
- **recommendations.py**: AI-powered clothing recommendations

### `routes/`

- **garments.py**: Garment upload and management endpoints
- **videos.py**: Video upload, download, and body detection endpoints
- **tryon.py**: Virtual try-on and user history endpoints

### `app.py`

- Main Flask application factory
- Blueprint registration
- CORS configuration
- Health check endpoints

## API Endpoints

All endpoints are now prefixed with `/api`:

### Garments

- `GET /api/preset-garments` - Get available preset garments
- `POST /api/upload-garment` - Upload custom garment

### Videos

- `POST /api/upload-video` - Upload video to GridFS
- `GET /api/download-video/<video_id>` - Download video
- `POST /api/cleanup-videos` - Clean up expired videos
- `POST /api/detect-body` - Detect body pose in video
- `GET/POST /api/test-body-detection` - Test body detection

### Try-on

- `POST /api/tryon` - Perform virtual try-on
- `GET /api/user-history/<user_id>` - Get user history

### Health

- `GET /health` - Health check
- `GET /test` - Simple test endpoint

## Benefits of Modular Structure

1. **Separation of Concerns**: Each module has a specific responsibility
2. **Maintainability**: Easier to find and modify specific functionality
3. **Testability**: Individual modules can be tested in isolation
4. **Scalability**: New features can be added as separate modules
5. **Code Reusability**: Services can be reused across different routes
6. **Readability**: Smaller, focused files are easier to understand

## Running the Application

The application can still be run the same way:

```bash
uv run app.py
```

Or using uvicorn (as per project memory):

```bash
uv run uvicorn app:app --host 0.0.0.0 --port 5000
```

## Migration Notes

- The original `app.py` has been backed up as `app_original.py`
- All functionality has been preserved
- API endpoints now have `/api` prefix
- Configuration is centralized in `config.py`
- Database operations are abstracted in `models.py`
