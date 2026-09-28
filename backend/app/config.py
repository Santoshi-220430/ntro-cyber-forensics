"""
Forensic Platform Configuration
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_DIR = BASE_DIR / "backend"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
REPORTS_DIR = BASE_DIR / "backend" / "app" / "reports_vault"
EVIDENCE_VAULT_DIR = BASE_DIR / "backend" / "app" / "evidence_vault"

# Ensure runtime directories exist
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_VAULT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)

FRONTEND_DIST_DIR = BASE_DIR / "frontend" / "dist"

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DB_PATH = Path(os.getenv("FORENSIC_DB_PATH", str(BACKEND_DIR / "app" / "forensic_platform.db")))

SECRET_KEY = os.getenv("FORENSIC_SECRET_KEY", "sih26148_ntro_authorized_dfir_super_secret_jwt_key_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 # 24 hours

ALLOWED_HOSTS = ["*"]

raw_cors = os.getenv("CORS_ORIGINS", "")
if raw_cors:
    CORS_ORIGINS = [origin.strip() for origin in raw_cors.split(",") if origin.strip()]
else:
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

