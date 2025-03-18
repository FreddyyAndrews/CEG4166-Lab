import cv2
import numpy as np

def preprocess_image(image):
    """Apply preprocessing to improve face detection and recognition"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply histogram equalization to enhance contrast
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise (using smaller kernel for better detail preservation)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    return gray

def run_face_recognition():
    """
    Run real-time face recognition using webcam
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
    
    # Set up camera
    cap = cv2.VideoCapture(0)
    
    # Check if camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
    
    # Set camera resolution for better performance
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    # Create a named window that can be resized by the user
    cv2.namedWindow('Face Recognition', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Face Recognition', 800, 600)
    
    print("Press 'q' to quit")
    
    # For improved performance, we'll keep track of faces across frames
    face_memory = None
    face_name_memory = None
    memory_decay = 0
    
    # Confidence history for smoothing predictions
    confidence_history = {1: [], 2: [], 3: []}
    prediction_history = []
    history_max_size = 5
    
    # Mouad-specific confidence boost
    mouad_confidence_boost = 15  # Add this percentage to Mouad's confidence
    
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        if not ret:
            print("Error: Failed to capture image from camera.")
            break
        
        # Create a copy for drawing results
        display_frame = frame.copy()
        
        # Preprocess the frame for face detection
        preprocessed = preprocess_image(frame)
        
        # Progressive face detection parameters to try
        detection_params = [
            {'scaleFactor': 1.1, 'minNeighbors': 6, 'minSize': (60, 60)},  # Balanced
            {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (50, 50)},  # Less strict
            {'scaleFactor': 1.2, 'minNeighbors': 3, 'minSize': (40, 40)}   # Very lenient
        ]
        
        # Try different detection parameters
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
        
        # If no faces detected but we have memory, use it
        if len(faces) == 0 and face_memory is not None and memory_decay < 5:
            faces = [face_memory]
            memory_decay += 1
            # Add a fading effect to indicate memory use
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (0, 0), (display_frame.shape[1], display_frame.shape[0]), 
                         (0, 0, 200), -1)
            alpha = 0.1 + (memory_decay * 0.02)
            cv2.addWeighted(overlay, alpha, display_frame, 1 - alpha, 0, display_frame)
            
            if face_name_memory:
                cv2.putText(display_frame, "Using memory: " + face_name_memory, 
                          (10, display_frame.shape[0] - 20), 
                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        elif len(faces) > 0:
            # Reset memory decay if we detected a face
            memory_decay = 0
        
        # Process each detected face
        for i, (x, y, w, h) in enumerate(faces):
            # Store the latest face in memory
            if i == 0:  # Only remember the first (hopefully main) face
                face_memory = (x, y, w, h)
            
            # Get the face region
            face_roi = preprocessed[y:y+h, x:x+w]
            
            # Resize to match training size
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Try multiple predictions with slightly different preprocessing to improve robustness
            all_predictions = []
            
            # Original image prediction
            label, confidence = recognizer.predict(face_roi)
            all_predictions.append((label, confidence))
            
            # Additional predictions with slight modifications
            # Try with different brightness levels
            for alpha in [0.95, 1.05]:  # Contrast
                for beta in [-3, 3]:    # Brightness
                    modified_face = cv2.convertScaleAbs(face_roi.copy(), alpha=alpha, beta=beta)
                    label_mod, confidence_mod = recognizer.predict(modified_face)
                    all_predictions.append((label_mod, confidence_mod))
            
            # Find the prediction with highest confidence (lowest distance value in LBPH)
            best_prediction = min(all_predictions, key=lambda x: x[1])
            label, confidence = best_prediction
            
            # Convert confidence to percentage (lower values mean better match in LBPH)
            confidence_percentage = round(100 - min(100, confidence), 2)
            
            # Apply Mouad-specific confidence boost if predicted as Mouad
            if label == 3:  # Mouad's ID
                confidence_percentage += mouad_confidence_boost
                confidence_percentage = min(confidence_percentage, 95)  # Cap at 95%
            
            # Track confidence for each person
            for person_id in names.keys():
                # If this is the predicted person, add the confidence
                # Otherwise, add a zero (no confidence for this person)
                if person_id == label:
                    confidence_history[person_id].append(confidence_percentage)
                else:
                    confidence_history[person_id].append(0)
                
                # Keep history limited to the max size
                if len(confidence_history[person_id]) > history_max_size:
                    confidence_history[person_id].pop(0)
            
            # Track predicted labels
            prediction_history.append(label)
            if len(prediction_history) > history_max_size:
                prediction_history.pop(0)
            
            # Get the most common prediction in history
            if prediction_history:
                # Count occurrences of each label in history
                label_counts = {}
                for l in prediction_history:
                    if l in label_counts:
                        label_counts[l] += 1
                    else:
                        label_counts[l] = 1
                
                # Find the most frequent label and its count
                most_common_label = max(label_counts, key=label_counts.get)
                most_common_count = label_counts[most_common_label]
                
                # Calculate average confidence for the most common label
                avg_confidence = 0
                if most_common_label in confidence_history:
                    values = confidence_history[most_common_label]
                    if values:
                        avg_confidence = sum(values) / len(values)
                
                # If the most common prediction is consistent and has decent average confidence
                if most_common_count >= 3 and avg_confidence > 10:
                    label = most_common_label
                    confidence_percentage = avg_confidence
            
            # Special handling for Mouad with low confidence
            # If another person is detected with low confidence, check if Mouad might be a better match
            if label != 3 and confidence_percentage < 25:  # Not Mouad and low confidence
                # Check Mouad's history
                mouad_values = confidence_history[3]
                if mouad_values and max(mouad_values) > 0:  # If Mouad has been detected recently
                    # There's a chance this might be Mouad with low confidence
                    # Try predicting with a Mouad-specific adjustment to the face
                    face_roi_enhanced = cv2.convertScaleAbs(face_roi.copy(), alpha=1.15, beta=5)
                    label_mouad, confidence_mouad = recognizer.predict(face_roi_enhanced)
                    confidence_percentage_mouad = round(100 - min(100, confidence_mouad), 2) + mouad_confidence_boost
                    
                    # If Mouad's confidence is reasonable, use it
                    if label_mouad == 3 and confidence_percentage_mouad > 25:
                        label = 3
                        confidence_percentage = confidence_percentage_mouad
            
            # Get the name based on label
            name = names.get(label, "Unknown")
            
            # Store the latest face name in memory (only if confidence is decent or we have consistent predictions)
            if confidence_percentage > 10:
                face_name_memory = name
            
            # Prepare confidence text with appropriate color coding
            confidence_color = (0, 0, 0)  # Black by default
            
            # Adjust thresholds for Mouad specifically
            if name == "Mouad":
                if confidence_percentage < 15:
                    confidence_text = "Low"
                    background_color = (0, 165, 255)  # Orange for low confidence
                elif confidence_percentage < 35:
                    confidence_text = "Medium"
                    background_color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    confidence_text = "High"
                    background_color = (0, 255, 0)    # Green for high confidence
            else:
                # Standard thresholds for other people
                if confidence_percentage < 20:
                    confidence_text = "Low"
                    background_color = (0, 165, 255)  # Orange for low confidence
                elif confidence_percentage < 40:
                    confidence_text = "Medium"
                    background_color = (0, 255, 255)  # Yellow for medium confidence
                else:
                    confidence_text = "High"
                    background_color = (0, 255, 0)    # Green for high confidence
            
            # Always show a prediction, with confidence indicator
            display_text = f"{name} ({confidence_text})"
            
            # Draw a rectangle around the face
            cv2.rectangle(display_frame, (x, y), (x+w, y+h), background_color, 2)
            
            # Add a background for text to make it more readable
            text_size = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(display_frame, (x, y-text_size[1]-10), (x+text_size[0]+10, y), background_color, -1)
            
            # Draw text
            cv2.putText(display_frame, display_text, (x+5, y-5), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.7, confidence_color, 2)
            
            # Add small confidence percentage at the bottom of the box
            conf_text = f"{confidence_percentage:.1f}%"
            cv2.putText(display_frame, conf_text, (x+5, y+h+15), 
                      cv2.FONT_HERSHEY_SIMPLEX, 0.5, background_color, 1)
        
        # Display the resulting frame
        cv2.imshow('Face Recognition', display_frame)
        
        # Exit on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_face_recognition()
