import os
from config_helper import load_config, debug_log

def resource_path(relative_path):
    try:
        import sys
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def load_current_theme_stylesheet():
    config = load_config()
    current_theme = config.get("DISPLAY", {}).get("current_theme", "")
    themes = config.get("DISPLAY", {}).get("THEMES", [])

    for theme in themes:
        if theme["name"] == current_theme:
            return theme["content"]

    fallback_path = resource_path("Visuals/style.qss")
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            return f.read()

    return ""