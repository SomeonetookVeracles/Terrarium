import os
import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

SESSION_LOG = os.path.join(LOG_DIR, f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

def log_event(message, level="INFO"):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] [{level}] {message}"
    print(entry)
    with open(SESSION_LOG, "a", encoding="utf-8") as f:
        f.write(entry + "\n")

def get_log():
    with open(SESSION_LOG, "r", encoding="utf-8") as f:
        return f.read()
