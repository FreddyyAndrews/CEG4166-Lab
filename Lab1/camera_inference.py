import sys, tty, termios, select, threading, time
import pigpio
import RPi.GPIO as GPIO
import cv2
import numpy as np
import tensorflow as tf
from motor_control import Motor_control
from picamera2 import Picamera2


# --- TensorFlow Object Detection Function ---
def detect_objects(image, model):
    """
    Runs inference on the image using the TensorFlow model.
    Draws bounding boxes on detections with scores above a threshold.
    """
    # Preprocess: convert image to tensor and add batch dimension.
    input_tensor = tf.convert_to_tensor(image)
    input_tensor = input_tensor[tf.newaxis, ...]
    
    # Run inference.
    detections = model(input_tensor)
    
    # Extract detection results (adjust keys if needed).
    boxes = detections['detection_boxes'][0].numpy()  # shape: [N, 4]
    scores = detections['detection_scores'][0].numpy()  # shape: [N]
    classes = detections['detection_classes'][0].numpy().astype(np.int32)
    
    threshold = 0.5  # Only consider detections above this score.
    height, width, _ = image.shape
    
    for i in range(boxes.shape[0]):
        if scores[i] > threshold:
            box = boxes[i]
            # Convert normalized coordinates to pixels.
            y_min = int(box[0] * height)
            x_min = int(box[1] * width)
            y_max = int(box[2] * height)
            x_max = int(box[3] * width)
            # Draw rectangle and label.
            cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
            label = f"ID:{classes[i]} {scores[i]:.2f}"
            cv2.putText(image, label, (x_min, y_min - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    return image

# --- Camera stream function with TensorFlow detection ---
def camera_stream_with_detection():
    # Initialize Picamera2 and configure for video capture.
    camera = Picamera2()
    video_config = camera.create_video_configuration()
    camera.configure(video_config)
    camera.start()
    
    # Load your TensorFlow detection model (change the path accordingly).
    model_path = 'ssd_mobilenet_v2_320x320_coco17_tpu-8/saved_model'
    model = tf.saved_model.load(model_path)
    
    while True:
        # Capture a frame as a numpy array.
        frame = camera.capture_array("main")
        
        # Run detection and draw bounding boxes.
        annotated_frame = detect_objects(frame.copy(), model)
        
        # Display the frame.
        cv2.imshow("Camera Feed with Detections", annotated_frame)
        # Exit the loop if 'x' is pressed in the camera window.
        if cv2.waitKey(1) & 0xFF == ord('x'):
            break
    
    camera.stop()
    cv2.destroyAllWindows()


# --- Main ---
if __name__ == "__main__":
    # Start camera stream with detection in a daemon thread.
    camera_thread = threading.Thread(target=camera_stream_with_detection, daemon=True)
    camera_thread.start()

    # When keyboard control exits, the program ends (camera thread is daemonized).
    print("Program terminated.")
