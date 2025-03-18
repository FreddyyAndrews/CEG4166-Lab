import os
os.environ["DISPLAY"] = ":0"  # Ensure X server is accessible
os.environ["QT_QPA_PLATFORM"] = "xcb"
import cv2
import numpy as np
from picamera2 import Picamera2

def preprocess_image(image):
    """Apply preprocessing to improve face detection and recognition"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply histogram equalization to enhance contrast
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise (using a smaller kernel for better detail preservation)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    return gray

def run_face_recognition():
    """
    Run real-time face recognition using the Pi Camera via picamera2.
    """
    # Load the Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load the face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read('trained_model.yml')
    except:
        print("Error: Could not load the trained model. Make sure 'trained_model.yml' exists.")
        return
    
    # Map labels to names
    names = {
        1: "Frederick",
        2: "Josué",
        3: "Mouad"
    }

    # Create a named window that can be resized by the user
    cv2.namedWindow('Face Recognition', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Face Recognition', 800, 600)
    
    # Initialize the Pi Camera using picamera2
    picam2 = Picamera2()
    # Configure for a preview with BGR output at 640x480 resolution
    config = picam2.create_preview_configuration(main={"format": "BGR888", "size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    
    print("Press 'q' to quit")
    
    # Variables for face tracking
    face_memory = None
    face_name_memory = None
    memory_decay = 0
    
    # Confidence history for smoothing predictions
    confidence_history = {1: [], 2: [], 3: []}
    prediction_history = []
    history_max_size = 5
    
    while True:
        # Capture frame from picamera2
        frame = picam2.capture_array()
        if frame is None:
            print("Error: Failed to capture image from camera.")
            break
        
        # Create a copy for drawing results
        display_frame = frame.copy()
        
        # Preprocess the frame for face detection
        preprocessed = preprocess_image(frame)
        
        # Try different detection parameters progressively
        detection_params = [
            {'scaleFactor': 1.1, 'minNeighbors': 6, 'minSize': (60, 60)},  # Balanced
            {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (50, 50)},  # Less strict
            {'scaleFactor': 1.2, 'minNeighbors': 3, 'minSize': (40, 40)}   # Very lenient
        ]
        
        faces = []
        for params in detection_params:
            faces = face_cascade.detectMultiScale(
                preprocessed,
                scaleFactor=params['scaleFactor'],
                minNeighbors=params['minNeighbors'],
                minSize=params['minSize'],
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            if len(faces) > 0:
                break
        
        # Use previous face memory if no face is detected
        if len(faces) == 0 and face_memory is not None and memory_decay < 5:
            faces = [face_memory]
            memory_decay += 1
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (0, 0), (display_frame.shape[1], display_frame.shape[0]), (0, 0, 200), -1)
            alpha = 0.1 + (memory_decay * 0.02)
            cv2.addWeighted(overlay, alpha, display_frame, 1 - alpha, 0, display_frame)
            
            if face_name_memory:
                cv2.putText(display_frame, "Using memory: " + face_name_memory, 
                            (10, display_frame.shape[0] - 20), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif len(faces) > 0:
            memory_decay = 0
        
        # Process each detected face
        for i, (x, y, w, h) in enumerate(faces):
            if i == 0:  # Remember only the first face
                face_memory = (x, y, w, h)
            
            face_roi = preprocessed[y:y+h, x:x+w]
            face_roi = cv2.resize(face_roi, (100, 100))
            
            all_predictions = []
            # Original image prediction
            label, confidence = recognizer.predict(face_roi)
            all_predictions.append((label, confidence))
            
            # Additional predictions with slight brightness modifications
            for alpha in [0.95, 1.05]:
                for beta in [-3, 3]:
                    modified_face = cv2.convertScaleAbs(face_roi.copy(), alpha=alpha, beta=beta)
                    label_mod, confidence_mod = recognizer.predict(modified_face)
                    all_predictions.append((label_mod, confidence_mod))
            
            best_prediction = min(all_predictions, key=lambda x: x[1])
            label, confidence = best_prediction
            confidence_percentage = round(100 - min(100, confidence), 2)
            
            # Update confidence history
            for person_id in names.keys():
                if person_id == label:
                    confidence_history[person_id].append(confidence_percentage)
                else:
                    confidence_history[person_id].append(0)
                
                if len(confidence_history[person_id]) > history_max_size:
                    confidence_history[person_id].pop(0)
            
            prediction_history.append(label)
            if len(prediction_history) > history_max_size:
                prediction_history.pop(0)
            
            if prediction_history:
                label_counts = {}
                for l in prediction_history:
                    label_counts[l] = label_counts.get(l, 0) + 1
                
                most_common_label = max(label_counts, key=label_counts.get)
                most_common_count = label_counts[most_common_label]
                
                avg_confidence = 0
                if most_common_label in confidence_history:
                    values = confidence_history[most_common_label]
                    if values:
                        avg_confidence = sum(values) / len(values)
                
                if most_common_count >= 3 and avg_confidence > 10:
                    label = most_common_label
                    confidence_percentage = avg_confidence
            
            name = names.get(label, "Unknown")
            if confidence_percentage > 10:
                face_name_memory = name
            
            if confidence_percentage < 20:
                confidence_text = "Low"
                background_color = (0, 165, 255)  # Orange
            elif confidence_percentage < 40:
                confidence_text = "Medium"
                background_color = (0, 255, 255)  # Yellow
            else:
                confidence_text = "High"
                background_color = (0, 255, 0)    # Green
            
            display_text = f"{name} ({confidence_text})"
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), background_color, 2)
            
            text_size = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(display_frame, (x, y-text_size[1]-10), (x+text_size[0]+10, y), background_color, -1)
            cv2.putText(display_frame, display_text, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
            
            conf_text = f"{confidence_percentage:.1f}%"
            cv2.putText(display_frame, conf_text, (x+5, y+h+15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, background_color, 1)
        
        cv2.imshow('Face Recognition', display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    picam2.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_recognition()
