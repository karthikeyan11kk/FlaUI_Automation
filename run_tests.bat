@echo off
rem Runs all Acturis tests. Report: results\report.html, screenshots: results\screenshots
cd /d "%~dp0"
python -m pytest
pause
