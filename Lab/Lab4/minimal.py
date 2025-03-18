import cv2
from picamera2 import Picamera2
import time
import matplotlib.pyplot as plt

def capture_frames():
    picam2 = Picamera2()
    picam2.start()
    time.sleep(2)  # Allow camera to warm up
    
    # Enable interactive mode for live updating
    plt.ion()
    fig, ax = plt.subplots()
    
    # Capture one frame to initialize the image plot
    im = picam2.capture_array()
    im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    im_plot = ax.imshow(im)
    ax.axis('off')  # Optionally hide axis ticks

    while True:
        im = picam2.capture_array()
        print(im.shape)
        im = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
        im_plot.set_data(im)
        fig.canvas.draw()
        fig.canvas.flush_events()
        # Optionally add a short pause:
        plt.pause(0.001)

    # Cleanup (this part won't be reached in an infinite loop)
    plt.ioff()
    plt.show()
    picam2.stop()

capture_frames()
