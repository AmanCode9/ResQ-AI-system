import os
import re
import sys
import json
from datetime import datetime
from transformers import pipeline

script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "..", "..", "data")
output_path = os.path.join(data_dir, "mission_logs.txt")
result_path = os.path.join(data_dir, "nlp_result.json")

print("Initializing ResQ-AI NLP Engine...")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

labels = ["urgent disaster rescue", "casual conversation", "news report"]

def extract_location(text):
    patterns = [
        r"\bat\s+([A-Za-z0-9\s,&\-]+?)(?:[.!?]|$)",
        r"\bnear\s+([A-Za-z0-9\s,&\-]+?)(?:[.!?]|$)",
        r"\bin\s+([A-Za-z0-9\s,&\-]+?)(?:[.!?]|$)"
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Location not found"

if len(sys.argv) > 1:
    text_message = " ".join(sys.argv[1:]).strip()
else:
    text_message = input("Enter distress message: ").strip()

if not text_message:
    print("No message entered. Exiting...")
    sys.exit()

result = classifier(text_message, labels)
top_label = result["labels"][0]
confidence = result["scores"][0]

location_text = extract_location(text_message)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
status = "HIGH PRIORITY ALERT" if top_label == "urgent disaster rescue" and confidence > 0.7 else "NON-URGENT / MONITOR"

response_data = {
    "module": "nlp",
    "message": text_message,
    "classification": top_label.upper(),
    "confidence": round(confidence, 4),
    "location": location_text,
    "status": status,
    "timestamp": timestamp
}

print("\n" + "=" * 60)
print(f"INTERCEPTED SIGNAL : {text_message}")
print(f"CLASSIFICATION     : {top_label.upper()}")
print(f"CONFIDENCE         : {confidence:.2%}")
print(f"EXTRACTED LOCATION : {location_text}")
print(f"RESCUE STATUS      : {status}")
print("=" * 60)

with open(result_path, "w", encoding="utf-8") as f:
    json.dump(response_data, f, indent=2)

if status == "HIGH PRIORITY ALERT":
    log_entry = (
        f"[{timestamp}] URGENT ALERT\n"
        f"Message: {text_message}\n"
        f"Location: {location_text}\n"
        f"Confidence: {confidence:.2%}\n\n"
    )
    with open(output_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Alert logged to: {os.path.normpath(output_path)}")
    print(f"NLP result saved to: {os.path.normpath(result_path)}")
else:
    print("Message marked as non-urgent.")
    print(f"NLP result saved to: {os.path.normpath(result_path)}")