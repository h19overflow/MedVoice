# MedVoice Startup Script
# Run with: .\start.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MedVoice Development Environment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Backend in WSL (new terminal)
Write-Host "[1/2] Starting Backend (WSL)..." -ForegroundColor Yellow
Start-Process wt -ArgumentList "wsl -d Ubuntu -- bash -c `"source ~/.local/bin/env && cd /mnt/c/Users/User/Projects/MedVoice && echo '=== MedVoice Backend ===' && uv run python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8080`""

Start-Sleep -Seconds 2

# Start Frontend (new terminal)
Write-Host "[2/2] Starting Frontend..." -ForegroundColor Yellow
Start-Process wt -ArgumentList "cmd /k `"cd /d C:\Users\User\Projects\MedVoice\medvoice-assistant && echo === MedVoice Frontend === && npm run dev`""

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  Services Starting..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Backend:  http://localhost:8080" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  API Docs: http://localhost:8080/docs" -ForegroundColor White
Write-Host ""
Write-Host "  Press any key to open the app in browser..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

# Open browser
Start-Process "http://localhost:5173"
