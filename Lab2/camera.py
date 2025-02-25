#Import libraries
import time
from picamera import PiCamera
from rotationSpeed_Graph import *

#initialize Camera
camera = PiCamera()

#define functions to start and stop camera stream
def robot_is_moving():
    # Placeholder implementation
    return False

def cameraPreview():
    camera.start_preview()

def cameraExit():
    camera.stop_preview()

#defining captue image function
def capture_image(filename):
    camera.capture(filename)
    print("Image Captured as " + filename)

#defining record video function
def record_video(filename):
    camera.start_recording(filename)
    print("Recording Started as " + filename)
    time.sleep(5)
    camera.stop_recording()
    print("Recording Stopped")

def Robot_foward_with_camera():
    cameraPreview()
    Robot_forward(LEFT_FORWARD, RIGHT_FORWARD)
    time.sleep(5)
    capture_image("forward.jpg")
    Robot_stop()
    cameraExit()

#defining camera stream
def camera_stream():
    camera.start_preview(fullscreen=False, window=(100, 100, 640, 480))
    while True:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    camera.stop_preview()
    
try:
    #python code starts execution from here
    #cameraPreview()
    camera_stream()
    time.sleep(5)
    cameraExit()

except KeyboardInterrupt:
    print ("CTRL+C pressed")

finally:
    cbameraExit()