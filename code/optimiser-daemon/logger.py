# logger.py

import os
import json
from datetime import datetime

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_file_path = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl")

def log_entry(state, action, reward):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "reward": reward,
        "state": state
    }

    try:
        with open(log_file_path, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        print(f"[Logger] Failed to write log: {e}")
