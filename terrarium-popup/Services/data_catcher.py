import json
import requests
from datetime import datetime, timedelta
from config_helper import load_config, save_config, debug_log

def fetch_heartbeats():
    """Fetch recent heartbeats from Hackatime API using the stored API key"""
    config = load_config()
    api_key = config.get("HACKATIME", {}).get("api_key", None)
    if not api_key:
        debug_log("No API key found in config under 'HACKATIME.api_key'")
        return []

    try:
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get("https://hackatime.hackclub.com/api/v1/heartbeats", headers=headers)

        if response.status_code != 200:
            debug_log("Failed to fetch heartbeats:", response.status_code, response.text)
            return []

        data = response.json()
        heartbeats = data.get("data", []) if isinstance(data, dict) else data
        debug_log(f"Fetched {len(heartbeats)} heartbeats")
        return heartbeats

    except Exception as e:
        debug_log("Error fetching heartbeats:", str(e))
        return []

def update_nourishment_from_heartbeats():
    """Update pet nourishment if heartbeats exist in the past minute"""
    heartbeats = fetch_heartbeats()
    if not heartbeats:
        return

    now = datetime.utcnow()
    recent = [
        hb for hb in heartbeats
        if "time" in hb and now - datetime.utcfromtimestamp(hb["time"]) <= timedelta(minutes=1)
    ]

    if recent:
        config = load_config()
        config.setdefault("GAME", {})["pet_nourishment"] = 100
        save_config(config)
        debug_log("Pet nourishment set to 100 due to recent activity")

# Optional helper access for other modules
def get_metric_names():
    return ["pet_nourishment"]

def get_metric_values():
    config = load_config()
    return {"pet_nourishment": config.get("GAME", {}).get("pet_nourishment", 0)}

def deteriorate_metrics():
    config = load_config()
    nourishment = config.get("GAME", {}).get("pet_nourishment", 0)
    nourishment = max(0, nourishment - 1)
    config["GAME"]["pet_nourishment"] = nourishment
    save_config(config)
    debug_log("Pet nourishment deteriorated to:", nourishment)
