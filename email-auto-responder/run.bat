@echo off
title Banking AI Automation - Launcher
echo ==========================================
echo   Starting Banking AI Agentic System
echo ==========================================

:: 1. Start the FastAPI Server in a new window
echo Starting FastAPI Server (The Brain)...
start "AI-SERVER" cmd /k "uv run main.py"

:: 2. Wait a few seconds for the model to start loading
timeout /t 5

:: 3. Start the Background Worker in a new window
echo Starting Background Worker (The Hands)...
start "EMAIL-WORKER" cmd /k "uv run background_worker.py"

echo.
echo ==========================================
echo   Both processes are now running!
echo   Close the separate windows to stop.
echo ==========================================
pause