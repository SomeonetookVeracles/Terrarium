import json
import os
CONFIG_PATH = "config.json"

#Add variables to this, otherwise it won't work.
default_config = {
    "METADATA": {
        "NAME": "Terrarium",
        "VERSION": "0.1.2",
        "build": "Unstable"
    },
    "GLOBALS": {
        "DEVMODE": True
    },
    "DISPLAY": {
        "width_ratio": 0.33,
        "height_ratio": 0.5,
        "DARKMODE": False
    },
    "GAME": {
        "Placeholders, put all variables for the game in here": False
    }
}

def load_config():
    if not os.path.exists(CONFIG_PATH):
        save_config(default_config)
        return default_config
    try:
        with open(CONFIG_PATH, "r") as f:
            user_config = json.load(f)
            print("Config Loaded.")
        return merge_dicts(default_config, user_config)
    except Exception:
        return default_config


def merge_dicts(defaults, custom):
    for key in defaults:
        if key not in custom:
            custom[key] = defaults[key]
        elif isinstance(defaults[key], dict):
            custom[key] = merge_dicts(defaults[key], custom/get(key, {}))
    return custom

def save_config(config_data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)
