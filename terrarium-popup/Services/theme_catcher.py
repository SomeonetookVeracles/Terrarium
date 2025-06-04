import os
import json
from config_helper import load_config, save_config
def update_theme_list():
    themes_dir = os.path.join(os.path.dirname(__file__), '..', 'visuals', 'themes')
    themes_dir = os.path.abspath(themes_dir)

    if not os.path.isdir(themes_dir):
        raise FileNotFoundError(f"Themes directory not found: {themes_dir}")
    
    themes = []
    for file in os.listdir(themes_dir):
        if file.endswith('.qss'):
            file_path = os.path.join(themes_dir, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    theme_content = f.read()
                themes.append({
                    'name': os.path.splitext(file)[0],  #example: "fluent_Dark"
                    'content': theme_content
                })
            except Exception as e:
                print(f"Failed to read {file_path}: {e}")

    if not themes:
        print("No themes found.")
        return
    # Load and update to config
    config = load_config()

    if 'DISPLAY' not in config or not isinstance(config['DISPLAY'], dict):
        config['DISPLAY'] = {}
    config['DISPLAY']['THEMES'] = themes 
    save_config(config)
    print(f"Updated config.json: {len(themes)} added under [DISPLAY].")
if __name__ == "__main__":
    update_theme_list()