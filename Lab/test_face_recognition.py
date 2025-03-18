import cv2
import sys
import os
import numpy as np
import re

def preprocess_image(image):
    """Apply preprocessing to improve face detection and recognition"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply histogram equalization
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise (smaller kernel preserves more details)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    return gray

def test_face_recognition(image_path):
    """
    Test face recognition on a specified image file
    
    Args:
        image_path: Path to the image file to test
    """
    # Check if the image file exists
    if not os.path.exists(image_path):
        print(f"Error: Image file '{image_path}' does not exist.")
        return
    
    # Load the face detection cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Load the face recognizer
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    try:
        recognizer.read('trained_model.yml')
    except:
        print("Error: Could not load the trained model file 'trained_model.yml'.")
        return
    
    # Map labels to names
    names = {
        1: "Frederick",
        2: "Josué",
        3: "Mouad"
    }
    
    # Try to identify the person from the filename pattern
    true_label = None
    if 'train_set' in image_path:
        # Check for directory pattern train_set/NUMBER/
        match = re.search(r'train_set[\\/]([123])[\\/]', image_path)
        if match:
            person_id = int(match.group(1))
            true_label = person_id
            print(f"This image is from the training set, belongs to person {names[person_id]}")
    
    # Read the input image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image from '{image_path}'.")
        return
    
    # Create a copy for drawing results
    result_image = image.copy()
    
    # Preprocess image for face detection
    preprocessed = preprocess_image(image)
    
    # List of detection parameters to try sequentially
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
    
    if len(faces) == 0:
        print("No faces detected in the image.")
        
        # For images in the training set with known labels, we can still show the ID
        if true_label is not None:
            display_text = f"{names[true_label]} (from filename)"
            height, width = image.shape[:2]
            cv2.putText(image, display_text, (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            
        cv2.namedWindow('Face Recognition Result', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Face Recognition Result', 640, 480)
        cv2.imshow('Face Recognition Result', image)
        print("Could not detect any faces in the image with any parameters.")
    else:
        print(f"Found {len(faces)} face(s) in the image")
        
        # Process each detected face
        for (x, y, w, h) in faces:
            # Get the face region
            face_roi = preprocessed[y:y+h, x:x+w]
            
            # Resize to match training size
            face_roi = cv2.resize(face_roi, (100, 100))
            
            # Predict the identity
            label, confidence = recognizer.predict(face_roi)
            
            # Convert confidence to percentage (lower values mean better match in LBPH)
            confidence_percentage = round(100 - min(100, confidence), 2)
            
            # Get the name based on label
            name = names.get(label, "Unknown")
            
            # Determine confidence level text and color
            if confidence_percentage < 20:
                confidence_text = "Low"
                color = (0, 165, 255)  # Orange for low confidence
            elif confidence_percentage < 40:
                confidence_text = "Medium"
                color = (0, 255, 255)  # Yellow for medium confidence
            else:
                confidence_text = "High"
                color = (0, 255, 0)    # Green for high confidence
            
            # For images in train_set with known labels, use that information
            if true_label is not None:
                true_name = names[true_label]
                display_text = f"{name} ({confidence_text}: {confidence_percentage:.1f}%)"
                
                # If confidence is low and we know the true label, add that info
                if confidence_percentage < 20 or name != true_name:
                    display_text += f" | Should be: {true_name}"
            else:
                display_text = f"{name} ({confidence_text}: {confidence_percentage:.1f}%)"
                
            print(f"Detected: {display_text}")
            
            # Draw rectangle with appropriate color
            cv2.rectangle(result_image, (x, y), (x+w, y+h), color, 3)
            
            # Add a background for text to make it more readable
            text_size = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            cv2.rectangle(result_image, (x, y-text_size[1]-10), (x+text_size[0]+10, y), (0, 0, 0), -1)
            
            # Draw text with improved visibility
            cv2.putText(result_image, display_text, (x+5, y-5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # If we know the true label and it's different, add explanation
            if true_label is not None and name != names[true_label]:
                explanation = f"Low confidence detection. This is actually {names[true_label]}"
                cv2.putText(result_image, explanation, (10, result_image.shape[0]-20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        # Create a named window that can be resized
        cv2.namedWindow('Face Recognition Result', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Face Recognition Result', 640, 480)  # Fixed size window
        cv2.imshow('Face Recognition Result', result_image)
    
    # Wait for a key press
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python test_face_recognition.py <image_path>")
    else:
        test_face_recognition(sys.argv[1]) 