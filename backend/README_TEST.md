# OpenCV Body Detection Test Script

This standalone script tests the OpenCV body detection functionality locally on your laptop without needing the Flask server.

## Features

- ✅ **OpenCV Installation Test**: Verifies OpenCV is properly installed
- 🎬 **Test Video Generation**: Creates a synthetic test video with moving objects
- 🔍 **Body Detection**: Tests the same detection algorithm used in the main app
- 📹 **Live Webcam Test**: Optional real-time testing with your webcam
- 📊 **Detailed Results**: Shows confidence scores and detection breakdown
- 💾 **Frame Saving**: Saves the best detected frame with annotations

## Requirements

- Python 3.10+
- OpenCV (`opencv-python`)
- NumPy

## Installation

```bash
cd backend
uv sync
```

## Usage

### Run the Complete Test Suite

```bash
cd backend
uv run python test_opencv_detection.py
```

This will run:

1. **OpenCV Installation Test** - Verifies everything is working
2. **Video Processing Test** - Creates and processes a test video
3. **Webcam Test** (optional) - Live testing with your camera

### What the Script Does

1. **Tests OpenCV Installation**

   - Checks OpenCV version
   - Verifies cascade classifiers are available
   - Tests classifier loading

2. **Creates Test Video**

   - Generates a 5-second synthetic video
   - Contains moving rectangles to simulate a person
   - Tests the detection algorithm

3. **Processes Video**

   - Analyzes every 10th frame for speed
   - Detects faces and bodies using Haar cascades
   - Calculates confidence scores
   - Saves the best frame with annotations

4. **Live Webcam Test** (optional)
   - Opens your webcam
   - Shows real-time detection
   - Press 'q' to quit, 's' to save a frame

## Output Files

The script creates several files:

- `test_video.mp4` - Generated test video (auto-deleted)
- `best_frame_YYYYMMDD_HHMMSS.jpg` - Best detected frame with annotations
- `webcam_frame_YYYYMMDD_HHMMSS.jpg` - Saved webcam frames (if used)

## Sample Output

```
🚀 OpenCV Body Detection Test Script
==================================================
🔍 Testing OpenCV Installation...
✅ OpenCV version: 4.8.1.78
✅ Face cascade found: /path/to/haarcascade_frontalface_default.xml
✅ Body cascade found: /path/to/haarcascade_fullbody.xml
✅ Face cascade classifier loaded successfully
✅ Body cascade classifier loaded successfully

==================================================
🎬 Test 2: Video Processing
🎬 Creating test video...
✅ Test video created: test_video.mp4
🔍 Processing video for body detection: test_video.mp4
📊 Video info: 150 frames, 30.0 fps, 5.00s duration
🎯 Analyzing frames for body detection...
🎯 New best frame found: frame 50, confidence: 0.85
   - Faces detected: 1, Bodies detected: 1
   - Brightness: 45.2, Contrast: 78.9
💾 Best frame saved: best_frame_20241220_143022.jpg

📊 Detection Result:
   Success: True
   Message: Person detected with 85.00% confidence
   Confidence: 85.00%
   Frame Number: 50
   Best Frame: best_frame_20241220_143022.jpg
   Faces Detected: 1
   Bodies Detected: 1
   Confidence Breakdown:
     face_confidence: 30.00%
     body_confidence: 70.00%
     brightness_confidence: 7.06%
     contrast_confidence: 10.00%
     total_confidence: 85.00%

==================================================
📹 Test 3: Live Webcam Test
This will open your webcam for live testing.
Do you want to test with webcam? (y/n): n

==================================================
✅ All tests completed!
🧹 Cleaned up test video: test_video.mp4
```

## Troubleshooting

### OpenCV Installation Issues

```bash
# If OpenCV is not installed
uv add opencv-python numpy

# If cascade files are missing
# This usually means OpenCV is not properly installed
pip uninstall opencv-python
pip install opencv-python
```

### Webcam Issues

- Make sure your webcam is not being used by another application
- Try different camera indices (0, 1, 2) in the script
- Check camera permissions on macOS/Linux

### Video Codec Issues

- On macOS, you might need to install additional codecs
- Try changing the fourcc code in the script from 'mp4v' to 'avc1'

## Understanding the Results

### Confidence Scores

- **Face Detection**: 30% per detected face
- **Body Detection**: 70% per detected body
- **Image Quality**: Up to 30% based on brightness and contrast
- **Total**: Sum of all components (max 100%)

### Annotations

- **Green rectangles**: Detected faces
- **Blue rectangles**: Detected bodies
- **White text**: Confidence scores and detection counts

## Integration with Main App

This test script uses the exact same detection algorithm as the main Flask application. If this script works, the main app should work too!

The key differences:

- Main app: Processes uploaded videos from frontend
- Test script: Creates synthetic videos or uses webcam
- Both use identical detection logic and confidence calculations
