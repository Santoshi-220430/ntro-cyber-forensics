"""
Forensic Platform - REST API Endpoints Router
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import os
import uuid
import json
import shutil
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse
from pydantic import BaseModel

from ..auth.auth_service import authenticate_user, create_access_token, get_current_user, require_roles
from ..database import get_db_connection, hash_password
from ..config import REPORTS_DIR, SAMPLE_DATA_DIR, EVIDENCE_VAULT_DIR
from ..audit.audit_service import AuditService
from ..evidence.evidence_service import EvidenceService
from ..evidence.chain_of_custody import ChainOfCustodyService
from ..timeline.timeline_service import TimelineService
from ..analysis.analysis_engine import AnalysisEngine
from ..reports.report_generator import ForensicReportGenerator
from ..security.compatibility import SecurityCompatibilityManager
from ..forensic.collectors import OfflinePCAPParser
from forensic_dsl import Lexer, Parser, DSLValidator
from forensic_dsl.interpreter import DSLInterpreter

router = APIRouter()

# --- Pydantic Request Models ---
class LoginRequest(BaseModel):
    username: str
    password: str

class CaseCreateRequest(BaseModel):
    case_number: str
    title: str
    description: Optional[str] = None
    target_host: Optional[str] = "WS-TARGET.local"
    mode: Optional[str] = "DEMO"

class ScriptValidateRequest(BaseModel):
    script: str
    case_id: Optional[str] = None

class ScriptExecuteRequest(BaseModel):
    script: str
    case_id: Optional[str] = None
    security_mode: Optional[str] = "AUTHORIZED" # NORMAL, SIMULATION, AUTHORIZED

class IOCCreateRequest(BaseModel):
    type: str # HASH, IP, DOMAIN, FILENAME
    value: str
    description: str
    severity: Optional[str] = "HIGH"
    source: Optional[str] = "INVESTIGATOR"

class SecuritySimulateRequest(BaseModel):
    mode: str # NORMAL, SIMULATION, AUTHORIZED
    script: str
    case_id: Optional[str] = None

# ================= AUTHENTICATION =================
@router.post("/auth/login")
def login(req: LoginRequest):
    user = authenticate_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid investigator username or password.")
    token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    AuditService.log_event(
        actor_name=user["full_name"],
        actor_role=user["role"],
        action="INVESTIGATOR_LOGIN",
        resource_type="SESSION",
        resource_id=user["id"],
        details="Investigator session initiated successfully."
    )
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/auth/me")
def get_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    return current_user

# ================= CASES =================
@router.get("/cases")
def list_cases(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
    SELECT c.*,
           (SELECT COUNT(*) FROM evidence WHERE case_id = c.id) as evidence_count,
           (SELECT COUNT(*) FROM findings WHERE case_id = c.id) as findings_count
    FROM cases c ORDER BY c.created_at DESC;
    """)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.post("/cases")
def create_case(req: CaseCreateRequest, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    conn = get_db_connection()
    c = conn.cursor()
    case_id = f"case-{uuid.uuid4().hex[:10]}"
    now = datetime.now(timezone.utc).isoformat()

    try:
        c.execute("""
        INSERT INTO cases (id, case_number, title, description, status, investigator_id, investigator_name, target_host, mode, created_at, updated_at)
        VALUES (?, ?, ?, ?, 'ACTIVE', ?, ?, ?, ?, ?, ?)
        """, (
            case_id, req.case_number, req.title, req.description,
            current_user["id"], current_user["full_name"], req.target_host, req.mode, now, now
        ))
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=400, detail=f"Failed to create case: {str(e)}")

    conn.close()

    ChainOfCustodyService.record_entry(
        case_id=case_id,
        evidence_id=None,
        action="CASE_INITIALIZED",
        actor_name=current_user["full_name"],
        actor_role=current_user["role"],
        details=f"Case {req.case_number} registered for target {req.target_host} in {req.mode} mode."
    )

    AuditService.log_event(
        actor_name=current_user["full_name"],
        actor_role=current_user["role"],
        action="CASE_CREATE",
        resource_type="CASE",
        resource_id=case_id,
        details=f"Case {req.case_number} created."
    )

    return {"id": case_id, "case_number": req.case_number, "status": "ACTIVE"}

@router.get("/cases/{case_id}")
def get_case(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM cases WHERE id = ? OR case_number = ?;", (case_id, case_id))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Case not found.")
    return dict(row)

@router.put("/cases/{case_id}")
def update_case(case_id: str, data: Dict[str, Any], current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    c.execute("""
    UPDATE cases SET
        title = COALESCE(?, title),
        description = COALESCE(?, description),
        status = COALESCE(?, status),
        mode = COALESCE(?, mode),
        target_host = COALESCE(?, target_host),
        updated_at = ?
    WHERE id = ? OR case_number = ?;
    """, (
        data.get("title"), data.get("description"), data.get("status"),
        data.get("mode"), data.get("target_host"), now, case_id, case_id
    ))
    conn.commit()
    conn.close()
    return {"status": "SUCCESS", "updated_at": now}

# ================= FORENSIC DSL =================
@router.post("/scripts/validate")
def validate_script(req: ScriptValidateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        lexer = Lexer(req.script)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    except Exception as e:
        return {
            "valid": False,
            "errors": [{"message": str(e), "line": 1, "col": 1, "severity": "ERROR", "code": "SYNTAX_ERROR"}],
            "warnings": [],
            "statements_count": 0
        }

    validator = DSLValidator(user_role=current_user["role"])
    is_valid, errors, warnings = validator.validate(ast, default_case_id=req.case_id)
    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "statements_count": len(ast.statements),
        "ast_summary": [s.to_dict() for s in ast.statements]
    }

@router.post("/scripts/execute")
def execute_script(req: ScriptExecuteRequest, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    try:
        lexer = Lexer(req.script)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Script parse error: {str(e)}")

    validator = DSLValidator(user_role=current_user["role"])
    is_valid, errors, warnings = validator.validate(ast, default_case_id=req.case_id)
    if not is_valid:
        return {
            "status": "VALIDATION_FAILED",
            "errors": errors,
            "warnings": warnings,
            "logs": [f"[!] Validation Error: {e['message']}" for e in errors]
        }

    interpreter = DSLInterpreter(current_user=current_user, security_mode=req.security_mode or "AUTHORIZED")
    result = interpreter.execute(ast, default_case_id=req.case_id)
    return result

# ================= EVIDENCE & INTEGRITY =================
@router.get("/cases/{case_id}/evidence")
def get_evidence(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    return EvidenceService.get_case_evidence(case_id)

@router.post("/cases/{case_id}/evidence/verify")
def verify_evidence(case_id: str, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    return EvidenceService.verify_all_evidence(case_id, actor_name=current_user["full_name"])

@router.post("/cases/{case_id}/evidence/upload")
async def upload_evidence(
    case_id: str,
    file: UploadFile = File(...),
    source_type: str = Form("FILE"),
    current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))
):
    # Save file into evidence vault
    vault_filename = f"{uuid.uuid4().hex[:8]}_{file.filename}"
    target_path = EVIDENCE_VAULT_DIR / vault_filename
    with open(target_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    evidence = EvidenceService.register_evidence(
        case_id=case_id,
        name=file.filename,
        source_type=source_type,
        original_file_path=str(target_path),
        collector_id=current_user["id"],
        collector_name=current_user["full_name"],
        collection_method="MANUAL_AUTHORIZED_UPLOAD"
    )
    return evidence

# ================= ARTIFACTS / COLLECTED DATA =================
@router.get("/cases/{case_id}/system")
def get_system_info(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM system_info WHERE case_id = ? ORDER BY collected_at DESC LIMIT 1;", (case_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else {}

@router.get("/cases/{case_id}/processes")
def get_processes(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM processes WHERE case_id = ? ORDER BY is_suspicious DESC, pid ASC;", (case_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.get("/cases/{case_id}/files")
def get_files(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM files WHERE case_id = ? ORDER BY is_suspicious DESC, filename ASC;", (case_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.get("/cases/{case_id}/network")
def get_network(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM network_connections WHERE case_id = ? ORDER BY is_suspicious DESC, local_port ASC;", (case_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.get("/cases/{case_id}/logs")
def get_logs(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM logs WHERE case_id = ? ORDER BY timestamp DESC;", (case_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

# ================= TIMELINE =================
@router.get("/cases/{case_id}/timeline")
def get_timeline(
    case_id: str,
    severity: Optional[str] = None,
    source: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return TimelineService.get_timeline(case_id, severity=severity, source=source)

# ================= FINDINGS & ANALYSIS =================
@router.get("/cases/{case_id}/findings")
def get_findings(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    return AnalysisEngine.get_findings(case_id)

@router.post("/cases/{case_id}/analyze")
def run_analysis(case_id: str, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    return AnalysisEngine.analyze_case(case_id, actor_name=current_user["full_name"])

# ================= CHAIN OF CUSTODY & AUDIT =================
@router.get("/cases/{case_id}/chain-of-custody")
def get_case_coc(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    return ChainOfCustodyService.get_entries(case_id)

@router.get("/cases/{case_id}/audit")
def get_case_audit(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    return AuditService.get_audit_logs(limit=100, case_id=case_id)

@router.get("/audit")
def get_all_audit(limit: int = 150, current_user: Dict[str, Any] = Depends(get_current_user)):
    return AuditService.get_audit_logs(limit=limit)

# ================= REPORTS =================
@router.post("/cases/{case_id}/report")
def generate_report(case_id: str, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    return ForensicReportGenerator.generate_report(
        case_id=case_id,
        author_name=current_user["full_name"],
        author_badge=current_user.get("badge_number", "NTRO-INV-42")
    )

@router.get("/cases/{case_id}/reports")
def list_reports(case_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE case_id = ? ORDER BY generated_at DESC;", (case_id,))
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.get("/reports/{report_id}/download")
def download_report(report_id: str):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM reports WHERE id = ?;", (report_id,))
    row = c.fetchone()
    conn.close()
    if not row or not os.path.exists(row["file_path"]):
        raise HTTPException(status_code=404, detail="Forensic report file not found on disk.")
    return FileResponse(
        path=row["file_path"],
        filename=os.path.basename(row["file_path"]),
        media_type="application/pdf"
    )

# ================= IOC MANAGEMENT =================
@router.get("/iocs")
def get_iocs(current_user: Dict[str, Any] = Depends(get_current_user)):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM iocs ORDER BY created_at DESC;")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@router.post("/iocs")
def add_ioc(req: IOCCreateRequest, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    conn = get_db_connection()
    c = conn.cursor()
    ioc_id = f"ioc-{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()
    c.execute("""
    INSERT INTO iocs (id, type, value, description, severity, source, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (ioc_id, req.type.upper(), req.value.strip(), req.description, req.severity, req.source or current_user["full_name"], now))
    conn.commit()
    conn.close()
    return {"id": ioc_id, "status": "CREATED"}

@router.delete("/iocs/{ioc_id}")
def delete_ioc(ioc_id: str, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN"]))):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM iocs WHERE id = ?;", (ioc_id,))
    conn.commit()
    conn.close()
    return {"status": "DELETED"}

# ================= PCAP OFFLINE ANALYSIS =================
@router.post("/pcap/analyze")
async def analyze_pcap(
    file: Optional[UploadFile] = File(None),
    use_sample: bool = Form(False),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    if use_sample or not file:
        sample_path = SAMPLE_DATA_DIR / "sample_traffic.pcap"
        if not sample_path.exists():
            from sample_data.generate_sample_pcap import create_sample_pcap
            create_sample_pcap(str(sample_path))
        target_path = str(sample_path)
        filename = "sample_traffic.pcap"
    else:
        filename = file.filename
        target_path = str(SAMPLE_DATA_DIR / f"upload_{uuid.uuid4().hex[:6]}_{filename}")
        with open(target_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

    result = OfflinePCAPParser.parse_pcap(target_path)
    result["filename"] = filename
    result["analyzed_at"] = datetime.now(timezone.utc).isoformat()

    AuditService.log_event(
        actor_name=current_user["full_name"],
        actor_role=current_user["role"],
        action="PCAP_ANALYSIS",
        resource_type="PCAP",
        details=f"Analyzed PCAP file '{filename}'. Found {result.get('total_packets', 0)} frames."
    )

    return result

# ================= SECURITY COMPATIBILITY LAYER =================
@router.get("/security/compatibility")
def get_security_status(case_id: Optional[str] = None, current_user: Dict[str, Any] = Depends(get_current_user)):
    events = SecurityCompatibilityManager.get_security_events(case_id)
    return {
        "framework": "NTRO SIH26148 Security Compatibility Layer",
        "active_policy": "FORENSIC_READ_ONLY",
        "investigator_badge": current_user.get("badge_number", "NTRO-INV-42"),
        "authorization_level": current_user.get("role", "INVESTIGATOR"),
        "tamper_protection": "ENABLED",
        "edr_simulation_status": "READY",
        "recent_security_events": events
    }

@router.post("/security/simulate")
def simulate_security_event(req: SecuritySimulateRequest, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    return SecurityCompatibilityManager.evaluate_execution(
        mode=req.mode,
        script_content=req.script,
        user_info=current_user,
        case_id=req.case_id or "DEMO"
    )

# ================= HEALTH & MAINTENANCE =================
@router.get("/health")
def api_health():
    return {
        "status": "HEALTHY",
        "service": "NTRO Cyber Forensics Platform API",
        "version": "2.4.0",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.post("/cases/{case_id}/deduplicate")
def deduplicate_case_data(case_id: str, current_user: Dict[str, Any] = Depends(require_roles(["ADMIN", "INVESTIGATOR"]))):
    from ..database import deduplicate_database
    deduplicate_database()
    return {"status": "SUCCESS", "message": "Case evidence, custody records, and reports deduplicated."}

