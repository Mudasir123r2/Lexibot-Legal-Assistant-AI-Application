@echo off
cd /d D:\fyp\lexibot-judgment\server_fastapi
call venv\Scripts\activate.bat
python scripts\ingest_judgments.py --source files --directory "D:\fyp\lexibot-judgment\Datacollectiom\divorce" --clear
pause
