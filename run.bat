@echo off
cd /d %~dp0
echo Installing dependencies...
pip install -r requirements.txt
echo Starting MSIP Label Scanner...
echo Open http://127.0.0.1:5000 in your browser
python app.py
pause
