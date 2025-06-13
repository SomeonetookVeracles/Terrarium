import requests
from datetime import datetime, timezone
import json
import os
import traceback
from config_helper import debug_log, load_config

class WakatimeService:
    def __init__(self, parent=None):
        self.parent = parent
        self.config_path = "config.json"
        
    def _load_config(self):
        """Load the config file"""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            debug_log(f"Failed to load config: {e}")
            return {}
            
    def _save_config(self, config_data):
        """Save the config file"""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config_data, f, indent=4)
            return True
        except Exception as e:
            debug_log(f"Failed to save config: {e}")
            return False
            
    def update_heartbeat(self):
        """Fetches the latest heartbeat from WakaTime API and updates the config"""
        config = self._load_config()
        
        # Check if we're in simulation mode
        if config.get("GLOBALS", {}).get("DEVMODE", False):
            return self._simulate_heartbeat(config)
            
        api_key = config.get("GLOBALS", {}).get("WAKA_API_KEY")
        
        if not api_key:
            debug_log("WakaTime API key not found in config")
            return False
            
        try:
            # Get current time in UTC
            now = datetime.now(timezone.utc)
            
            # Make request to WakaTime API
            headers = {
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json"
            }
            
            # Get the last heartbeat
            response = requests.get(
                "https://hackatime.hackclub.com/api/v1/",
                headers=headers,
                params={"date": now.strftime("%Y-%m-%d")}
            )
            
            if response.status_code != 200:
                debug_log(f"Failed to fetch WakaTime data: {response.status_code}")
                return False
                
            data = response.json()
            if not data.get("data"):
                debug_log("No heartbeats found for today")
                return False
                
            # Get the latest heartbeat
            latest_heartbeat = data["data"][0]
            
            # Add 5 to the duration
            duration = latest_heartbeat.get("duration", 0) + 5
            
            # Update the config with the new heartbeat data
            if "WAKATIME" not in config:
                config["WAKATIME"] = {}
                
            config["WAKATIME"]["last_heartbeat"] = {
                "time": latest_heartbeat.get("time"),
                "duration": duration,
                "project": latest_heartbeat.get("project"),
                "language": latest_heartbeat.get("language")
            }
            
            # Update pet_nourishment
            if "GAME" not in config:
                config["GAME"] = {}
            
            current_nourishment = config["GAME"].get("pet_nourishment", 0)
            new_nourishment = min(current_nourishment + 5, 100)  # Cap at 100
            config["GAME"]["pet_nourishment"] = new_nourishment
            
            debug_log(f"Updated pet nourishment from {current_nourishment} to {new_nourishment}")
            
            # Save the updated config
            if self._save_config(config):
                debug_log("Successfully updated WakaTime heartbeat data and pet nourishment")
                return True
            return False
            
        except Exception as e:
            debug_log(f"Failed to update WakaTime heartbeat: {e}")
            traceback.print_exc()
            return False

    def _simulate_heartbeat(self, config):
        """Simulate a WakaTime heartbeat in debug mode"""
        try:
            now = datetime.now(timezone.utc)
            
            # Create simulated heartbeat data
            if "WAKATIME" not in config:
                config["WAKATIME"] = {}
                
            config["WAKATIME"]["last_heartbeat"] = {
                "time": now.isoformat(),
                "duration": 5,
                "project": "Debug Simulation",
                "language": "Python"
            }
            
            # Update pet_nourishment
            if "GAME" not in config:
                config["GAME"] = {}
            
            current_nourishment = config["GAME"].get("pet_nourishment", 0)
            new_nourishment = min(current_nourishment + 5, 100)  # Cap at 100
            config["GAME"]["pet_nourishment"] = new_nourishment
            
            debug_log(f"Simulated heartbeat - Updated pet nourishment from {current_nourishment} to {new_nourishment}")
            
            # Save the updated config
            if self._save_config(config):
                debug_log("Successfully simulated WakaTime heartbeat")
                return True
            return False
            
        except Exception as e:
            debug_log(f"Failed to simulate WakaTime heartbeat: {e}")
            traceback.print_exc()
            return False 