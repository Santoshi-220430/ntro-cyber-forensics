"""
Forensic Platform - FastAPI Main Application
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import sys
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Ensure parent directory is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.config import CORS_ORIGINS, REPORTS_DIR, FRONTEND_DIST_DIR, HOST, PORT
from backend.app.database import init_db, seed_default_data
from backend.app.api.endpoints import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure tables exist and seed demo scenario
    init_db()
    seed_default_data()
    print("[+] Forensic Platform backend initialized. Security compatibility mode: ACTIVE.")
    yield
    print("[-] Forensic Platform backend shutting down.")

app = FastAPI(
    title="Cyber Investigators - NTRO Forensics Platform & DSL Engine",
    description="Authorized Computer & Network Forensics Platform with Custom DSL and Security Compatibility Layer (SIH26148)",
    version="2.4.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(api_router, prefix="/api")

@app.get("/health")
def health():
    return {
        "status": "HEALTHY",
        "service": "Cyber Investigators Forensics Platform",
        "version": "2.4.0",
        "security_compatibility_mode": "AUTHORIZED_FORENSIC_MODE"
    }

# Production SPA static file serving
if FRONTEND_DIST_DIR.exists() and (FRONTEND_DIST_DIR / "index.html").exists():
    if (FRONTEND_DIST_DIR / "assets").exists():
        app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST_DIR / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Allow API and Docs to be handled by FastAPI
        if full_path.startswith("api") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Not found")

        file_path = FRONTEND_DIST_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        index_file = FRONTEND_DIST_DIR / "index.html"
        return FileResponse(str(index_file))
else:
    @app.get("/")
    def root():
        return {
            "service": "NTRO Cyber Forensics Platform",
            "problem_id": "SIH26148",
            "organization": "National Technical Research Organisation (NTRO)",
            "status": "OPERATIONAL",
            "documentation": "/docs",
            "api_root": "/api"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host=HOST, port=PORT, reload=False)

