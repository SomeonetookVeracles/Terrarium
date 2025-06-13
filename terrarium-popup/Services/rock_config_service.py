import json
import os
from Services.debug_service import debug_log

def get_rock_config():
    """Get the current rock configuration"""
    try:
        # Check if the config file exists
        if not os.path.exists('Data/rock_config.json'):
            debug_log("No rock config file found, creating default config")
            default_config = {
                "rock_type": "default",
                "rock_color": "#808080",
                "rock_size": 1.0,
                "rock_position": {"x": 0.5, "y": 0.5}
            }
            save_rock_config(default_config)
            return default_config

        # Read the config file
        with open('Data/rock_config.json', 'r') as f:
            config = json.load(f)
            return config
    except Exception as e:
        debug_log(f"Error reading rock config: {str(e)}", level="error")
        return None

def update_rock_config(new_config):
    """Update the rock configuration with new values"""
    try:
        # Get current config
        current_config = get_rock_config()
        if not current_config:
            current_config = {}

        # Update with new values
        current_config.update(new_config)

        # Save the updated config
        return save_rock_config(current_config)
    except Exception as e:
        debug_log(f"Error updating rock config: {str(e)}", level="error")
        return None

def save_rock_config(config):
    """Save the rock configuration to file"""
    try:
        # Create Data directory if it doesn't exist
        if not os.path.exists('Data'):
            os.makedirs('Data')

        # Save the config
        with open('Data/rock_config.json', 'w') as f:
            json.dump(config, f, indent=4)
        return config
    except Exception as e:
        debug_log(f"Error saving rock config: {str(e)}", level="error")
        return None

def reset_rock_config():
    """Reset the rock configuration to default values"""
    default_config = {
        "rock_type": "default",
        "rock_color": "#808080",
        "rock_size": 1.0,
        "rock_position": {"x": 0.5, "y": 0.5}
    }
    return save_rock_config(default_config) 