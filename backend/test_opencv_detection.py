#!/usr/bin/env python3
"""
MediaPipe Body Detection - Live Stream Test
Tests body pose detection with continuous live video stream
Focuses on torso and legs detection for virtual try-on
"""

import cv2
import numpy as np
import os
import sys
from datetime import datetime
import time

def test_dependencies():
    """Test if required dependencies are installed"""
    print("🔍 Testing Dependencies...")
    
    try:
        import cv2
        print(f"✅ OpenCV version: {cv2.__version__}")
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    
    try:
        import mediapipe as mp
        print(f"✅ MediaPipe version: {mp.__version__}")
    except ImportError:
        print("❌ MediaPipe not installed. Installing...")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mediapipe"])
            import mediapipe as mp
            print(f"✅ MediaPipe installed: {mp.__version__}")
        except Exception as e:
            print(f"❌ Failed to install MediaPipe: {e}")
            return False
    
    return True

def test_camera_access():
    """Test different camera indices to find a working camera"""
    print("📹 Testing camera access...")
    
    for camera_index in [0, 1, 2]:
        print(f"   Trying camera index {camera_index}...")
        cap = cv2.VideoCapture(camera_index)
        
        if cap.isOpened():
            # Try to read a frame
            ret, frame = cap.read()
            if ret and frame is not None:
                print(f"✅ Camera {camera_index} is working!")
                cap.release()
                return camera_index
            cap.release()
        else:
            print(f"   Camera {camera_index} not available")
    
    print("❌ No working camera found")
    return None

def get_body_landmarks(landmarks, mp_pose):
    """Extract key body landmarks for torso and legs"""
    if not landmarks:
        return None
    
    # Define key body parts for virtual try-on
    body_parts = {
        'left_shoulder': mp_pose.PoseLandmark.LEFT_SHOULDER,
        'right_shoulder': mp_pose.PoseLandmark.RIGHT_SHOULDER,
        'left_hip': mp_pose.PoseLandmark.LEFT_HIP,
        'right_hip': mp_pose.PoseLandmark.RIGHT_HIP,
        'left_knee': mp_pose.PoseLandmark.LEFT_KNEE,
        'right_knee': mp_pose.PoseLandmark.RIGHT_KNEE,
        'left_ankle': mp_pose.PoseLandmark.LEFT_ANKLE,
        'right_ankle': mp_pose.PoseLandmark.RIGHT_ANKLE,
        'left_elbow': mp_pose.PoseLandmark.LEFT_ELBOW,
        'right_elbow': mp_pose.PoseLandmark.RIGHT_ELBOW,
        'left_wrist': mp_pose.PoseLandmark.LEFT_WRIST,
        'right_wrist': mp_pose.PoseLandmark.RIGHT_WRIST
    }
    
    extracted_landmarks = {}
    for part_name, landmark_id in body_parts.items():
        if landmark_id < len(landmarks.landmark):
            landmark = landmarks.landmark[landmark_id]
            extracted_landmarks[part_name] = {
                'x': landmark.x,
                'y': landmark.y,
                'z': landmark.z,
                'visibility': landmark.visibility
            }
    
    return extracted_landmarks

def calculate_body_confidence(landmarks):
    """Calculate confidence based on body pose detection"""
    if not landmarks:
        return 0.0
    
    # Count visible body parts
    visible_parts = 0
    total_parts = len(landmarks)
    
    # Key parts for virtual try-on (torso and legs)
    key_parts = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip', 
                 'left_knee', 'right_knee', 'left_ankle', 'right_ankle']
    
    key_visible = 0
    for part_name in key_parts:
        if part_name in landmarks:
            part = landmarks[part_name]
            if part['visibility'] > 0.5:  # MediaPipe visibility threshold
                visible_parts += 1
                if part_name in key_parts:
                    key_visible += 1
    
    # Base confidence from visible parts
    base_confidence = visible_parts / total_parts if total_parts > 0 else 0
    
    # Bonus for key body parts (torso and legs)
    key_confidence = key_visible / len(key_parts) if key_parts else 0
    
    # Weighted confidence (emphasize key parts)
    final_confidence = (base_confidence * 0.3) + (key_confidence * 0.7)
    
    return min(final_confidence, 1.0)

def detect_body_pose(frame, mp_pose, pose):
    """Detect body pose using MediaPipe"""
    # Convert BGR to RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    results = pose.process(rgb_frame)
    
    # Extract landmarks
    landmarks = None
    if results.pose_landmarks:
        landmarks = get_body_landmarks(results.pose_landmarks, mp_pose)
    
    return results, landmarks

def live_body_detection(camera_index=0):
    """Continuous live body detection with MediaPipe"""
    print(f"🎥 Starting MediaPipe body detection with camera {camera_index}")
    print("Controls:")
    print("  - Press 'q' to quit")
    print("  - Press 's' to save current frame")
    print("  - Press 'r' to reset confidence tracking")
    print("  - Press 'h' to show/hide help text")
    print("  - Press 'l' to show/hide landmarks")
    
    # Initialize MediaPipe
    import mediapipe as mp
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles
    
    # Initialize pose detection
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=1,  # 0, 1, or 2 (higher = more accurate but slower)
        smooth_landmarks=True,
        enable_segmentation=False,
        smooth_segmentation=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    
    # Open camera
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"❌ Could not open camera {camera_index}")
        return
    
    # Set camera properties for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Tracking variables
    show_help = True
    show_landmarks = True
    best_confidence = 0
    best_frame = None
    frame_count = 0
    start_time = time.time()
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("❌ Failed to read frame from camera")
                break
            
            frame_count += 1
            
            # Detect body pose
            results, landmarks = detect_body_pose(frame, mp_pose, pose)
            
            # Calculate confidence
            confidence = calculate_body_confidence(landmarks)
            
            # Track best confidence
            if confidence > best_confidence:
                best_confidence = confidence
                best_frame = frame.copy()
            
            # Create display frame
            display_frame = frame.copy()
            
            # Draw MediaPipe pose landmarks
            if show_landmarks and results.pose_landmarks:
                mp_drawing.draw_landmarks(
                    display_frame,
                    results.pose_landmarks,
                    mp_pose.POSE_CONNECTIONS,
                    landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
                )
            
            # Add confidence and info text
            y_offset = 30
            cv2.putText(display_frame, f'Body Confidence: {confidence:.1%}', 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            y_offset += 30
            
            cv2.putText(display_frame, f'Best Confidence: {best_confidence:.1%}', 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            y_offset += 30
            
            # Show detected body parts
            if landmarks:
                visible_parts = sum(1 for part in landmarks.values() if part['visibility'] > 0.5)
                total_parts = len(landmarks)
                cv2.putText(display_frame, f'Body Parts: {visible_parts}/{total_parts} visible', 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                y_offset += 25
                
                # Show key body parts status
                key_parts = ['left_shoulder', 'right_shoulder', 'left_hip', 'right_hip', 
                            'left_knee', 'right_knee', 'left_ankle', 'right_ankle']
                key_visible = sum(1 for part in key_parts 
                                if part in landmarks and landmarks[part]['visibility'] > 0.5)
                cv2.putText(display_frame, f'Key Parts (Torso/Legs): {key_visible}/{len(key_parts)}', 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25
            else:
                cv2.putText(display_frame, 'No body detected', 
                           (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                y_offset += 25
            
            # FPS calculation
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time if elapsed_time > 0 else 0
            cv2.putText(display_frame, f'FPS: {fps:.1f}', 
                       (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)
            
            # Add help text if enabled
            if show_help:
                help_y = display_frame.shape[0] - 140
                cv2.putText(display_frame, 'q: quit | s: save | r: reset | h: help | l: landmarks', 
                           (10, help_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                help_y += 20
                cv2.putText(display_frame, 'Green: Key body parts | Yellow: Best confidence', 
                           (10, help_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                help_y += 20
                cv2.putText(display_frame, 'Focus on torso and legs for virtual try-on', 
                           (10, help_y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show the frame
            cv2.imshow('MediaPipe Body Detection', display_frame)
            
            # Handle key presses
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # Save current frame
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"body_detection_{timestamp}.jpg"
                cv2.imwrite(filename, display_frame)
                print(f"💾 Frame saved: {filename}")
            elif key == ord('r'):
                # Reset best confidence
                best_confidence = 0
                best_frame = None
                print("🔄 Reset confidence tracking")
            elif key == ord('h'):
                # Toggle help text
                show_help = not show_help
                print(f"ℹ️ Help text {'shown' if show_help else 'hidden'}")
            elif key == ord('l'):
                # Toggle landmarks
                show_landmarks = not show_landmarks
                print(f"🎯 Landmarks {'shown' if show_landmarks else 'hidden'}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        pose.close()
        
        # Print final statistics
        print(f"\n📊 Session Statistics:")
        print(f"   Total frames processed: {frame_count}")
        print(f"   Session duration: {elapsed_time:.1f} seconds")
        print(f"   Average FPS: {fps:.1f}")
        print(f"   Best confidence achieved: {best_confidence:.1%}")
        
        if best_frame is not None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            best_filename = f"best_body_detection_{timestamp}.jpg"
            cv2.imwrite(best_filename, best_frame)
            print(f"💾 Best frame saved: {best_filename}")

def main():
    """Main function"""
    print("🚀 MediaPipe Body Detection Test")
    print("=" * 50)
    
    # Test 1: Dependencies
    if not test_dependencies():
        print("❌ Dependency test failed. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test 2: Camera Access
    camera_index = test_camera_access()
    if camera_index is None:
        print("❌ No camera available. Exiting.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Test 3: Live Detection
    print("🎥 Starting MediaPipe Body Detection")
    print("This will open your camera for continuous body pose detection.")
    print("Focus on having your torso and legs clearly visible for virtual try-on.")
    
    try:
        live_body_detection(camera_index)
    except KeyboardInterrupt:
        print("\n⏹️ Detection stopped by user")
    except Exception as e:
        print(f"\n❌ Error during detection: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Body detection test completed!")

if __name__ == "__main__":
    main() 