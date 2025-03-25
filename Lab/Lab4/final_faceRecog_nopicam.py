import cv2
import time

# Open default camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Camera not accessible.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert to grayscale and detect faces as before
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceDetector.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
        if confidence < 100:
            id = name_data[id] if id < len(name_data) else "Unknown"
            confidence_text = " {0}%".format(round(100 - confidence))
        else:
            id = "Unknown"
            confidence_text = " {0}%".format(round(100 - confidence))
        cv2.putText(frame, str(id), (x+5, y-5), font, 1, (255, 255, 255), 2)
        cv2.putText(frame, str(confidence_text), (x+5, y+h-5), font, 1, (255, 255, 0), 1)

    cv2.imshow('Face Detector', frame)
    if cv2.waitKey(10) & 0xFF == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()
