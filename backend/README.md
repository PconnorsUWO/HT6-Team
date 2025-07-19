# Virtual Try-On Flask API

A Flask-based REST API that provides virtual try-on functionality using the IDM-VTON model from Hugging Face.

## Features

- Virtual try-on using person and garment images
- Support for both file uploads and image URLs
- RESTful API endpoints
- File upload handling
- CORS support for frontend integration
- Health check and API information endpoints
- TwelveLabs video processing integration
- MongoDB storage for garments and results
- Vellum AI recommendations
- Test video integration for development

## Installation

1. Install dependencies:

```bash
uv add flask flask-cors werkzeug gradio-client requests pymongo python-dotenv twelvelabs
```

2. Set up environment variables (create a `.env` file):

```bash
# Required for TwelveLabs integration
TWELVELABS_API_KEY=your_twelvelabs_api_key_here

# Required for Vellum recommendations
VELLUM_API_KEY=your_vellum_api_key_here

# MongoDB connection (optional, has default)
MONGODB_URI=your_mongodb_connection_string
```

2. Make sure you have the required image files:
   - `person.jpg` - Person image for try-on
   - `garment.jpg` - Garment image to try on

## Running the API

Start the Flask server:

```bash
uv run python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### 1. Health Check

**GET** `/health`

Check if the API is running.

**Response:**

```json
{
  "status": "healthy",
  "message": "Virtual Try-On API is running"
}
```

### 2. API Information

**GET** `/api-info`

Get information about available endpoints and the underlying Gradio API.

**Response:**

```json
{
  "api_info": "Client.predict() Usage Info...",
  "endpoints": {
    "health": "GET /health",
    "tryon": "POST /tryon",
    "download": "GET /download/<filename>",
    "api_info": "GET /api-info"
  }
}
```

### 3. Virtual Try-On

**POST** `/tryon`

Perform virtual try-on with uploaded images or image URLs.

**Request Options:**

**Option 1: File Upload**

- Content-Type: `multipart/form-data`
- Files:
  - `person_image`: Person image file (required)
  - `garment_image`: Garment image file (required)
- Form data (optional):
  - `garment_description`: Description of the garment (default: "Virtual try-on")
  - `is_checked`: Boolean flag (default: true)
  - `is_checked_crop`: Boolean flag (default: false)
  - `denoise_steps`: Number of denoising steps (default: 30)
  - `seed`: Random seed (default: 42)

**Option 2: Image URLs**

- Content-Type: `application/x-www-form-urlencoded` or `multipart/form-data`
- Form data:
  - `person_image_url`: URL to person image (required)
  - `garment_image_url`: URL to garment image (required)
  - `garment_description`: Description of the garment (optional, default: "Virtual try-on")
  - `is_checked`: Boolean flag (optional, default: true)
  - `is_checked_crop`: Boolean flag (optional, default: false)
  - `denoise_steps`: Number of denoising steps (optional, default: 30)
  - `seed`: Random seed (optional, default: 42)

**Response:**

```json
{
  "success": true,
  "output_image": "/path/to/output/image.png",
  "masked_image": "/path/to/masked/image.png",
  "message": "Virtual try-on completed successfully"
}
```

### 4. Download Generated Images

**GET** `/download/<filename>`

Download generated images by providing the file path.

### 5. Test TwelveLabs Integration

**GET** `/test-twelvelabs`

Test video download functionality using the provided test video URL.

**Response:**

```json
{
  "success": true,
  "message": "Test video downloaded successfully",
  "video_url": "https://videos.pexels.com/video-files/5058382/5058382-uhd_2560_1440_25fps.mp4",
  "content_type": "video/mp4",
  "content_length": "12345678",
  "file_size_bytes": 12345678,
  "file_size_mb": 11.77
}
```

**POST** `/test-twelvelabs`

Test full TwelveLabs integration with video processing and frame analysis.

**Response:**

```json
{
  "success": true,
  "best_frame": {
    "video_id": "video_123",
    "score": 0.95,
    "start": 2.5,
    "end": 3.0
  },
  "video_id": "video_123",
  "message": "Test video processed successfully with TwelveLabs"
}
```

### 6. Preset Garments

**GET** `/preset-garments`

Get available preset garments for testing.

### 7. Upload Custom Garment

**POST** `/upload-garment`

Upload a custom garment image to MongoDB.

### 8. User History

**GET** `/user-history/<user_id>`

Get user's try-on history from MongoDB.

## Testing the API

Run the test script to verify the API functionality:

```bash
uv run python test_api.py
```

### Testing TwelveLabs Integration

Test the new TwelveLabs functionality:

```bash
# Test video download
uv run python test_twelvelabs.py

# Or test manually with curl:
curl http://localhost:5000/test-twelvelabs
curl -X POST http://localhost:5000/test-twelvelabs
```

## Example Usage

### Using curl:

```bash
# Health check
curl http://localhost:5000/health

# Virtual try-on with file uploads
curl -X POST http://localhost:5000/tryon \
  -F "person_image=@person.jpg" \
  -F "garment_image=@garment.jpg" \
  -F "garment_description=Blue shirt" \
  -F "denoise_steps=30" \
  -F "seed=42"

# Virtual try-on with image URLs
curl -X POST http://localhost:5000/tryon \
  -d "person_image_url=https://example.com/person.jpg" \
  -d "garment_image_url=https://example.com/garment.jpg" \
  -d "garment_description=Blue shirt" \
  -d "denoise_steps=30" \
  -d "seed=42"
```

### Using Python requests:

```python
import requests

# Option 1: Upload images for virtual try-on
files = {
    'person_image': open('person.jpg', 'rb'),
    'garment_image': open('garment.jpg', 'rb')
}

data = {
    'garment_description': 'Blue shirt',
    'denoise_steps': '30',
    'seed': '42'
}

response = requests.post('http://localhost:5000/tryon', files=files, data=data)
result = response.json()

print(f"Output image: {result['output_image']}")
print(f"Masked image: {result['masked_image']}")

# Option 2: Use image URLs for virtual try-on
data = {
    'person_image_url': 'https://example.com/person.jpg',
    'garment_image_url': 'https://example.com/garment.jpg',
    'garment_description': 'Blue shirt',
    'denoise_steps': '30',
    'seed': '42'
}

response = requests.post('http://localhost:5000/tryon', data=data)
result = response.json()

print(f"Output image: {result['output_image']}")
print(f"Masked image: {result['masked_image']}")
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

- `400 Bad Request`: Missing files or invalid file types
- `404 Not Found`: File not found for download
- `500 Internal Server Error`: Server-side errors

## File Requirements

- Supported image formats: PNG, JPG, JPEG, GIF
- Maximum file size: 16MB per file
- Images are temporarily stored and automatically cleaned up after processing

## Notes

- The API uses the IDM-VTON model from Hugging Face
- Processing may take some time depending on the model's current load
- Generated images are stored in temporary locations and should be downloaded promptly
- CORS is enabled for frontend integration
- TwelveLabs integration uses the official Python SDK for video processing
- The system automatically creates indexes and manages video uploads through the SDK
