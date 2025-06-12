import requests

def get_coding_minutes_today(api_key):
    url = "https://hackatime.hackclub.com/v1/"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    # Example field – adjust based on real API response
    minutes = data.get("total_minutes_today", 0)
    return minutes
