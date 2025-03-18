import cv2
import os
import numpy as np
from PIL import Image, ImageEnhance
from glob import glob

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

def create_augmented_images(image):
    """Create augmented versions of the image to improve training"""
    augmented_images = []
    
    # Ensure image is grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Convert OpenCV image to PIL for easier augmentation
    pil_img = Image.fromarray(gray)
    
    # Original image
    augmented_images.append(np.array(pil_img))
    
    # Brightness variations
    enhancer = ImageEnhance.Brightness(pil_img)
    augmented_images.append(np.array(enhancer.enhance(0.8)))  # Darker
    augmented_images.append(np.array(enhancer.enhance(1.2)))  # Brighter
    
    # Contrast variation
    enhancer = ImageEnhance.Contrast(pil_img)
    augmented_images.append(np.array(enhancer.enhance(1.2)))  # More contrast
    
    return augmented_images

def train_face_recognizer():
    """
    Train a face recognizer using images from the train_set directory
    """
    # Load the Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Create the face recognizer - LBPH works well for face recognition
    # Adjust parameters for better performance
    # radius=1: Default radius captures facial details well
    # neighbors=8: Default number of points in the pattern
    # grid_x=8, grid_y=8: More cells provides more spatial information
    recognizer = cv2.face.LBPHFaceRecognizer_create(
        radius=1,      # Radius of the circular LBP pattern (default: 1)
        neighbors=8,   # Number of points in the circular pattern (default: 8)
        grid_x=8,      # Number of cells in the horizontal direction (default: 8)
        grid_y=8,      # Number of cells in the vertical direction (default: 8)
        threshold=100  # Threshold for face recognition (default: DBL_MAX)
    )
    
    # Base directory for training data
    train_dir = 'train_set'
    
    # Parameters for face detection with progressive relaxation
    detection_params = [
        {'scaleFactor': 1.1, 'minNeighbors': 6, 'minSize': (60, 60)}, # Strict parameters
        {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (50, 50)}, # Medium parameters
        {'scaleFactor': 1.2, 'minNeighbors': 3, 'minSize': (40, 40)}  # Relaxed parameters
    ]
    
    # Lists to store training data
    faces = []
    labels = []
    
    # Process each person's directory
    person_count = {1: 0, 2: 0, 3: 0}
    for person_id in range(1, 4):  # 1, 2, 3
        person_dir = os.path.join(train_dir, str(person_id))
        if not os.path.exists(person_dir):
            print(f"Warning: Directory for person {person_id} not found")
            continue
            
        print(f"Processing images for person {person_id}...")
        
        # Get all image files in the directory (any supported format)
        image_patterns = ['*.jpg', '*.jpeg', '*.png']
        image_files = []
        for pattern in image_patterns:
            image_files.extend(glob(os.path.join(person_dir, pattern)))
        
        # Process each image file
        for image_file in image_files:
            image = cv2.imread(image_file)
            if image is None:
                print(f"Warning: Could not read image {image_file}")
                continue
                
            # Preprocess the image
            preprocessed = preprocess_image(image)
            
            # Detect faces using progressive parameters
            faces_detected = []
            for params in detection_params:
                faces_detected = face_cascade.detectMultiScale(
                    preprocessed,
                    scaleFactor=params['scaleFactor'],
                    minNeighbors=params['minNeighbors'],
                    minSize=params['minSize'],
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                if len(faces_detected) > 0:
                    break
            
            # Process each detected face (normally just one per image)
            for (x, y, w, h) in faces_detected:
                # Extract face region
                face_roi = preprocessed[y:y+h, x:x+w]
                
                # Resize to a standard size for consistency (e.g., 100x100)
                face_roi = cv2.resize(face_roi, (100, 100))
                
                # Add to training set
                faces.append(face_roi)
                labels.append(person_id)
                
                # Increment person counter
                person_count[person_id] += 1
                
                # For Mouad, also add slightly modified versions of the face to improve robustness
                if person_id == 3:  # Mouad's ID
                    # Add versions with slight brightness and contrast changes
                    for alpha in [0.9, 1.1]:  # Contrast
                        for beta in [-5, 5]:  # Brightness
                            modified_face = cv2.convertScaleAbs(face_roi.copy(), alpha=alpha, beta=beta)
                            faces.append(modified_face)
                            labels.append(person_id)
                            person_count[person_id] += 1
    
    # Check if we have enough training samples
    if len(faces) == 0:
        print("Error: No face samples detected for training")
        return False
    
    # Print stats
    print("\nTraining statistics:")
    for person_id, count in person_count.items():
        print(f"Person {person_id}: {count} face samples")
    print(f"Total: {len(faces)} face samples\n")
    
    # Convert lists to numpy arrays
    faces_array = np.array(faces)
    labels_array = np.array(labels)
    
    # Train the recognizer
    print("Training the face recognizer...")
    recognizer.train(faces_array, labels_array)
    
    # Save the trained model
    model_file = 'trained_model.yml'
    print(f"Saving the trained model to {model_file}")
    recognizer.write(model_file)
    
    print("Face recognizer training completed successfully")
    return True

if __name__ == "__main__":
    train_face_recognizer()
