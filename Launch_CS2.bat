@echo off
cd /d "C:\Users\pc\Documents\Projects\cs2-tracker"
start "CS2 Tracker" python track_cs2.py
timeout /t 2 /nobreak > nul
start steam://rungameid/730