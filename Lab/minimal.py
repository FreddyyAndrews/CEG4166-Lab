import os
import numpy as np
os.environ["DISPLAY"] = ":0"
os.environ["QT_QPA_PLATFORM"] = "xcb"
import cv2
cv2.startWindowThread()
test_image = 255 * np.ones((480, 640, 3), np.uint8)
cv2.namedWindow("Test", cv2.WINDOW_NORMAL)
cv2.imshow("Test", test_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
