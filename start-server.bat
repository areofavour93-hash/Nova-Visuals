@echo off
cd /d "%~dp0"
where node >nul 2>nul
if %errorlevel%==0 (
  echo Starting the dashboard server...
  node server.js
  pause
  exit /b
)
echo Node.js is not installed or is not on PATH.
echo For online hosting, upload this project to your hosting provider instead.
pause
