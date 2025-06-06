import os
import sys
from config_helper import load_config, save_config, debug_log

def resource_path(relative_path):
    """ Get absolute path to resource, compatible with PyInstaller """
    try:
        base_path = sys._MEIPASS  # when bundled by PyInstaller
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def update_theme_list():
    # Locate themes directory safely
    themes_dir = resource_path('Visuals/themes')

    if not os.path.isdir(themes_dir):
        print(f"[ERROR] Themes directory not found: {themes_dir}")
        return

    themes = []
    for file in os.listdir(themes_dir):
        if file.lower().endswith('.qss'):
            file_path = os.path.join(themes_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    theme_content = f.read()
                themes.append({
                    'name': os.path.splitext(file)[0],  # "fluent_dark"
                    'content': theme_content
                })
            except Exception as e:
                print(f"[ERROR] Failed to read theme '{file_path}': {e}")

    if not themes:
        print("[INFO] No themes found in Visuals/themes.")
        return

    config = load_config()
    if 'DISPLAY' not in config or not isinstance(config['DISPLAY'], dict):
        config['DISPLAY'] = {}

    config['DISPLAY']['THEMES'] = themes
    save_config(config)
    print(f"[SUCCESS] {len(themes)} theme(s) loaded and saved to config.")

if __name__ == "__main__":
    update_theme_list()