# 🚁 ResQ-AI: Intelligent Disaster Response Ecosystem

**Phase 1: Core AI Modules (Vision & NLP)**

ResQ-AI is an autonomous drone response system designed to locate survivors in disaster zones using computer vision and prioritize rescue missions using natural language processing.

## 📂 Project Structure
```text
├── ai-engine/          # ML Models & Inference Scripts
│   ├── src/            # Source code (Vision & NLP)
│   └── models/         # YOLOv8 Weights
├── data/               # Test Footage & Logs (Local Only)
└── backend-hub/        # (Upcoming in Phase 2)

🚀 Key Features (Phase 1)
Vision Core: Real-time human detection from aerial drone footage using YOLOv8.

Status: ✅ Operational (Tested on flood/forest scenarios).

NLP Core: Zero-shot classification of emergency messages using BART-Large.

Status: ✅ Operational (80%+ confidence on urgent alerts).

🛠️ Setup & Installation
1. Clone the repository:
