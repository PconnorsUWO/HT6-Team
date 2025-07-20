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
        self.brand_color = (255, 0, 255)
        
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
        
        # Define full body validation landmarks (head to toe)
        self.full_body_landmarks = {
            # Head
            'nose': mp.solutions.pose.PoseLandmark.NOSE,
            'left_ear': mp.solutions.pose.PoseLandmark.LEFT_EAR,
            'right_ear': mp.solutions.pose.PoseLandmark.RIGHT_EAR,
            
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
        
    def validate_full_body_visibility(self, landmarks) -> Dict:
        """
        Validate that the entire body is visible in the frame
        Returns validation result with detailed feedback
        """
        if not landmarks:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "missing_parts": ["all"],
                "feedback": "No body landmarks detected",
                "body_coverage": 0.0
            }
        
        height, width = landmarks.shape[:2] if hasattr(landmarks, 'shape') else (1, 1)
        
        # Track visible landmarks and their positions
        visible_landmarks = {}
        missing_parts = []
        
        for part_name, landmark_id in self.full_body_landmarks.items():
            if landmark_id < len(landmarks.landmark):
                landmark = landmarks.landmark[landmark_id]
                if landmark.visibility > 0.3:  # Landmark is visible
                    visible_landmarks[part_name] = {
                        "x": landmark.x,
                        "y": landmark.y,
                        "visibility": landmark.visibility
                    }
                else:
                    missing_parts.append(part_name)
            else:
                missing_parts.append(part_name)
        
        # Calculate body coverage metrics
        if not visible_landmarks:
            return {
                "is_valid": False,
                "confidence": 0.0,
                "missing_parts": missing_parts,
                "feedback": "No visible body parts detected",
                "body_coverage": 0.0
            }
        
        # Check for essential body regions
        regions = {
            "head": ["nose", "left_ear", "right_ear"],
            "torso": ["left_shoulder", "right_shoulder", "left_hip", "right_hip"],
            "arms": ["left_elbow", "right_elbow", "left_wrist", "right_wrist"],
            "legs": ["left_knee", "right_knee", "left_ankle", "right_ankle"]
        }
        
        region_coverage = {}
        for region, parts in regions.items():
            visible_parts = [p for p in parts if p in visible_landmarks]
            region_coverage[region] = len(visible_parts) / len(parts)
        
        # Calculate overall body coverage
        total_parts = len(self.full_body_landmarks)
        visible_parts = len(visible_landmarks)
        body_coverage = visible_parts / total_parts
        
        # Check body positioning and size
        positioning_score = self._check_body_positioning(visible_landmarks, width, height)
        
        # Calculate final validation score
        validation_score = (
            body_coverage * 0.4 +           # 40% weight for body coverage
            positioning_score * 0.4 +       # 40% weight for positioning
            min(region_coverage.values()) * 0.2  # 20% weight for minimum region coverage
        )
        
        # MUCH STRICTER validation - require ALL critical body parts
        critical_parts = ["nose", "left_ankle", "right_ankle"]  # Head and feet must be visible
        critical_visible = all(part in visible_landmarks for part in critical_parts)
        
        # Determine if validation passes
        is_valid = (
            body_coverage >= 0.8 and        # At least 80% of body parts visible (increased from 70%)
            positioning_score >= 0.7 and    # Better positioning required (increased from 0.6)
            min(region_coverage.values()) >= 0.6 and  # At least 60% of each region visible (increased from 0.5)
            critical_visible and            # Head and feet must be visible
            region_coverage["legs"] >= 0.8  # Legs must be mostly visible (ankles detected)
        )
        
        # Generate feedback
        feedback = self._generate_validation_feedback(
            is_valid, body_coverage, region_coverage, missing_parts, positioning_score
        )
        
        return {
            "is_valid": is_valid,
            "confidence": validation_score,
            "missing_parts": missing_parts,
            "feedback": feedback,
            "body_coverage": body_coverage,
            "region_coverage": region_coverage,
            "positioning_score": positioning_score,
            "visible_landmarks": visible_landmarks
        }
    
    def _check_body_positioning(self, visible_landmarks: Dict, frame_width: int, frame_height: int) -> float:
        """Check if body is properly positioned in the frame"""
        if not visible_landmarks:
            return 0.0
        
        # Get bounding box of visible landmarks
        x_coords = [landmark["x"] for landmark in visible_landmarks.values()]
        y_coords = [landmark["y"] for landmark in visible_landmarks.values()]
        
        if not x_coords or not y_coords:
            return 0.0
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        # Calculate body dimensions relative to frame
        body_width = max_x - min_x
        body_height = max_y - min_y
        body_center_x = (min_x + max_x) / 2
        body_center_y = (min_y + max_y) / 2
        
        # Check if body is centered horizontally (within 20% of center)
        horizontal_centering = 1.0 - min(abs(body_center_x - 0.5) / 0.2, 1.0)
        
        # Check if body fills appropriate portion of frame height (not too small, not too large)
        # For full body, should be between 50% and 80% of frame height (stricter - person must be further away)
        if 0.5 <= body_height <= 0.8:
            size_score = 1.0
        elif 0.4 <= body_height <= 0.85:
            size_score = 0.5
        else:
            size_score = 0.0  # Reject if too close or too far
        
        # Check if body is not cut off at top or bottom
        margin_score = 1.0
        if min_y < 0.05:  # Too close to top
            margin_score -= 0.3
        if max_y > 0.95:  # Too close to bottom
            margin_score -= 0.3
        
        # Check aspect ratio (body should be taller than wide)
        aspect_ratio = body_height / body_width if body_width > 0 else 0
        if 1.5 <= aspect_ratio <= 3.0:
            aspect_score = 1.0
        elif 1.2 <= aspect_ratio <= 4.0:
            aspect_score = 0.7
        else:
            aspect_score = 0.3
        
        # Calculate final positioning score
        positioning_score = (
            horizontal_centering * 0.3 +
            size_score * 0.3 +
            margin_score * 0.2 +
            aspect_score * 0.2
        )
        
        return positioning_score
    
    def _generate_validation_feedback(self, is_valid: bool, body_coverage: float, 
                                    region_coverage: Dict, missing_parts: List[str], 
                                    positioning_score: float) -> str:
        """Generate user-friendly feedback for validation results"""
        if is_valid:
            return "Perfect! Your entire body is visible and well-positioned for virtual try-on."
        
        feedback_parts = []
        
        # Body coverage feedback
        if body_coverage < 0.7:
            coverage_percent = int(body_coverage * 100)
            feedback_parts.append(f"Only {coverage_percent}% of your body is visible")
        
        # Missing regions feedback
        low_coverage_regions = [region for region, coverage in region_coverage.items() if coverage < 0.5]
        if low_coverage_regions:
            feedback_parts.append(f"Missing: {', '.join(low_coverage_regions)}")
        
        # Positioning feedback
        if positioning_score < 0.7:
            if positioning_score < 0.3:
                feedback_parts.append("Move 8-12 feet from camera for full body view")
            elif positioning_score < 0.5:
                feedback_parts.append("Move 6-8 feet from camera")
            else:
                feedback_parts.append("Center yourself in the frame")
        
        # Specific missing parts feedback
        if len(missing_parts) > 0:
            critical_missing = [part for part in missing_parts if part in ["nose", "left_ankle", "right_ankle"]]
            if critical_missing:
                feedback_parts.append(f"Ensure {', '.join(critical_missing)} are visible")
        
        # Legs visibility feedback
        if region_coverage.get("legs", 0) < 0.8:
            feedback_parts.append("Your feet/ankles must be visible - move further from camera")
        
        if not feedback_parts:
            feedback_parts.append("Please ensure your entire body is visible in the frame")
        
        return " • ".join(feedback_parts)
        
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
            "essential_landmarks": [],
            "full_body_validation": None
        }
        
        # MediaPipe Pose Detection - only essential parts
        try:
            pose_results = self.mp_pose.process(frame_rgb)
            if pose_results.pose_landmarks:
                # Calculate confidence based on essential parts only
                confidence = self.calculate_essential_confidence(pose_results.pose_landmarks)
                detection_results["confidence"] = confidence
                
                # Perform full body validation
                full_body_validation = self.validate_full_body_visibility(pose_results.pose_landmarks)
                detection_results["full_body_validation"] = full_body_validation
                
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
        
        # Add validation status overlay to frame
        if detection_results["full_body_validation"]:
            validation = detection_results["full_body_validation"]
            status_color = (0, 255, 0) if validation["is_valid"] else (0, 0, 255)  # Green if valid, red if not
            status_text = "✓ Full Body" if validation["is_valid"] else "✗ Partial Body"
            
            cv2.putText(annotated_frame, status_text, 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, status_color, 2)
            cv2.putText(annotated_frame, f'Coverage: {validation["body_coverage"]:.1%}', 
                       (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.brand_color, 2)
            cv2.putText(annotated_frame, f'Position: {validation["positioning_score"]:.1%}', 
                       (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.brand_color, 2)
        else:
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