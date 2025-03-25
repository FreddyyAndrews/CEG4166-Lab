import os
os.environ["DISPLAY"] = ":0"

import matplotlib
matplotlib.use('TkAgg')  # Use a non-Qt backend to avoid conflicts
import matplotlib.pyplot as plt

import cv2
import numpy as np
import time
from picamera2 import Picamera2

# Load the face detection model
cascadePath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
faceDetector = cv2.CascadeClassifier(cascadePath)

# Load trained face recognition model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('model.yml')

# Font settings
font = cv2.FONT_HERSHEY_SIMPLEX

# Name data (ensure order matches dataset)
name_data = ['none', 'Freddy', 'Mouad']

# Initialize Picamera2
picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()
time.sleep(2)  # Allow camera to warm up

def face_recognition():
    # Set up matplotlib interactive display in the main thread using TkAgg
    plt.ion()
    fig, ax = plt.subplots()
    init_img = np.zeros((480, 640, 3), dtype=np.uint8)
    im_plot = ax.imshow(init_img)
    ax.axis('off')
    
    while plt.fignum_exists(fig.number):
        # Capture frame from Picamera2
        img = picam2.capture_array()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceDetector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
        
        # Process each detected face
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            if confidence < 100:
                label = name_data[id] if id < len(name_data) else "Unknown"
                confidence_text = " {0}%".format(round(100 - confidence))
            else:
                label = "Unknown"
                confidence_text = " {0}%".format(round(100 - confidence))
            cv2.putText(img, str(label), (x + 5, y - 5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence_text), (x + 5, y + h - 5), font, 1, (255, 255, 0), 1)
        
        # Convert BGR to RGB for matplotlib
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        im_plot.set_data(img_rgb)
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(0.001)
    
    plt.close(fig)
    picam2.stop()

# Run face recognition in the main thread
face_recognition()
