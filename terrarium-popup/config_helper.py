import json
import os 
import shutil
import traceback
config_path = "config.json"
backup_path = "config_backup.json"

def load_config():
    #Load user config, create backup, return empty if file is missing or fucked
    if not os.path.exists(config_path):
        print("[WARNING] Config file not found. A new one will be created on save")
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        print("[INFO] Config loaded")
        return config 
    except json.JSONDecodeError:
        print("[ERROR] Failed to parse config (invalid). Creating backup")
        _backup_corrupt_config()
        return {}
    
    except Exception as e:
        print(f"[ERROR] Unexpected error while loading config")
        traceback.print_exc()
        return {}
def save_config(config_data):
    #Attempt to save, if failed, preserve existing data
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"[CRITICAL] Failed to save config: {e}")
        traceback.print_exc()

def _backup_corrupt_config():
    try:
        if os.path.exists(config_path):
            shutil.copy(config_path, backup_path)
            print(f"[INFO] Corrupt config backed up to {backup_path}")
    except Exception as e:
        print(f"[WARNING] Failed to create config backip: {e}")