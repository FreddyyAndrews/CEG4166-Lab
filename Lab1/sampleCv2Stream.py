# Sample Code: Capturing and displaying a video stream from the Pi camera via OpenCV.
# A window pops up with the camera stream view. Do not change focus, type 'q' to quit.
# (c) Dan Ionescu 2025

import cv2

# Initialize the Pi camera using OpenCV
cap = cv2.VideoCapture(0)  # 0 is the default camera index

# Set resolution and frame rate (optional)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 32)

# Allow some time for the camera to warm up
cv2.waitKey(100)

print("Press 'q' to exit video stream...")

# Capture continuous frames from the camera
while True:
    ret, frame = cap.read()  # Capture a single frame
    if not ret:
        print("Failed to capture frame. Exiting...")
        break

    # Display the current frame
    cv2.imshow("Stingray Live Video Feed", frame)

    # Wait for key press and break if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup: Release the camera and close OpenCV windows
cap.release()
cv2.destroyAllWindows()