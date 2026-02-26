#  ResQ-AI: Intelligent Disaster Response Ecosystem

**Phase 1: Core AI Modules (Vision & NLP)**

ResQ-AI is an autonomous drone response system designed to locate survivors in disaster zones using computer vision and prioritize rescue missions using natural language processing.

## 📂 Project Structure
```text
├── ai-engine/          # ML Models & Inference Scripts
│   ├── src/            # Source code (Vision & NLP)
│   └── models/         # YOLOv8 Weights
├── data/               # Test Footage & Logs (Local Only)
└── backend-hub/        # (Upcoming in Phase 2)

 Key Features (Phase 1)
Vision Core: Real-time human detection from aerial drone footage using YOLOv8.

Status: ✅ Operational (Tested on flood/forest scenarios).

NLP Core: Zero-shot classification of emergency messages using BART-Large.

Status: ✅ Operational (80%+ confidence on urgent alerts).

🛠️ Setup & Installation

1. Clone the repository: git clone [https://github.com/AmanCode9/resq-ai-system.git](https://github.com/AmanCode9/RESQ-AI-system.git)
cd RESQ-AI-system

2. Create a Virtual Environment (Recommended):
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

3. Install Dependencies:
pip install -r ai-engine/requirements.txt

4. Download Models (First Run Only):
The YOLOv8 model (yolov8n.pt) and BART-Large NLP model will download automatically when you run the scripts for the first time.

🖥️ Usage
1. Run Vision Demo (Drone Surveillance)
Detects survivors in sample drone footage.
python ai-engine/src/vision_poc.py

>Controls: Press q to stop the video stream.

>Output: Real-time bounding boxes around detected persons.

2. Run NLP Demo (Emergency Parsing)
Classifies incoming text messages as "Urgent Rescue," "News," or "Casual."
python ai-engine/src/nlp_poc.py

Output: Classification label, confidence score, and automatic logging of urgent alerts to data/mission_logs.txt.

📊 Evaluation Metrics
Detection Accuracy: Successfully identifies humans in low-contrast environments (e.g., floods, forests).
Response Latency: Real-time inference (~30 FPS) on standard CPU.
NLP Confidence: High accuracy (>80%) on zero-shot classification of distress signals.
