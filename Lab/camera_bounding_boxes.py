import cv2
import numpy as np
from tflite_runtime.interpreter import Interpreter

# --- Load the TensorFlow Lite model ---
model_path = "model.tflite"  # Replace with your model's filename
interpreter = Interpreter(model_path=model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
input_height, input_width = input_details[0]["shape"][1:3]

# --- Set up camera capture ---
# Option 1: Using GStreamer pipeline for libcamera support with OpenCV
cap = cv2.VideoCapture(
    "libcamerasrc ! video/x-raw, width=640, height=480, format=(string)NV12, framerate=30/1 ! videoconvert ! appsink"
)
# Option 2: If your setup supports cv2.VideoCapture(0) directly, use:
# cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # --- Preprocess the frame ---
    # Resize frame to model input size
    resized_frame = cv2.resize(frame, (input_width, input_height))
    # Depending on your model, you may need to convert to float32 and normalize (e.g., divide by 255)
    input_data = np.expand_dims(resized_frame, axis=0).astype(np.float32)
    # For some models, normalization might be required:
    # input_data = (input_data - 127.5) / 127.5

    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()

    # --- Process model outputs ---
    # The following assumes your model returns:
    #   1. bounding boxes (normalized coordinates),
    #   2. class indices,
    #   3. confidence scores,
    #   4. number of detections (this order may vary!)
    boxes = interpreter.get_tensor(output_details[0]["index"])[
        0
    ]  # shape: [num_boxes, 4]
    classes = interpreter.get_tensor(output_details[1]["index"])[
        0
    ]  # shape: [num_boxes]
    scores = interpreter.get_tensor(output_details[2]["index"])[0]  # shape: [num_boxes]
    # If your model provides a fourth tensor, it might indicate the number of detections.

    height, width, _ = frame.shape
    for i in range(len(scores)):
        if scores[i] > 0.5:  # Confidence threshold
            # The box format is usually [ymin, xmin, ymax, xmax] normalized between 0 and 1
            ymin, xmin, ymax, xmax = boxes[i]
            start_point = (int(xmin * width), int(ymin * height))
            end_point = (int(xmax * width), int(ymax * height))
            # Draw bounding box
            cv2.rectangle(frame, start_point, end_point, (0, 255, 0), 2)
            # Label for the object detected
            label = f"ID: {int(classes[i])} {scores[i]:.2f}"
            cv2.putText(
                frame,
                label,
                (start_point[0], start_point[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2,
            )

    # --- Display the frame with bounding boxes ---
    cv2.imshow("Live Detection", frame)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
