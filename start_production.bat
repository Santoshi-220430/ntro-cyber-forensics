@echo off
echo ========================================================
echo   NTRO CYBER FORENSICS PLATFORM - PRODUCTION RUNNER
echo   Problem ID: SIH26148 | Ready to Deploy Single Service
echo ========================================================

echo [*] Building frontend static bundle...
cd frontend
call npm run build
cd ..

echo [*] Starting FastAPI production server with built SPA on port 8000...
echo [*] Open in browser: http://localhost:8000
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
pause
