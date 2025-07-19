import cv2
import numpy as np
import base64
import os
from config import Config

def get_video_info(video_path):
    """Get basic video information using OpenCV"""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'error': 'Could not open video file'}
        
        info = {
            'file_path': video_path,
            'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            'fps': cap.get(cv2.CAP_PROP_FPS),
            'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        }
        
        if info['fps'] > 0:
            info['duration'] = info['frame_count'] / info['fps']
        
        cap.release()
        return info
        
    except Exception as e:
        return {'error': str(e)}

def detect_body_pose_in_video(video_path: str) -> dict:
    """
    Detect body pose in video using OpenCV and find the best frame
    where a person is clearly visible with annotations
    """
    try:
        print(f"Processing video for body detection: {video_path}")
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception("Could not open video file")
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = frame_count / fps if fps > 0 else 0
        
        print(f"Video info: {frame_count} frames, {fps} fps, {duration:.2f}s duration")
        
        best_frame = None
        best_confidence = 0
        best_frame_number = 0
        best_annotations = None
        
        # Load pre-trained models for detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        
        # Process every 5th frame to speed up processing
        frame_skip = 5
        processed_frames = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frames += 1
            
            # Skip frames to speed up processing
            if processed_frames % frame_skip != 0:
                continue
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces and bodies
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            bodies = body_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Calculate confidence based on detection results
            face_confidence = len(faces) * 0.3  # Each face adds 30% confidence
            body_confidence = len(bodies) * 0.7  # Each body adds 70% confidence
            
            total_confidence = min(face_confidence + body_confidence, 1.0)
            
            # Additional confidence based on frame quality (brightness, contrast)
            # Calculate average brightness
            brightness = np.mean(gray)
            brightness_confidence = min(brightness / 128.0, 1.0) * 0.2  # Up to 20% from brightness
            
            # Calculate contrast
            contrast = np.std(gray)
            contrast_confidence = min(contrast / 50.0, 1.0) * 0.1  # Up to 10% from contrast
            
            final_confidence = total_confidence + brightness_confidence + contrast_confidence
            
            # Check if this is the best frame so far
            if final_confidence > best_confidence and final_confidence >= 0.5:  # At least 50% confidence
                best_confidence = final_confidence
                best_frame = frame.copy()
                best_frame_number = processed_frames
                
                # Create annotations for the best frame
                annotated_frame = frame.copy()
                annotations = {
                    "faces": [],
                    "bodies": [],
                    "confidence_breakdown": {
                        "face_confidence": face_confidence,
                        "body_confidence": body_confidence,
                        "brightness_confidence": brightness_confidence,
                        "contrast_confidence": contrast_confidence,
                        "total_confidence": final_confidence
                    }
                }
                
                # Draw face annotations
                for (x, y, w, h) in faces:
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, 'Face', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    annotations["faces"].append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
                
                # Draw body annotations
                for (x, y, w, h) in bodies:
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(annotated_frame, 'Body', (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)
                    annotations["bodies"].append({"x": int(x), "y": int(y), "width": int(w), "height": int(h)})
                
                # Add confidence text
                cv2.putText(annotated_frame, f'Confidence: {final_confidence:.2%}', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f'Faces: {len(faces)}, Bodies: {len(bodies)}', 
                           (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                best_annotations = annotations
                print(f"New best frame found: frame {processed_frames}, confidence: {final_confidence:.2f}")
                print(f"  - Faces detected: {len(faces)}, Bodies detected: {len(bodies)}")
                print(f"  - Brightness: {brightness:.1f}, Contrast: {contrast:.1f}")
        
        cap.release()
        
        if best_frame is not None:
            # Convert the annotated frame to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            frame_data_url = f"data:image/jpeg;base64,{frame_base64}"
            
            return {
                "success": True,
                "best_frame": frame_data_url,
                "confidence": best_confidence,
                "frame_number": best_frame_number,
                "annotations": best_annotations,
                "message": f"Person detected with {best_confidence:.2%} confidence"
            }
        else:
            return {
                "success": False,
                "message": "No suitable frame found with a person clearly visible"
            }
            
    except Exception as e:
        print(f"Error in body detection: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing video: {str(e)}"
        } 