import os
from transformers import pipeline

script_dir = os.path.dirname(os.path.abspath(__file__))

output_path = os.path.join(script_dir, "..", "..", "data", "mission_logs.txt")

print("🔄 Initializing ResQ-AI NLP Engine... (this may take a moment)")
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

text_message = "Help! We are trapped on the roof at 5th and Main. Water is rising fast."
labels = ["urgent disaster rescue", "casual conversation", "news report"]

result = classifier(text_message, labels)
top_label = result['labels'][0]
confidence = result['scores'][0]

print("\n" + "="*40)
print(f"📡 INTERCEPTED SIGNAL: {text_message}")
print(f"🚨 CLASSIFICATION:    {top_label.upper()}")
print(f"📊 CONFIDENCE:        {confidence:.2%}")
print("="*40)

if top_label == "urgent disaster rescue" and confidence > 0.7:
    log_entry = f"URGENT ALERT: {text_message} (Conf: {confidence:.2%})\n"
    
    with open(output_path, "a") as f:
        f.write(log_entry)
    
    print(f"✅ Alert logged to system at: {os.path.normpath(output_path)}")
else:
    print("ℹ️ Message logged as non-urgent. No action taken.")