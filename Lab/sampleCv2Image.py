# Sample Code: Reading and writing an image from the Pi camera via OpenCV.
# A window pops up with the camera view. Do not change focus, type 's' to save the image.
# (c) Dan Ionescu 2025

import cv2

# Initialize the camera (0 is the default index for the primary camera)
cap = cv2.VideoCapture(0)

# Allow some time for the camera to warm up
cv2.waitKey(100)

# Capture a single frame
ret, frame = cap.read()

if ret:
    # Display the captured image
    cv2.imshow("Stingray PiCam Snapshot", frame)

    # Wait for a key press
    key = cv2.waitKey(0) & 0xFF

    # Save the image if 's' is pressed
    if key == ord('s'):
        cv2.imwrite('Test_Image.jpg', frame)
        print("Image saved as Test_Image.jpg")

# Cleanup: Close OpenCV windows and release the camera
cv2.destroyAllWindows()
cap.release()
