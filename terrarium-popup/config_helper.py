import json
import os 
import shutil
import traceback
config_path = "config.json"
backup_path = "config_backup.json"
def get_default_config():
    return {
        "METADATA": {
            "Name": "Terrarium",
            "Version": "0.1.8",
            "Build": "Unstable"
        },
        "GLOBALS": {
            "DEVMODE": False
        },
        "DISPLAY": {
            "width_ratio": 0.33,
            "height_ratio": 0.5,
            "sidebar_width": 120,
            "winwidth": 513,
            "winheight": 525,
            "current_theme": "fluent-Dark",
            "THEMES": [
                {
                    "name": "fluent-Dark",
                    "content": "/* ==== Fluent themed dark mode ==== */\n/* Font and base styling */\nQWidget {\n    background-color: #1f1f1f;\n    color: #f3f3f3;\n    font-family: 'Segoe UI', 'Roboto', sans-serif;\n    font-size: 14px;\n}\n\n/* === Settings Page === */\n#settings-page {\n    background-color: #2b2b2b;\n    padding: 24px;\n    border-radius: 12px;\n    border: 1px solid #3a3a3a;\n}\n\n/* === Labels === */\n#settings-label {\n    font-weight: 600;\n    color: #ffffff;\n    padding: 8px 0;\n}\n\n/* === Sidebar === */\n#sidebar {\n    background-color: #1f1f1f;\n    border-right: 1px solid #333333;\n}\n\n/* === Sidebar Buttons === */\n#sidebar-button {\n    background-color: transparent;\n    color: #f3f3f3;\n    padding: 12px 16px;\n    border: none;\n    text-align: left;\n    border-radius: 6px;\n}\n#sidebar-button:hover {\n    background-color: #2a2a2a;\n}\n\n/* === Content Area === */\n#content {\n    background-color: #2b2b2b;\n    padding: 20px;\n    border-radius: 8px;\n}\n\n/* === QPushButton === */\nQPushButton {\n    background-color: #333333;\n    color: #ffffff;\n    border: 1px solid #444444;\n    padding: 10px 16px;\n    border-radius: 6px;\n    font-weight: 500;\n}\nQPushButton:hover {\n    background-color: #3d3d3d;\n    border: 1px solid #555555;\n}\nQPushButton:pressed {\n    background-color: #4a4a4a;\n    border: 1px solid #666666;\n}\n/* === QCheckBox === */\nQCheckBox {\n    padding: 6px;\n    spacing: 6px;\n    font-weight: 400;\n}\nQCheckBox::indicator {\n    width: 18px;\n    height: 18px;\n    border-radius: 4px;\n    border: 1px solid #777777;\n    background-color: #2a2a2a;\n}\nQCheckBox::indicator:checked {\n    background-color: #0078d4;\n    /* image: url(:/icons/Darkcheckmark.svg); */\n    border: 1px solid #0078d4;\n}\n\n/* === Qslider == */\nQSlider::groove:horizontal {\n    height: 4px;\n    background: #444444;\n    border-radius: 2px;\n}\nQSlider::handle:horizontal {\n    background: #0078d4;\n    border: none;\n    height: 16px;\n    width: 16px;\n    margin: -6px 0;\n    border-radius: 8px;\n}\n\n/* === Settings Elements === */\n#settings-checkbox {\n    font-size: 14px;\n    margin-bottom: 12px;\n    color: #e0e0e0;\n}\n#settings-slider {\n    min-height: 20px;\n    border-radius: 3px;\n}\n/* Contrasting Labels */\n#settings-label {\n    font-weight: bold;\n    color: #ffffff;\n}"
                },
                {
                    "name": "fluent-Light",
                    "content": "/* Lightmode fluent style */\n\n/*font and base styling */\nQWidget {\n    background-color: #f3f3f3; /* Light background color, like fluent mica*/\n    color: #1f1f1f;\n    font-family: 'Segoe UI', 'Roboto', sans-serif;\n    font-size: 14px;\n}\n/* === Settings === */\n#settings-page {\n    background-color: #ffffff;\n    padding: 24px;\n    border-radius: 12px;\n    border: 1px solid #d0d0d0;\n}\n/* === Labels === */\n#settings-label {\n    font-weight: 600;\n    color: #1f1f1f;\n    padding: 8px 0,\n}\n\n/* ==== Sidebar ==== */\n#sidebar {\n    background-color: #e6e6e6;\n    border-right: 1px solid #cccccc\n}\n/* === Sidebar Buttons === */\n#sidebar-button {\n    background-color: transparent;\n    color: #1f1f1f;\n    padding: 12px 16px;\n    border: none;\n    text-align: left;\n    border-radius: 6px;\n}\n\n#sidebar-button:hover {\n    background-color: #e0e0e0;\n}\n/* === Content Area === */\n#content {\n    background-color: #ffffff;\n    padding: 20px;\n    border-radius: 8px;\n}\n/* === General Styling for QPushButton === */\nQPushButton {\n    background-color: #e1e1e1;\n    color: #1f1f1f;\n    border: 1px solid #cfcfcf;\n    padding: 10px 16px;\n    border-radius: 6px;\n    font-weight: 500;\n}\n\nQPushButton:hover {\n    background-color: #d0d0d0;\n    border: 1px solid #b0b0b0;\n}\nQPushButton:pressed {\n    background-color: #c0c0c0;\n    border: 1px solid #a0a0a0;\n}\n/* === Checkbox Styling === */\nQCheckBox {\n    padding: 6px;\n    spacing: 6px;\n    font-weight: 400;\n}\nQCheckBox::indicator {\n    width: 18px;\n    height: 18px;\n    border-radius: 4px;\n    border: 1px solid #a0a0a0;\n    background-color: #ffffff;\n}\nQCheckBox::indicator:checked {\n    background-color: #0078d4; /*Fluent Blue */\n    /* image: url(:/icons/checkmark.svg); */\n    border: 1px solid #0078d4;\n}\n/* === Sliders === */\nQSlider::groove:horizontal {\n    height: 4px;\n    background: #d0d0d0;\n    border-radius: 2px;\n}\n\nQSlider::handle:horizontal {\n    background: #0078d4;\n    border: none;\n    height: 16px;\n    width: 16px;\n    margin: -6px 0;\n    border-radius: 8px;\n}\n/* === Specific Settings Elements === */\n#settings-checkbox {\n    font-size: 14px;\n    margin-bottom: 12px;\n}\n#settings-slider {\n    min-height: 20px;\n    border-radius: 3px;\n}\n/* Ensure label contrast */\n#settings-label {\n    font-weight: bold;\n    color: #1f1f1f;\n}"
                }
            ]
        },
        "GAME": {
            "placeholder": True
        }

    }
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