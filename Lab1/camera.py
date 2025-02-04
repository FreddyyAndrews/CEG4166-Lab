# Import libraries
import time
from picamera import PiCamera

# Initialize Camera
camera = PiCamera()

# Define functions to start and stop camera stream
def cameraPreview():
    camera.start_preview()

def cameraExit():
    camera.stop_preview()

try:
    # Python code starts execution from here
    cameraPreview()
    time.sleep(5)
    cameraExit()
except KeyboardInterrupt:
    print("CTRL+C pressed")

finally:
    cameraExit()
