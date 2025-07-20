import cv2
import numpy as np
import base64
import mediapipe as mp
from typing import Dict, List, Tuple, Optional

class RealtimeBodyDetector:
    """Optimized real-time body detection focusing only on torso, legs, and arms"""
    
    def __init__(self):
        """Initialize detection models with minimal processing"""
        # MediaPipe for essential pose detection only
        self.mp_pose = mp.solutions.pose.Pose(
            static_image_mode=False,
            model_complexity=0,  # Use fastest model
            smooth_landmarks=False,  # Disable smoothing for speed
            min_detection_confidence=0.3,  # Lower threshold for speed
            min_tracking_confidence=0.3
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # Get pose connections from the correct module
        self.pose_connections = mp.solutions.pose.POSE_CONNECTIONS
        
        # Detection state
        self.frame_count = 0
        self.best_confidence = 0.0
        self.best_frame = None
        
        # Purple color for brand consistency (BGR format)
        self.brand_color = (255, 0, 255)  # Purple in BGR
        
        # Define essential body parts for virtual try-on
        self.essential_landmarks = {
            # Torso
            'left_shoulder': mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,
            'left_hip': mp.solutions.pose.PoseLandmark.LEFT_HIP,
            'right_hip': mp.solutions.pose.PoseLandmark.RIGHT_HIP,
            
            # Arms
            'left_elbow': mp.solutions.pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': mp.solutions.pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': mp.solutions.pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': mp.solutions.pose.PoseLandmark.RIGHT_WRIST,
            
            # Legs
            'left_knee': mp.solutions.pose.PoseLandmark.LEFT_KNEE,
            'right_knee': mp.solutions.pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': mp.solutions.pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': mp.solutions.pose.PoseLandmark.RIGHT_ANKLE,
        }
        
    def calculate_essential_confidence(self, landmarks) -> float:
        """Calculate confidence based only on essential body parts (torso, legs, arms)"""
        if not landmarks:
            return 0.0
        
        # Count visible essential parts
        visible_essential = 0
        total_essential = len(self.essential_landmarks)
        
        for landmark_id in self.essential_landmarks.values():
            if landmark_id < len(landmarks.landmark):
                landmark = landmarks.landmark[landmark_id]
                if landmark.visibility > 0.3:  # Lower threshold for speed
                    visible_essential += 1
        
        # Simple confidence calculation
        confidence = visible_essential / total_essential if total_essential > 0 else 0
        return min(confidence, 1.0)
        
    def process_frame(self, frame_data: str) -> Dict:
        """
        Process a single video frame with minimal processing
        
        Args:
            frame_data: Base64 encoded image data
            
        Returns:
            Dict containing annotated frame (for display), clean frame (for try-on), 
            detection results, and confidence scores
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
            
            # Get essential body part detection
            detection_results = self._detect_essential_parts(frame_rgb, annotated_frame)
            
            # Update best confidence tracking - store the CLEAN frame (not annotated)
            if detection_results["confidence"] > self.best_confidence:
                self.best_confidence = detection_results["confidence"]
                self.best_frame = frame.copy()  # Store clean frame for try-on
            
            # Add frame info
            detection_results["frame_number"] = self.frame_count
            detection_results["timestamp"] = self.frame_count / 30.0  # Assuming 30 FPS
            detection_results["best_confidence"] = self.best_confidence
            
            # Update frame counter
            self.frame_count += 1
            
            # Encode annotated frame back to base64 (for display)
            _, buffer = cv2.imencode('.jpg', annotated_frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            annotated_frame_b64 = base64.b64encode(buffer).decode('utf-8')
            detection_results["annotated_frame"] = f"data:image/jpeg;base64,{annotated_frame_b64}"
            
            # Encode clean frame back to base64 (for try-on processing)
            _, clean_buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            clean_frame_b64 = base64.b64encode(clean_buffer).decode('utf-8')
            detection_results["clean_frame"] = f"data:image/jpeg;base64,{clean_frame_b64}"
            
            return detection_results
            
        except Exception as e:
            print(f"Error processing frame: {str(e)}")
            return {"error": f"Frame processing error: {str(e)}"}
    
    def _detect_essential_parts(self, frame_rgb: np.ndarray, annotated_frame: np.ndarray) -> Dict:
        """Detect only essential body parts (torso, legs, arms) with minimal processing"""
        height, width = frame_rgb.shape[:2]
        
        detection_results = {
            "confidence": 0.0,
            "detection_quality": {},
            "essential_landmarks": []
        }
        
        # MediaPipe Pose Detection - only essential parts
        try:
            pose_results = self.mp_pose.process(frame_rgb)
            if pose_results.pose_landmarks:
                # Calculate confidence based on essential parts only
                confidence = self.calculate_essential_confidence(pose_results.pose_landmarks)
                detection_results["confidence"] = confidence
                
                # Create custom drawing style with purple color
                purple_rgb = (self.brand_color[2], self.brand_color[1], self.brand_color[0])  # BGR to RGB
                purple_style = mp.solutions.drawing_styles.DrawingSpec(
                    color=purple_rgb, thickness=2, circle_radius=3
                )
                purple_connections_style = mp.solutions.drawing_styles.DrawingSpec(
                    color=purple_rgb, thickness=2
                )
                
                # Draw only essential pose landmarks with purple color
                self.mp_drawing.draw_landmarks(
                    annotated_frame,
                    pose_results.pose_landmarks,
                    self.pose_connections,
                    landmark_drawing_spec=purple_style,
                    connection_drawing_spec=purple_connections_style
                )
                
                # Extract only essential landmarks
                essential_landmarks = []
                for part_name, landmark_id in self.essential_landmarks.items():
                    if landmark_id < len(pose_results.pose_landmarks.landmark):
                        landmark = pose_results.pose_landmarks.landmark[landmark_id]
                        if landmark.visibility > 0.3:  # Only visible landmarks
                            x_px = int(landmark.x * width)
                            y_px = int(landmark.y * height)
                            essential_landmarks.append({
                                "part": part_name,
                                "x": x_px,
                                "y": y_px,
                                "confidence": landmark.visibility
                            })
                
                detection_results["essential_landmarks"] = essential_landmarks
                
        except Exception as e:
            print(f"MediaPipe pose detection error: {str(e)}")
            # Continue without pose detection if it fails
        
        # Add minimal detection quality metrics
        gray = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        contrast = np.std(gray)
        
        detection_results["detection_quality"] = {
            "brightness": float(brightness),
            "contrast": float(contrast),
            "essential_landmarks_count": len(detection_results["essential_landmarks"]),
            "total_confidence": detection_results["confidence"]
        }
        
        # Add minimal confidence overlay to frame (purple text)
        cv2.putText(annotated_frame, f'Confidence: {detection_results["confidence"]:.1%}', 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.brand_color, 2)
        cv2.putText(annotated_frame, f'Best: {self.best_confidence:.1%}', 
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.brand_color, 2)
        
        return detection_results
    
    def reset(self):
        """Reset detection state"""
        self.frame_count = 0
        self.best_confidence = 0.0
        self.best_frame = None
    
    def get_best_frame(self):
        """Get the best frame captured so far"""
        return self.best_frame, self.best_confidence 