Terrarium
    Terrarium is a productivity companion that allows coders in the Hack Club base to stay on track while having a small terrarium that grows as they code. This project reminds users to drink water every 45 minutes and eat a snack every hour. It also automatically takes a screenshot of your screen every hour so you don't forget to have a picture of your project to put into Hack_Hour on Slack!

Installation:
git clone https://github.com/SomeonetookVeracles/Terrarium.git
->cd terrarium
->pip install -r requirements.txt
->python terrarium.py.

Modifications:
You can modify the intervals and screenshot behavior in config.json
    You can copy the json code to input into your own config.json
{
    "water_interval_minutes": 45,
    "snack_interval_minutes": 60,
    "screenshot_interval_minutes": 60,
    "screenshot_folder": "./screenshots"
}
All screenshots are saved in the "screenshots" folder by default.

Dependencies
plyer - for cross-platform notifications
pyautogui - for screenshots
datetime and os - time and file management.
    To install these dependencies:
    pip install -r requirements.txt

License:
    Licensed under the Apache License 2.0

Authors:
    SomeonetookVeracles & CitrusB1. 
                                                    Happy Hacking!
