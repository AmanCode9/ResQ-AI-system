import cv2
import os
from ultralytics import YOLO

script_dir = os.path.dirname(os.path.abspath(__file__))


model_path = os.path.join(script_dir, "..", "models", "yolov8n.pt")

video_name = "flood.mp4" 
video_path = os.path.join(script_dir, "..", "..", "data", video_name)

print(f"📍 Loading Model from: {os.path.normpath(model_path)}")
print(f"📍 Loading Video from: {os.path.normpath(video_path)}")

try:
    model = YOLO(model_path)
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("Tip: Check if 'yolov8n.pt' is in the 'ai-engine/models' folder.")
    exit()

if not os.path.exists(video_path):
    print(f"❌ Error: Could not find video at {video_path}")
    exit()

results = model.predict(source=video_path, stream=True, classes=[0])

print("\n✅ Video started! Press 'q' or the 'X' button on the window to stop.")

for result in results:
    frame = result.plot()

    cv2.putText(frame, "RESQ-AI VISION CORE", (20, 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    cv2.imshow("ResQ-AI Vision POC", frame)

    if cv2.waitKey(1) & 0xFF == ord('q') or cv2.getWindowProperty("ResQ-AI Vision POC", cv2.WND_PROP_VISIBLE) < 1:
        break

cv2.destroyAllWindows()
print("Process stopped successfully.")