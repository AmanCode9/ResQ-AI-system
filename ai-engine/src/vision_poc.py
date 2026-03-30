import cv2
import os
from ultralytics import YOLO

script_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(script_dir, "..", "models", "yolov8n.pt")
video_name = "people_demo.mp4"
video_path = os.path.join(script_dir, "..", "..", "data", video_name)

print(f"Loading model from: {os.path.normpath(model_path)}")
print(f"Loading video from: {os.path.normpath(video_path)}")

if not os.path.exists(model_path):
    print("Error: Model file not found.")
    exit()

if not os.path.exists(video_path):
    print("Error: Video file not found.")
    exit()

try:
    model = YOLO(model_path)
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video.")
    exit()

cv2.namedWindow("ResQ-AI Vision POC", cv2.WINDOW_NORMAL)

frame_idx = 0
print("\nProcessing video... Press 'q' or 'Esc' to stop.\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_idx += 1

    results = model.predict(frame, classes=[0], verbose=False)
    result = results[0]

    human_found = False

    if result.boxes is not None and len(result.boxes) > 0:
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())

            if cls_id == 0 and conf > 0.20:
                human_found = True

        if human_found:
            print(f"Human detected at frame {frame_idx}")

    annotated_frame = result.plot()

    cv2.putText(
        annotated_frame,
        f"Frame: {frame_idx}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 0, 255),
        2
    )

    if human_found:
        cv2.putText(
            annotated_frame,
            "HUMAN DETECTED",
            (20, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )

    cv2.imshow("ResQ-AI Vision POC", annotated_frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q") or key == 27:
        print("Exit key pressed. Closing video...")
        break

    if cv2.getWindowProperty("ResQ-AI Vision POC", cv2.WND_PROP_VISIBLE) < 1:
        print("Window closed manually. Exiting...")
        break

cap.release()
cv2.destroyAllWindows()
print("Process stopped successfully.")