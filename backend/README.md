# Virtual Try-On Backend API

A Flask-based backend API for virtual try-on functionality with video processing and AI recommendations.

## Features

- **Video Processing**: Upload videos to MongoDB GridFS and process them with TwelveLabs AI
- **Virtual Try-On**: AI-powered clothing try-on using Gradio client
- **Garment Management**: Upload custom garments and manage preset garments
- **AI Recommendations**: Generate style recommendations based on try-on results
- **User History**: Track user interactions and try-on history

## New Video Processing Architecture

The application now uses a two-step video processing approach with **FFmpeg conversion**:

### Step 1: Video Upload to MongoDB

- Videos are uploaded to MongoDB GridFS for temporary storage
- Each video gets a unique ID and public URL
- Videos automatically expire after 24 hours
- Supports MP4 and WebM formats

### Step 2: FFmpeg Video Conversion

- **NEW**: Browser-recorded videos are converted to MP4 using FFmpeg
- Ensures compatibility with TwelveLabs API requirements
- Converts WebM/other formats to H.264 MP4 with proper headers
- Validates video duration and quality

### Step 3: TwelveLabs Processing

- The converted MP4 video URL is sent to TwelveLabs for AI analysis
- TwelveLabs finds the best frame for virtual try-on
- Results include frame selection and confidence scores

## API Endpoints

### Video Processing

- `POST /upload-video` - Upload video to MongoDB GridFS
- `GET /download-video/<video_id>` - Download video from MongoDB
- `POST /process-video` - Process video with TwelveLabs (uses MongoDB URL)
- `POST /cleanup-videos` - Manually trigger cleanup of expired videos

### Try-On

- `POST /tryon` - Perform virtual try-on with selected frame and garment
- `GET /preset-garments` - Get list of preset garments
- `POST /upload-garment` - Upload custom garment

### User Management

- `GET /user-history/<user_id>` - Get user's try-on history

### Testing

- `GET /test` - Test backend connectivity
- `GET /health` - Health check endpoint
- `GET /test-twelvelabs` - Test TwelveLabs integration

## Environment Variables

Create a `.env` file with the following variables:

```env
MONGODB_URI=mongodb://localhost:27017/virtual_tryon
TWELVELABS_API_KEY=your_twelvelabs_api_key
VELLUM_API_KEY=your_vellum_api_key
```

## Installation

1. Install dependencies:

```bash
uv sync
```

2. Set up environment variables in `.env`

3. Start the server:

```bash
uv run python app.py
```

## Video Processing Flow

1. **Frontend**: User records video using browser's MediaRecorder API
2. **Upload**: Video blob is uploaded to `/upload-video` endpoint
3. **MongoDB Storage**: Video is stored in GridFS with 24-hour expiration
4. **Download**: Video is downloaded from MongoDB URL
5. **FFmpeg Conversion**: Video is converted to MP4 format with H.264 codec
6. **Processing**: Converted video is sent to `/process-video` for TwelveLabs analysis
7. **Frame Selection**: AI finds the best frame for virtual try-on
8. **Try-On**: Selected frame and garment are processed for virtual try-on
9. **Cleanup**: Expired videos are automatically removed

## Testing

Run the test script to verify the new video processing functionality:

```bash
uv run python test_mongodb_video.py
```

This will test:

- Backend connectivity
- Video upload to MongoDB
- Video download from MongoDB
- Video processing with TwelveLabs

## Benefits of New Approach

- **Scalability**: Videos are stored in MongoDB instead of local filesystem
- **Reliability**: GridFS handles large files efficiently
- **Format Compatibility**: FFmpeg ensures all videos are converted to TwelveLabs-compatible MP4
- **Cleanup**: Automatic expiration prevents storage bloat
- **URL-based**: TwelveLabs can access videos via HTTP URLs
- **Stateless**: Backend doesn't need to manage local video files
- **Robust Processing**: Browser-recorded videos are properly converted and validated

## Error Handling

- Videos automatically expire after 24 hours
- Failed uploads are cleaned up immediately
- Network errors are handled gracefully
- Invalid video formats are rejected
- TwelveLabs API errors are logged and reported
