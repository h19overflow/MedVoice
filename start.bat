@echo off
title MedVoice Launcher
color 0B

echo ========================================
echo   MedVoice Development Environment
echo ========================================
echo.

echo [1/2] Starting Backend on port 8080 (WSL)...
start wt wsl -d Ubuntu -- bash -c "source ~/.local/bin/env && cd /mnt/c/Users/User/Projects/MedVoice && echo '=== MedVoice Backend (port 8080) ===' && uv run python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080"

echo Waiting for backend to start...
timeout /t 5 /nobreak > nul

echo [2/2] Starting Frontend on port 5173...
start wt cmd /k "cd /d C:\Users\User\Projects\MedVoice\medvoice-assistant && echo === MedVoice Frontend (port 5173) === && npm run dev"

echo.
echo ========================================
echo   Services Starting...
echo ========================================
echo.
echo   Backend:  http://localhost:8080
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:8080/docs
echo.

timeout /t 5 /nobreak > nul

echo Opening browser...
start http://localhost:5173

echo.
echo Press any key to close this window...
pause > nul
