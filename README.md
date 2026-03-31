
# ResQ-AI: Intelligent Disaster Response Ecosystem

ResQ-AI is an AI-based disaster response system designed to assist in locating survivors and prioritizing rescue operations using computer vision and natural language processing.

The system combines real-time vision models with intelligent text analysis to improve situational awareness in disaster scenarios such as floods, forests, and collapsed infrastructure.

---

## Core Features

### Vision Module — Survivor Detection
- Real-time human detection from aerial drone footage using YOLOv8  
- Designed to work in low-visibility environments such as floods and forests  
- Outputs bounding boxes for detected individuals  

Status: Operational (tested on sample disaster footage)

---

### NLP Module — Emergency Message Parsing
- Zero-shot classification using BART-Large  
- Categorizes messages into:
  - Urgent Rescue  
  - News  
  - Casual  
- Automatically logs urgent alerts for further processing  

Status: Operational (above 80% confidence on urgent alerts)

---

## Project Structure

```text
resq-ai-system/
├── ai-engine/              # ML models and inference scripts
│   ├── src/
│   │   ├── vision_poc.py   # YOLOv8-based detection
│   │   ├── nlp_poc.py      # NLP classification
│   │   └── utils/          # Helper functions
│   ├── models/             # Auto-downloaded weights
│   └── requirements.txt    # Python dependencies
│
├── data/                   # Test footage and logs (local only)
├── backend-hub/            # Planned for future integration
└── README.md



## Setup and Installation

### Prerequisites

* Python 3.9 or above
* pip
* Virtual environment (recommended)

---

### 1. Clone the Repository

```bash
git clone https://github.com/AmanCode9/RESQ-AI-system.git
cd RESQ-AI-system
```

---

### 2. Create a Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r ai-engine/requirements.txt
```

---

### 4. Model Download

Required models will be downloaded automatically during the first run:

* YOLOv8 (yolov8n.pt)
* BART-Large

---

## Usage

### Run Vision Module

```bash
python ai-engine/src/vision_poc.py
```

* Detects humans in sample drone footage
* Displays real-time bounding boxes

Controls:
Press `q` to stop execution

---

### Run NLP Module

```bash
python ai-engine/src/nlp_poc.py
```

* Classifies input messages
* Outputs:

  * Label
  * Confidence score
* Logs urgent alerts to:

```text
data/mission_logs.txt
```

---

## Evaluation Metrics

| Metric             | Description                                     |
| ------------------ | ----------------------------------------------- |
| Detection Accuracy | Reliable detection in low-contrast environments |
| Response Latency   | Approx. 30 FPS on standard CPU                  |
| NLP Confidence     | Above 80% accuracy in classification            |

---

## Roadmap

* [x] Vision and NLP modules implemented
* [x] Basic testing and evaluation completed
* [x] System architecture designed for integration
* [x] Backend and real-time pipeline planned
* [x] End-to-end workflow defined
* [x] Autonomous response pipeline conceptualized

---

## Real-World Relevance

This system is intended to:

* Reduce disaster response time
* Support rescue teams with AI-based insights
* Improve prioritization of critical rescue efforts

---

## Notes

* Large files such as videos and model weights are not included in the repository
* Models are downloaded automatically during execution

---

## License

This project is developed as part of an academic mini project.

```
