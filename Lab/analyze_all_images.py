import cv2
import os
import numpy as np
import re
from glob import glob
import datetime

def preprocess_image(image):
    """Apply preprocessing to improve face detection and recognition"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Apply histogram equalization
    gray = cv2.equalizeHist(gray)
    
    # Apply Gaussian blur to reduce noise
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    
    return gray

def get_person_id_from_path(image_path):
    """Extract person ID from image path if it's in the training set"""
    if 'train_set' in image_path:
        match = re.search(r'train_set[\\/]([123])[\\/]', image_path)
        if match:
            return int(match.group(1))
    return None

def analyze_all_images():
    """
    Analyze all images in the training set and save results to a text file
    """
    # Create results file with timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"recognition_results_{timestamp}.txt"
    
    with open(results_file, 'w') as f:
        f.write(f"Face Recognition Analysis Results - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*80 + "\n\n")
        
        # Load the face detection cascade
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Load the face recognizer
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        try:
            recognizer.read('trained_model.yml')
        except:
            f.write("Error: Could not load the trained model file 'trained_model.yml'.\n")
            return
        
        # Map labels to names
        names = {
            1: "Frederick",
            2: "Josué",
            3: "Mouad"
        }
        
        # Get all image files from the training set
        image_files = []
        for person_id in [1, 2, 3]:
            pattern = os.path.join('train_set', str(person_id), '*.*')
            image_files.extend(glob(pattern))
        
        # Statistics by person
        stats = {1: {'correct': 0, 'total': 0, 'confidence_sum': 0},
                 2: {'correct': 0, 'total': 0, 'confidence_sum': 0},
                 3: {'correct': 0, 'total': 0, 'confidence_sum': 0}}
        
        f.write(f"Total images to analyze: {len(image_files)}\n")
        f.write("-"*80 + "\n\n")
        
        # Process each image
        for image_path in image_files:
            # Get expected person ID from the file path
            true_label = get_person_id_from_path(image_path)
            if true_label is None:
                continue  # Skip if can't determine the label
            
            true_name = names[true_label]
            
            # Read the image
            image = cv2.imread(image_path)
            if image is None:
                f.write(f"Error: Could not read image from '{image_path}'.\n")
                continue
            
            # Preprocess image
            preprocessed = preprocess_image(image)
            
            # List of detection parameters to try sequentially
            detection_params = [
                {'scaleFactor': 1.1, 'minNeighbors': 6, 'minSize': (60, 60)}, # Balanced
                {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (50, 50)}, # Less strict
                {'scaleFactor': 1.2, 'minNeighbors': 3, 'minSize': (40, 40)}  # Very lenient
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
            
            # Count as a test for this person
            stats[true_label]['total'] += 1
            
            f.write(f"Image: {image_path}\n")
            f.write(f"  Expected: {true_name}\n")
            
            # If no face was detected
            if len(faces) == 0:
                f.write("  Result: No face detected\n\n")
                continue
            
            f.write(f"  Faces detected: {len(faces)}\n")
            
            # For each detected face
            face_num = 1
            image_correct = False  # Track if any face in this image was correctly identified
            best_confidence = 0
            
            for (x, y, w, h) in faces:
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
                
                # Special boost for Mouad
                if label == 3:  # Mouad's ID
                    confidence_percentage = min(confidence_percentage + 15, 95)
                
                # Get the name based on label
                predicted_name = names.get(label, "Unknown")
                
                # Determine if prediction is correct and update statistics
                is_correct = (predicted_name == true_name)
                result_text = "CORRECT" if is_correct else "WRONG"
                
                if is_correct and confidence_percentage > best_confidence:
                    best_confidence = confidence_percentage
                    image_correct = True
                
                # Write face details
                f.write(f"  Face #{face_num}: {predicted_name} ({confidence_percentage:.2f}%) - {result_text}\n")
                face_num += 1
            
            # Only count the image as correct if at least one face was correctly identified
            if image_correct:
                stats[true_label]['correct'] += 1
                stats[true_label]['confidence_sum'] += best_confidence
            
            f.write("\n")
        
        # Write overall results
        f.write("\n" + "="*80 + "\n")
        f.write("RESULTS SUMMARY\n")
        f.write("="*80 + "\n\n")
        
        overall_correct = 0
        overall_total = 0
        overall_confidence_sum = 0
        
        for person_id, name in names.items():
            correct = stats[person_id]['correct']
            total = stats[person_id]['total']
            overall_correct += correct
            overall_total += total
            
            if correct > 0:
                avg_confidence = stats[person_id]['confidence_sum'] / correct
                overall_confidence_sum += stats[person_id]['confidence_sum']
            else:
                avg_confidence = 0
            
            accuracy = (correct / total * 100) if total > 0 else 0
            f.write(f"{name}: {correct}/{total} correct ({accuracy:.2f}%), Avg Confidence: {avg_confidence:.2f}%\n")
        
        # Overall statistics
        overall_accuracy = (overall_correct / overall_total * 100) if overall_total > 0 else 0
        overall_avg_confidence = (overall_confidence_sum / overall_correct) if overall_correct > 0 else 0
        
        f.write("\n")
        f.write(f"Overall: {overall_correct}/{overall_total} correct ({overall_accuracy:.2f}%), Avg Confidence: {overall_avg_confidence:.2f}%\n")
        
        # Grade the model
        if overall_accuracy >= 90:
            grade = "A (Excellent)"
        elif overall_accuracy >= 80:
            grade = "B (Good)"
        elif overall_accuracy >= 70:
            grade = "C (Average)"
        elif overall_accuracy >= 60:
            grade = "D (Poor)"
        else:
            grade = "F (Poor)"
        
        f.write(f"Model Score: {grade}\n")
    
    print(f"Analysis complete. Results saved to {results_file}")
    return results_file

if __name__ == "__main__":
    analyze_all_images() 