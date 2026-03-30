import os
import re
from datetime import datetime
from transformers import pipeline

script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "..", "..", "data", "mission_logs.txt")

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

text_message = input("Enter distress message: ").strip()

if not text_message:
    print("No message entered. Exiting...")
    exit()

result = classifier(text_message, labels)
top_label = result["labels"][0]
confidence = result["scores"][0]

location_text = extract_location(text_message)
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

print("\n" + "=" * 60)
print(f"INTERCEPTED SIGNAL : {text_message}")
print(f"CLASSIFICATION     : {top_label.upper()}")
print(f"CONFIDENCE         : {confidence:.2%}")
print(f"EXTRACTED LOCATION : {location_text}")

if top_label == "urgent disaster rescue" and confidence > 0.7:
    print("RESCUE STATUS      : HIGH PRIORITY ALERT")
else:
    print("RESCUE STATUS      : NON-URGENT / MONITOR")
print("=" * 60)

if top_label == "urgent disaster rescue" and confidence > 0.7:
    log_entry = (
        f"[{timestamp}] URGENT ALERT\n"
        f"Message: {text_message}\n"
        f"Location: {location_text}\n"
        f"Confidence: {confidence:.2%}\n\n"
    )

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(log_entry)

    print(f"Alert logged to: {os.path.normpath(output_path)}")
else:
    print("Message marked as non-urgent.")