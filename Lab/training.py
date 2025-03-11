import cv2
import os
import numpy as np

def prepare_training_data(data_folder_path):
    faces = []
    labels = []
    # Assume each sub-folder in data_folder_path is named with a label (e.g., "1", "2", ...)
    for label in os.listdir(data_folder_path):
        person_folder_path = os.path.join(data_folder_path, label)
        if not os.path.isdir(person_folder_path):
            continue
        
        for image_name in os.listdir(person_folder_path):
            image_path = os.path.join(person_folder_path, image_name)
            # Read the image in grayscale
            image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if image is None:
                continue

            # Detect the face in the image
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces_rects = face_cascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5)
            
            for (x, y, w, h) in faces_rects:
                face = image[y:y+h, x:x+w]
                faces.append(face)
                labels.append(int(label))
    return faces, labels

# Path to your dataset
data_folder_path = 'train_set'
faces, labels = prepare_training_data(data_folder_path)

# Create and train the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.train(faces, np.array(labels))

# Save the trained model to a file
recognizer.write('trained_model.yml')
