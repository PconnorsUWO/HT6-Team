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

def calculate_detection_quality(frame, faces, bodies):
    """Calculate additional quality metrics for stricter detection"""
    height, width = frame.shape[:2]
    
    # Check if detections are reasonably sized (not too small or too large)
    quality_score = 0.0
    
    # Face quality checks
    for (x, y, w, h) in faces:
        face_area = w * h
        frame_area = width * height
        face_ratio = face_area / frame_area
        
        # Face should be between 0.5% and 15% of frame area
        if 0.005 <= face_ratio <= 0.15:
            quality_score += 0.2
        elif 0.001 <= face_ratio <= 0.25:
            quality_score += 0.1
        
        # Check face aspect ratio (should be roughly square-ish)
        aspect_ratio = w / h
        if 0.7 <= aspect_ratio <= 1.3:
            quality_score += 0.1
    
    # Body quality checks
    for (x, y, w, h) in bodies:
        body_area = w * h
        frame_area = width * height
        body_ratio = body_area / frame_area
        
        # Body should be between 5% and 50% of frame area
        if 0.05 <= body_ratio <= 0.5:
            quality_score += 0.3
        elif 0.02 <= body_ratio <= 0.7:
            quality_score += 0.15
        
        # Check body aspect ratio (should be taller than wide)
        aspect_ratio = h / w
        if 1.5 <= aspect_ratio <= 4.0:
            quality_score += 0.2
    
    # Check for reasonable positioning (not at edges)
    for (x, y, w, h) in faces + bodies:
        center_x = x + w/2
        center_y = y + h/2
        
        # Should be in central area (not too close to edges)
        if 0.1 <= center_x/width <= 0.9 and 0.1 <= center_y/height <= 0.9:
            quality_score += 0.1
    
    return min(quality_score, 1.0)

def validate_full_body_visibility_opencv(frame, faces, bodies):
    """Validate that the entire body is visible using OpenCV detections"""
    height, width = frame.shape[:2]
    
    # Check if we have both face and body detections
    has_face = len(faces) > 0
    has_body = len(bodies) > 0
    
    if not has_face or not has_body:
        return {
            "is_valid": False,
            "confidence": 0.0,
            "missing_parts": ["face" if not has_face else "", "body" if not has_body else ""],
            "feedback": "Missing face or body detection",
            "body_coverage": 0.0,
            "region_coverage": {"head": 0.0, "torso": 0.0, "arms": 0.0, "legs": 0.0},
            "positioning_score": 0.0
        }
    
    # Get the largest face and body detections
    largest_face = max(faces, key=lambda f: f[2] * f[3]) if faces else None
    largest_body = max(bodies, key=lambda b: b[2] * b[3]) if bodies else None
    
    if not largest_face or not largest_body:
        return {
            "is_valid": False,
            "confidence": 0.0,
            "missing_parts": ["face", "body"],
            "feedback": "No valid face or body detection",
            "body_coverage": 0.0,
            "region_coverage": {"head": 0.0, "torso": 0.0, "arms": 0.0, "legs": 0.0},
            "positioning_score": 0.0
        }
    
    fx, fy, fw, fh = largest_face
    bx, by, bw, bh = largest_body
    
    # Calculate body coverage (how much of the frame the body occupies)
    body_area = bw * bh
    frame_area = width * height
    body_coverage = body_area / frame_area
    
    # Check if body is properly sized (should be between 20% and 60% of frame)
    if 0.2 <= body_coverage <= 0.6:
        size_score = 1.0
    elif 0.15 <= body_coverage <= 0.7:
        size_score = 0.7
    else:
        size_score = 0.3
    
    # Check body positioning (should be centered and not cut off)
    body_center_x = bx + bw/2
    body_center_y = by + bh/2
    
    # Horizontal centering (within 20% of center)
    horizontal_centering = 1.0 - min(abs(body_center_x/width - 0.5) / 0.2, 1.0)
    
    # Check if body is not cut off at top or bottom
    margin_score = 1.0
    if by < height * 0.05:  # Too close to top
        margin_score -= 0.3
    if by + bh > height * 0.95:  # Too close to bottom
        margin_score -= 0.3
    
    # Check aspect ratio (body should be taller than wide)
    aspect_ratio = bh / bw if bw > 0 else 0
    if 1.5 <= aspect_ratio <= 3.0:
        aspect_score = 1.0
    elif 1.2 <= aspect_ratio <= 4.0:
        aspect_score = 0.7
    else:
        aspect_score = 0.3
    
    # Calculate positioning score
    positioning_score = (
        horizontal_centering * 0.3 +
        size_score * 0.3 +
        margin_score * 0.2 +
        aspect_score * 0.2
    )
    
    # Estimate region coverage based on body detection
    # This is a simplified estimation since OpenCV doesn't provide detailed landmarks
    region_coverage = {
        "head": 1.0 if has_face else 0.0,
        "torso": 0.8 if has_body else 0.0,  # Assume torso is mostly visible if body detected
        "arms": 0.6 if has_body else 0.0,   # Assume arms are partially visible
        "legs": 0.7 if has_body else 0.0    # Assume legs are mostly visible
    }
    
    # Calculate overall validation score
    validation_score = (
        body_coverage * 0.4 +
        positioning_score * 0.4 +
        min(region_coverage.values()) * 0.2
    )
    
    # Determine if validation passes
    is_valid = (
        body_coverage >= 0.2 and           # At least 20% of frame covered by body
        positioning_score >= 0.6 and       # Good positioning
        has_face and has_body and          # Both face and body detected
        min(region_coverage.values()) >= 0.5  # At least 50% of each region estimated visible
    )
    
    # Generate feedback
    feedback_parts = []
    if not is_valid:
        if body_coverage < 0.2:
            feedback_parts.append("Move closer to camera for full body view")
        if positioning_score < 0.6:
            feedback_parts.append("Center yourself in the frame")
        if not has_face:
            feedback_parts.append("Ensure your face is visible")
        if not has_body:
            feedback_parts.append("Ensure your entire body is visible")
    
    feedback = " • ".join(feedback_parts) if feedback_parts else "Perfect! Your entire body is visible and well-positioned."
    
    return {
        "is_valid": is_valid,
        "confidence": validation_score,
        "missing_parts": [] if has_face and has_body else ["face" if not has_face else "", "body" if not has_body else ""],
        "feedback": feedback,
        "body_coverage": body_coverage,
        "region_coverage": region_coverage,
        "positioning_score": positioning_score
    }

def detect_body_pose_in_video(video_path: str) -> dict:
    """
    Detect body pose in video using OpenCV with STRICT detection criteria
    where a person is clearly visible with annotations
    """
    try:
        print(f"Processing video for STRICT body detection: {video_path}")
        
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
        
        # Load multiple pre-trained models for stricter detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        face_alt_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_alt.xml')
        body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_fullbody.xml')
        upper_body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_upperbody.xml')
        
        # Process every 3rd frame for more thorough analysis
        frame_skip = 3
        processed_frames = 0
        total_frames_analyzed = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            processed_frames += 1
            
            # Skip frames to speed up processing
            if processed_frames % frame_skip != 0:
                continue
            
            total_frames_analyzed += 1
            
            # Convert to grayscale for detection
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply histogram equalization for better detection
            gray = cv2.equalizeHist(gray)
            
            # STRICT detection with multiple cascades and parameters
            # Face detection with multiple cascades
            faces1 = face_cascade.detectMultiScale(gray, 1.05, 6, minSize=(30, 30))
            faces2 = face_alt_cascade.detectMultiScale(gray, 1.05, 6, minSize=(30, 30))
            
            # Combine and deduplicate face detections
            all_faces = list(faces1) + list(faces2)
            faces = []
            for face in all_faces:
                # Remove duplicates (faces that are too close to each other)
                is_duplicate = False
                for existing_face in faces:
                    x1, y1, w1, h1 = face
                    x2, y2, w2, h2 = existing_face
                    center_dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
                    if center_dist < min(w1, w2) * 0.5:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    faces.append(face)
            
            # Body detection with multiple cascades
            bodies = body_cascade.detectMultiScale(gray, 1.05, 6, minSize=(50, 100))
            upper_bodies = upper_body_cascade.detectMultiScale(gray, 1.05, 6, minSize=(50, 50))
            
            # Combine body detections
            all_bodies = list(bodies) + list(upper_bodies)
            bodies = []
            for body in all_bodies:
                # Remove duplicates
                is_duplicate = False
                for existing_body in bodies:
                    x1, y1, w1, h1 = body
                    x2, y2, w2, h2 = existing_body
                    center_dist = np.sqrt((x1-x2)**2 + (y1-y2)**2)
                    if center_dist < min(w1, w2) * 0.7:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    bodies.append(body)
            
            # STRICT confidence calculation
            face_confidence = len(faces) * 0.25  # Reduced from 0.3 - each face adds 25% confidence
            body_confidence = len(bodies) * 0.5   # Reduced from 0.7 - each body adds 50% confidence
            
            # Require BOTH face AND body for high confidence
            if len(faces) == 0 or len(bodies) == 0:
                total_confidence = min(face_confidence + body_confidence, 0.3)  # Cap at 30% if missing either
            else:
                total_confidence = min(face_confidence + body_confidence, 1.0)
            
            # Additional quality checks
            quality_score = calculate_detection_quality(frame, faces, bodies)
            
            # Full body validation
            full_body_validation = validate_full_body_visibility_opencv(frame, faces, bodies)
            
            # Calculate frame quality metrics
            brightness = np.mean(gray)
            contrast = np.std(gray)
            
            # Stricter brightness requirements (not too dark, not too bright)
            if 40 <= brightness <= 200:
                brightness_confidence = 0.15
            elif 20 <= brightness <= 220:
                brightness_confidence = 0.08
            else:
                brightness_confidence = 0.0
            
            # Stricter contrast requirements
            if contrast >= 30:
                contrast_confidence = 0.1
            elif contrast >= 20:
                contrast_confidence = 0.05
            else:
                contrast_confidence = 0.0
            
            # Calculate final confidence with stricter requirements
            final_confidence = (
                total_confidence * 0.6 +  # Detection confidence (60% weight)
                quality_score * 0.25 +    # Quality score (25% weight)
                brightness_confidence +   # Brightness (15% weight)
                contrast_confidence       # Contrast (10% weight)
            )
            
            # MUCH STRICTER threshold - require 70% confidence minimum AND full body validation
            if (final_confidence > best_confidence and 
                final_confidence >= 0.7 and 
                full_body_validation["is_valid"]):
                best_confidence = final_confidence
                best_frame = frame.copy()
                best_frame_number = processed_frames
                
                # Create detailed annotations for the best frame
                annotated_frame = frame.copy()
                annotations = {
                    "faces": [],
                    "bodies": [],
                    "detection_quality": {
                        "face_confidence": face_confidence,
                        "body_confidence": body_confidence,
                        "quality_score": quality_score,
                        "brightness_confidence": brightness_confidence,
                        "contrast_confidence": contrast_confidence,
                        "total_confidence": final_confidence,
                        "brightness": brightness,
                        "contrast": contrast
                    },
                    "full_body_validation": full_body_validation
                }
                
                # Draw face annotations with confidence
                for i, (x, y, w, h) in enumerate(faces):
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(annotated_frame, f'Face {i+1}', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                    annotations["faces"].append({
                        "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                        "area_ratio": (w * h) / (frame.shape[0] * frame.shape[1])
                    })
                
                # Draw body annotations with confidence
                for i, (x, y, w, h) in enumerate(bodies):
                    cv2.rectangle(annotated_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    cv2.putText(annotated_frame, f'Body {i+1}', (x, y-10), 
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                    annotations["bodies"].append({
                        "x": int(x), "y": int(y), "width": int(w), "height": int(h),
                        "area_ratio": (w * h) / (frame.shape[0] * frame.shape[1])
                    })
                
                # Add detailed confidence information
                cv2.putText(annotated_frame, f'STRICT Confidence: {final_confidence:.1%}', 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f'Faces: {len(faces)}, Bodies: {len(bodies)}', 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f'Quality: {quality_score:.2f}, Bright: {brightness:.0f}', 
                           (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                cv2.putText(annotated_frame, f'Frame: {processed_frames}/{frame_count}', 
                           (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                best_annotations = annotations
                print(f"STRICT: New best frame found: frame {processed_frames}, confidence: {final_confidence:.1%}")
                print(f"  - Faces: {len(faces)}, Bodies: {len(bodies)}, Quality: {quality_score:.2f}")
                print(f"  - Brightness: {brightness:.0f}, Contrast: {contrast:.0f}")
        
        cap.release()
        
        print(f"STRICT detection completed. Analyzed {total_frames_analyzed} frames.")
        
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
                "message": f"Person detected with STRICT {best_confidence:.1%} confidence",
                "detection_mode": "strict"
            }
        else:
            return {
                "success": False,
                "message": "No suitable frame found with STRICT detection criteria (minimum 70% confidence required)",
                "detection_mode": "strict"
            }
            
    except Exception as e:
        print(f"Error in STRICT body detection: {str(e)}")
        return {
            "success": False,
            "message": f"Error processing video: {str(e)}",
            "detection_mode": "strict"
        } 