#!/usr/bin/env bash
set -e

echo "========================================================"
echo "  NTRO CYBER FORENSICS PLATFORM - PRODUCTION RUNNER"
echo "  Problem ID: SIH26148 | Ready to Deploy Single Service"
echo "========================================================"

echo "[*] Building frontend assets..."
cd frontend
npm install
npm run build
cd ..

echo "[*] Starting production web server on port ${PORT:-8000}..."
exec uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 2
