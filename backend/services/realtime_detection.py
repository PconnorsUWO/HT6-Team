import cv2
import numpy as np
import base64
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from typing import Dict, List, Tuple, Optional

class RealtimeBodyDetector:
    """Real-time body detection service using OpenCV and MediaPipe"""
    
    def __init__(self):
        """Initialize detection models"""
        # OpenCV Haar cascades for basic detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_alt_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        self.body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        self.upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # MediaPipe for enhanced pose detection
        self.mp_pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Get pose connections from the correct module
        self.pose_connections = mp.solutions.pose.POSE_CONNECTIONS
        
        # Detection state
        self.frame_count = 0
        self.detection_history = []
        
    def process_frame(self, frame_data: str) -> Dict:
        """
        Process a single video frame and return annotated frame with detection results
        
        Args:
            frame_data: Base64 encoded image data
            
        Returns:
            Dict containing annotated frame, detection results, and confidence scores
        """
        try:
            # Decode base64 frame
            frame_bytes = base64.b64decode(frame_data.split(',')[1])
            frame_array = np.frombuffer(frame_bytes, dtype=np.uint8)
            frame = cv2.imdecode(frame_array, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {"error": "Invalid frame data"}
            
            # Create copy for annotation
            annotated_frame = frame.copy()
            
            # Convert to RGB for MediaPipe
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Get detections
            detection_results = self._detect_body_parts(frame, frame_rgb, annotated_frame)
            
            # Add frame info
            detection_results["frame_number"] = self.frame_count
            detection_results["timestamp"] = self.frame_count / 30.0  # Assuming 30 FPS
            
            # Update frame counter
            self.frame_count += 1
            
            # Encode annotated frame back to base64
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            annotated_frame_b64 = base64.b64encode(buffer).decode('utf-8')
            detection_results["annotated_frame"] = f"data:image/jpeg;base64,{annotated_frame_b64}"
            
            return detection_results
            
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return {"error": f"Frame processing error: {str(e)}"}
    
    def _detect_body_parts(self, frame: np.ndarray, frame_rgb: np.ndarray, annotated_frame: np.ndarray) -> Dict:
        """Detect body parts using OpenCV and MediaPipe"""
        height, width = frame.shape[:2]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        detection_results = {
            "faces": [],
            "bodies": [],
            "eyes": [],
            "pose_landmarks": [],
            "confidence": 0.0,
            "detection_quality": {}
        }
        
        # 1. OpenCV Face Detection
        faces1 = self.face_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        faces2 = self.face_alt_cascade.detectMultiScale(gray, 1.1, 4, minSize=(30, 30))
        
        # Combine and deduplicate faces
        all_faces = list(faces1) + list(faces2)
        faces = self._deduplicate_detections(all_faces, 0.5)
        
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(annotated_frame, f'Face {i+1}', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            
            detection_results["faces"].append({
                "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                "confidence": 0.8
            })
            
            # Detect eyes within face region
            face_roi = gray[y:y+h, x:x+w]
            eyes = self.eye_cascade.detectMultiScale(face_roi, 1.1, 3, minSize=(20, 20))
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(annotated_frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (255, 255, 0), 1)
                detection_results["eyes"].append({
                    "x": int(x+ex), "y": int(y+ey), "width": int(ew), "height": int(eh),
                    "confidence": 0.7
                })
        
        # 2. OpenCV Body Detection
        bodies = self.body_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 100))
        upper_bodies = self.upper_body_cascade.detectMultiScale(gray, 1.1, 4, minSize=(50, 50))
        
        all_bodies = list(bodies) + list(upper_bodies)
        bodies = self._deduplicate_detections(all_bodies, 0.7)
        
        for i, (x, y, w, h) in enumerate(bodies):
            cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.putText(annotated_frame, f'Body {i+1}', (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)
            
            detection_results["bodies"].append({
                "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                "confidence": 0.75
            })
        
        # 3. MediaPipe Pose Detection
        try:
            pose_results = self.mp_pose.process(frame_rgb)
            if pose_results.pose_landmarks:
                # Draw pose landmarks
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    pose_results.pose_landmarks,
                    self.pose_connections,
                    landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style()
                )
                
                # Extract key landmarks
                landmarks = []
                for i, landmark in enumerate(pose_results.pose_landmarks.landmark):
                    if landmark.visibility > 0.5:  # Only visible landmarks
                        x_px = int(landmark.x * width)
                        y_px = int(landmark.y * height)
                        landmarks.append({
                            "id": i,
                            "x": x_px,
                            "y": y_px,
                            "confidence": landmark.visibility,
                            "name": self._get_landmark_name(i)
                        })
                
                detection_results["pose_landmarks"] = landmarks
        except Exception as e:
            print(f"MediaPipe pose detection error: {str(e)}")
            # Continue without pose detection if it fails
        
        # 4. Calculate overall confidence
        face_confidence = len(faces) * 0.25
        body_confidence = len(bodies) * 0.4
        pose_confidence = len(detection_results["pose_landmarks"]) * 0.01  # Each landmark adds 1%
        
        total_confidence = min(face_confidence + body_confidence + pose_confidence, 1.0)
        detection_results["confidence"] = total_confidence
        
        # 5. Add detection quality metrics
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        detection_results["detection_quality"] = {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "face_count": len(faces),
            "body_count": len(bodies),
            "landmark_count": len(detection_results["pose_landmarks"]),
            "total_confidence": total_confidence
        }
        
        # 6. Add confidence overlay to frame
        cv2.putText(annotated_frame, f'Confidence: {total_confidence:.1%}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f'Faces: {len(faces)}, Bodies: {len(bodies)}', 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.putText(annotated_frame, f'Landmarks: {len(detection_results["pose_landmarks"])}', 
                   (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        return detection_results
    
    def _deduplicate_detections(self, detections: List[Tuple], threshold: float) -> List[Tuple]:
        """Remove duplicate detections based on overlap threshold"""
        if not detections:
            return []
        
        deduplicated = []
        for detection in detections:
            is_duplicate = False
            for existing in deduplicated:
                x1, y1, w1, h1 = detection
                x2, y2, w2, h2 = existing
                
                # Calculate overlap
                x_overlap = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
                y_overlap = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
                overlap_area = x_overlap * y_overlap
                
                area1 = w1 * h1
                area2 = w2 * h2
                min_area = min(area1, area2)
                
                if overlap_area / min_area > threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(detection)
        
        return deduplicated
    
    def _get_landmark_name(self, landmark_id: int) -> str:
        """Get human-readable name for MediaPipe landmark ID"""
        landmark_names = {
            0: "nose", 1: "left_eye_inner", 2: "left_eye", 3: "left_eye_outer",
            4: "right_eye_inner", 5: "right_eye", 6: "right_eye_outer",
            7: "left_ear", 8: "right_ear", 9: "mouth_left", 10: "mouth_right",
            11: "left_shoulder", 12: "right_shoulder", 13: "left_elbow", 14: "right_elbow",
            15: "left_wrist", 16: "right_wrist", 17: "left_pinky", 18: "right_pinky",
            19: "left_index", 20: "right_index", 21: "left_thumb", 22: "right_thumb",
            23: "left_hip", 24: "right_hip", 25: "left_knee", 26: "right_knee",
            27: "left_ankle", 28: "right_ankle", 29: "left_heel", 30: "right_heel",
            31: "left_foot_index", 32: "right_foot_index"
        }
        return landmark_names.get(landmark_id, f"landmark_{landmark_id}")
    
    def reset(self):
        """Reset detection state"""
        self.frame_count = 0
        self.detection_history = [] 