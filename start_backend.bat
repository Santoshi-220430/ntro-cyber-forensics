@echo off
echo ========================================================
echo   NTRO CYBER FORENSICS PLATFORM - FASTAPI BACKEND
echo   Problem ID: SIH26148
echo ========================================================
python -m uvicorn backend.app.main:app --reload --port 8000
pause
