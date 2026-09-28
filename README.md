# NTRO Cyber Forensics Platform & DSL Engine
### Smart India Hackathon Prototype (SIH26148)
**Organization:** National Technical Research Organisation (NTRO)  
**Problem Statement:** *"Creation of scripts/functions with new programming language to commence Computer & Network forensic analysis without triggering security solutions."*

---

## 1. Problem Understanding & Solution

### The Core Challenge
Legitimate digital forensics and incident response (DFIR) tools frequently trigger alarms in endpoint security software (Antivirus, EDR, HIPS). Active memory inspection, process enumeration, socket inspection, or file crawling may be classified as suspicious activity, causing security agents to terminate the forensic tool, corrupt in-flight volatile evidence, or trigger false incident tickets.

### Our Solution
Rather than resorting to unsafe, real-world malware evasion techniques (such as API unhooking, direct syscalls, reflective DLL injection, or BYOVD exploitation), this platform establishes a **cryptographically governed, policy-compliant forensic scripting platform**:
- **Domain-Specific Language (Forensic DSL)**: Allows investigators to describe computer and network forensic tasks in high-level commands (`GET SYSTEM`, `GET PROCESSES`, `GET NETWORK`, `GET LOGS`, `HASH FILES`, `BUILD TIMELINE`, `ANALYZE`, `GENERATE REPORT`).
- **Safety Enforcement**: Destructive operations (`DELETE`, `KILL`, `MODIFY`, `DROP`, `INJECT`) are blocked at the compiler level.
- **Security Compatibility Layer**: Binds investigator identity, script HMAC signatures, and read-only policies (`FORENSIC_READ_ONLY`) so enterprise security solutions can verify and allow legitimate triage without alerts.
- **Evidence Integrity & Chain of Custody**: Cryptographically seals evidence using FIPS 180-4 SHA-256 digests and maintains an immutable hash-chained custody ledger.
- **Automated Reporting**: Generates official, court-admissible forensic PDF reports with a single command.

---

## 2. System Architecture

```
                 ┌──────────────────────────────────────────────┐
                 │       AUTHORIZED INVESTIGATOR CONSOLE        │
                 │          (React + Vite + Tailwind)           │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │           FORENSIC SCRIPTING DSL             │
                 │   (Lexer -> Parser -> AST -> Validator)      │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │        SECURITY COMPATIBILITY LAYER          │
                 │  - Investigator badge verification           │
                 │  - Script SHA-256 & HMAC-SHA256 signature    │
                 │  - Policy Enforcement: FORENSIC_READ_ONLY    │
                 │  - EDR Coexistence Simulation Engine         │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │               FORENSIC ENGINE                │
                 │   System • Processes • Files • Network • Logs│
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │          EVIDENCE INTEGRITY VAULT            │
                 │  - Read-only storage + SHA-256 seal          │
                 │  - Normalized multi-source timeline          │
                 │  - Deterministic rule engine & Threat IOCs   │
                 │  - Hash-chained chain of custody ledger      │
                 │  - Official PDF ReportLab report generator   │
                 └──────────────────────────────────────────────┘
```

---

## 3. Technology Stack

- **Frontend**: React, Vite, Tailwind CSS, Lucide Icons
- **Backend API**: Python FastAPI, Uvicorn, Pydantic
- **Forensic DSL Engine**: Custom Python Lexer, Recursive-Descent Parser, AST Validator, Interpreter
- **Database**: SQLite (WAL Mode, Thread-Safe, Relational Schema)
- **Report Generation**: ReportLab (Vector PDF compiler with cryptographic hash verification)
- **Evidence Vault**: FIPS 180-4 SHA-256 digest computation & hash-chaining

---

---

## 4. Idempotent Architecture & Zero-Duplication Engine

To ensure production integrity and avoid duplicate evidence clutter or ledger flooding:
- **Evidence Deduplication**: When `GET FILES`, `GET SYSTEM`, or manual uploads are triggered, the platform verifies `(case_id, artifact_name, sha256_hash)`. Existing artifacts are returned idempotently rather than duplicated. File modifications update existing records and log a single `EVIDENCE_UPDATED` custody record.
- **Custody Ledger Cleanliness**: Repeated health checks or verification scans across unchanged evidence log consolidated batch verification entries rather than hundreds of repetitive rows.
- **Automated Database Normalization**: Startup migrations automatically prune any duplicate evidence or orphaned records on launch.
- **Vault Deduplication Action**: Investigators can click `Deduplicate Vault` or call `POST /api/cases/{case_id}/deduplicate` anytime.

---

## 5. Deployment Options (Ready-to-Deploy)

### Option A: 1-Command Production Service (Backend + React SPA Served Together)
FastAPI automatically serves the production-compiled React frontend bundle directly from `/frontend/dist`:
```powershell
cd forensic-platform
start_production.bat
```
*(On Linux/macOS/Cloud VM: `./start_production.sh`)*
- Production URL: `http://localhost:8000` (Dashboard, API, and Swagger Docs all unified on port 8000)

### Option B: Docker Container Deployment
Run the complete multi-stage containerized environment with healthchecks and persistent volumes:
```bash
cd forensic-platform
docker compose up --build -d
```
- Web Application & API: `http://localhost:8000`
- Check Health: `curl http://localhost:8000/health`

### Option C: Cloud Deployment (Render & Vercel)
- **Render (Full Stack)**: Deploy via the included [render.yaml](file:///c:/Users/acer/Documents/ORCA-main/forensic-platform/render.yaml). Builds the Vite frontend and serves via FastAPI with 2 Uvicorn workers.
- **Vercel (Frontend)**: Deploy via the included [vercel.json](file:///c:/Users/acer/Documents/ORCA-main/forensic-platform/vercel.json) with automatic API routing.

### Option D: Local Development Mode (Hot Reload)
```powershell
# Terminal 1 - FastAPI Backend
cd forensic-platform
python -m uvicorn backend.app.main:app --reload --port 8000

# Terminal 2 - React Vite Frontend
cd forensic-platform/frontend
npm run dev
```
- Frontend Dev: `http://localhost:5173`
- Backend API Docs: `http://127.0.0.1:8000/docs`


## 6. Pre-Seeded Demonstration Credentials

| Role | Username | Password | Badge Number | Permitted Operations |
|---|---|---|---|---|
| **INVESTIGATOR** | `investigator` | `Forensic@123` | NTRO-INV-42 | Collect, analyze, hash, correlate, export report |
| **ADMIN** | `admin` | `Admin@NTRO2026` | NTRO-DIR-01 | Full system administration, IOC config, security policy |
| **AUDITOR / VIEWER** | `viewer` | `Viewer@123` | NTRO-AUD-07 | Read-only inspection of evidence, chain of custody, and reports |

*(One-click quick login buttons for these accounts are available on the login page).*

---

## 7. Example Forensic DSL Scripts

### Full Investigation Sequence:
```dsl
CASE "CASE-2026-001"

SET MODE = "DEMO"
GET SYSTEM
GET USERS
GET PROCESSES
GET NETWORK
GET LOGS
GET FILES "/sample_data"
HASH FILES
BUILD TIMELINE
ANALYZE
GENERATE REPORT "PDF"
VERIFY INTEGRITY
```

### Safety Test (Destructive Command Blocking):
```dsl
CASE "CASE-2026-001"
DELETE SYSTEM FILES
KILL PROCESS 1337
```
*Platform immediately intercepts and halts with reason: `Destructive operation is prohibited by forensic integrity rules`.*

---

## 8. Automated Test Suites

Run all unit and integration test suites:
```powershell
cd forensic-platform

# 1. Test DSL Lexer, Parser, AST, and Validator
python tests/test_dsl.py

# 2. Test End-to-End Forensic Interpreter Pipeline
python tests/test_full_pipeline.py

# 3. Test FastAPI REST Endpoints & Authentication
python tests/test_api.py
```
*(All test suites exit with code 0).*

---

## 8. SIH Demonstration Scenario (CASE-2026-001)

- **Target Workstation:** `WS-FIN-04.fin.local`
- **Scenario:** A finance workstation is suspected of staging an unauthorized executable and connecting to an external C2 node.
- **Workflow:**
  1. Login as `investigator`.
  2. Open the **Forensic Console**.
  3. Execute the full DSL script.
  4. Inspect the **Detection Findings** (`update_svc_helper.exe` staged in user `Temp` directory; active TCP socket to threat intel C2 `198.51.100.45:4444`).
  5. Check **Evidence & Integrity** (all artifacts verified with SHA-256).
  6. Inspect the **Chain of Custody** (tamper-evident hash-linked ledger).
  7. Open **Security Compatibility** to demonstrate the EDR coexistence handshake simulation.
  8. Download the official, cryptographically sealed **Forensic Examination PDF Report**.

---

## 9. Limitations & Future Scope

### Known Prototype Limitations:
- The offline PCAP parser handles IPv4, TCP, UDP, DNS, and HTTP metadata; extended protocols (QUIC, IPv6, SMB) are scheduled for subsequent iterations.
- In LIVE mode on Windows, certain kernel memory allocations require administrative elevation.

### Future Roadmap:
- Real-time kernel driver connector for signed ETW (Event Tracing for Windows) telemetry.
- STIX/TAXII automated threat feed synchronization for live IOC updates.
- YARA rule compilation support directly embedded into the DSL grammar (`SCAN FILES WITH YARA "rule_name"`).
