@echo off
python -m PyInstaller --onefile --noconsole --add-data "Visuals//style.qss;." main.py
pause
