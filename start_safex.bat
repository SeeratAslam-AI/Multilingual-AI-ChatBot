@echo off
title SafeX Chatbot Server
cd /d "%~dp0"

echo Starting SafeX Chatbot backend...
start "SafeX Backend" cmd /k py -m uvicorn main:app --reload

echo Waiting for the server to start...
timeout /t 3 /nobreak >nul

echo Opening the chatbot in your browser...
start http://127.0.0.1:8000

echo.
echo Done. The backend is running in the other window - keep it open.
echo Close that window (or press CTRL+C in it) to stop the server.
pause >nul
