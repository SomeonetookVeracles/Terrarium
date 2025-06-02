@echo off
python -m PyInstaller --onefile --noconsole --add-data "style.qss;." main.py
pause
