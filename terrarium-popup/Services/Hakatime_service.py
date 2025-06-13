import requests
from datetime import datetime, timezone, timedelta
import json
import os
import traceback
from config_helper import debug_log, load_config, save_config

class WakatimeService:
    def __init__(self, parent=None):
        self.parent = parent
        self.config_path = "Data/config.json"
        self.last_check_time = None
        self.heartbeat_timer = None
        
    def start_monitoring(self):
        """Start monitoring for heartbeats"""
        try:
            # Load last check time from config
            config = load_config()
            last_check = config.get("WAKATIME", {}).get("last_check_time")
            if last_check:
                self.last_check_time = datetime.fromisoformat(last_check)
            else:
                self.last_check_time = datetime.now(timezone.utc)
                
            # Calculate deterioration since last check
            self._calculate_deterioration()
            
            # Start monitoring for new heartbeats
            self._check_heartbeat()
            
        except Exception as e:
            debug_log(f"Error starting heartbeat monitoring: {str(e)}", level="error")
            traceback.print_exc()
            
    def _calculate_deterioration(self):
        """Calculate nourishment deterioration based on time passed"""
        try:
            now = datetime.now(timezone.utc)
            if not self.last_check_time:
                return
                
            # Calculate hours passed
            hours_passed = (now - self.last_check_time).total_seconds() / 3600
            
            # Calculate deterioration (20% per day = 0.833% per hour)
            deterioration = (hours_passed * 0.833)
            
            # Update nourishment
            config = load_config()
            current_nourishment = config.get("GAME", {}).get("active-pet", {}).get("nourishment", 50)
            new_nourishment = max(current_nourishment - deterioration, 0)
            
            # Update config
            if "active-pet" in config.get("GAME", {}):
                config["GAME"]["active-pet"]["nourishment"] = new_nourishment
                config["WAKATIME"] = config.get("WAKATIME", {})
                config["WAKATIME"]["last_check_time"] = now.isoformat()
                save_config(config)
                
            debug_log(f"Calculated nourishment deterioration: {current_nourishment} -> {new_nourishment}")
            
        except Exception as e:
            debug_log(f"Error calculating deterioration: {str(e)}", level="error")
            traceback.print_exc()
            
    def _check_heartbeat(self):
        """Check for new heartbeats and update nourishment"""
        try:
            config = load_config()
            
            # Check if we're in simulation mode
            if config.get("GLOBALS", {}).get("DEVMODE", False):
                debug_log("DEV MODE: Simulating heartbeat instead of API call")
                return self._simulate_heartbeat()
                
            api_key = config.get("GLOBALS", {}).get("WAKA_API_KEY")
            if not api_key:
                debug_log("WakaTime API key not found in config", level="warning")
                return
                
            # Get current time in UTC
            now = datetime.now(timezone.utc)
            
            # Check if we need to reset recreation for a new day
            last_reset = config.get("WAKATIME", {}).get("last_recreation_reset")
            if last_reset:
                last_reset_time = datetime.fromisoformat(last_reset)
                if last_reset_time.date() < now.date():
                    # Reset recreation to 150%
                    if "active-pet" in config.get("GAME", {}):
                        config["GAME"]["active-pet"]["recreation"] = 150
                        config["WAKATIME"]["last_recreation_reset"] = now.isoformat()
                        save_config(config)
                        debug_log("DEV MODE: Reset recreation to 150% for new day")
                        
                        # Notify main widget to update display
                        if self.parent and hasattr(self.parent, 'main_widget'):
                            self.parent.main_widget.pet_updated.emit()
            
            # Make request to WakaTime API
            headers = {
                "Authorization": f"Basic {api_key}",
                "Content-Type": "application/json"
            }
            
            debug_log("DEV MODE: Making API call to Hackatime...")
            # Get the last heartbeat
            response = requests.get(
                "https://hackatime.hackclub.com/api/v1/my/heartbeats/most_recent",
                headers=headers
            )
            
            if response.status_code != 200:
                debug_log(f"DEV MODE: API call failed with status code: {response.status_code}", level="error")
                return
                
            data = response.json()
            if not data:
                debug_log("DEV MODE: No heartbeats found in API response", level="warning")
                return
                
            # Get the latest heartbeat time
            latest_heartbeat = datetime.fromisoformat(data.get("time", "").replace("Z", "+00:00"))
            
            # Check if this is a new heartbeat (within last 2 minutes)
            if (now - latest_heartbeat).total_seconds() <= 120:
                debug_log(f"DEV MODE: New heartbeat detected! Time: {latest_heartbeat}")
                
                # Update nourishment
                current_nourishment = config.get("GAME", {}).get("active-pet", {}).get("nourishment", 50)
                new_nourishment = min(current_nourishment + 25, 100)  # Add 25% and cap at 100
                
                # Update recreation based on coding activity
                current_recreation = config.get("GAME", {}).get("active-pet", {}).get("recreation", 50)
                # Add 5% for each coding session, up to 200%
                new_recreation = min(current_recreation + 5, 200)
                
                # Update config
                if "active-pet" in config.get("GAME", {}):
                    config["GAME"]["active-pet"]["nourishment"] = new_nourishment
                    config["GAME"]["active-pet"]["recreation"] = new_recreation
                    config["WAKATIME"] = config.get("WAKATIME", {})
                    config["WAKATIME"]["last_check_time"] = now.isoformat()
                    save_config(config)
                    
                debug_log(f"DEV MODE: Updated nourishment: {current_nourishment} -> {new_nourishment}")
                debug_log(f"DEV MODE: Updated recreation: {current_recreation} -> {new_recreation}")
                
                # Notify main widget to update display
                if self.parent and hasattr(self.parent, 'main_widget'):
                    self.parent.main_widget.pet_updated.emit()
            else:
                debug_log(f"DEV MODE: No new heartbeat found. Last heartbeat was at {latest_heartbeat}")
                    
        except Exception as e:
            debug_log(f"Error checking heartbeat: {str(e)}", level="error")
            traceback.print_exc()
            
        finally:
            # Schedule next check in 2 minutes
            if self.heartbeat_timer:
                self.heartbeat_timer.stop()
            self.heartbeat_timer = QTimer()
            self.heartbeat_timer.timeout.connect(self._check_heartbeat)
            self.heartbeat_timer.start(120000)  # 2 minutes in milliseconds
            
    def _simulate_heartbeat(self):
        """Simulate a heartbeat in debug mode"""
        try:
            config = load_config()
            now = datetime.now(timezone.utc)
            
            # Update nourishment
            current_nourishment = config.get("GAME", {}).get("active-pet", {}).get("nourishment", 50)
            new_nourishment = min(current_nourishment + 25, 100)  # Add 25% and cap at 100
            
            # Update config
            if "active-pet" in config.get("GAME", {}):
                config["GAME"]["active-pet"]["nourishment"] = new_nourishment
                config["WAKATIME"] = config.get("WAKATIME", {})
                config["WAKATIME"]["last_check_time"] = now.isoformat()
                save_config(config)
                
            debug_log(f"Simulated heartbeat - Updated nourishment: {current_nourishment} -> {new_nourishment}")
            
            # Notify main widget to update display
            if self.parent and hasattr(self.parent, 'main_widget'):
                self.parent.main_widget.pet_updated.emit()
                
        except Exception as e:
            debug_log(f"Error simulating heartbeat: {str(e)}", level="error")
            traceback.print_exc() 