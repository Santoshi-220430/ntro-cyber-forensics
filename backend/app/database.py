"""
Forensic Platform Database Management & Schema
Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
"""

import sqlite3
import os
import json
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from .config import DB_PATH

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    # PBKDF2 HMAC SHA-256 for secure password hashing
    salt = b"sih26148_ntro_salt"
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return key.hex()

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Enable WAL mode for high concurrency
    cursor.execute("PRAGMA journal_mode=WAL;")

    # 1. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL, -- ADMIN, INVESTIGATOR, VIEWER
        full_name TEXT NOT NULL,
        badge_number TEXT,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Cases
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id TEXT PRIMARY KEY,
        case_number TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL, -- ACTIVE, IN_PROGRESS, CLOSED, ARCHIVED
        investigator_id TEXT,
        investigator_name TEXT,
        target_host TEXT,
        mode TEXT DEFAULT 'DEMO', -- DEMO or LIVE
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 3. Scripts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scripts (
        id TEXT PRIMARY KEY,
        case_id TEXT,
        name TEXT NOT NULL,
        content TEXT NOT NULL,
        author_id TEXT,
        author_name TEXT,
        signature TEXT,
        integrity_hash TEXT NOT NULL,
        status TEXT DEFAULT 'VALIDATED',
        created_at TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 4. Script Executions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS script_executions (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        script_id TEXT,
        executor_id TEXT,
        executor_name TEXT,
        raw_script TEXT NOT NULL,
        status TEXT NOT NULL, -- SUCCESS, BLOCKED, FAILED
        output_logs TEXT,
        security_status TEXT NOT NULL, -- AUTHORIZED, BLOCKED, COMPATIBLE
        started_at TEXT NOT NULL,
        completed_at TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 5. Evidence
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS evidence (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        evidence_number TEXT NOT NULL,
        name TEXT NOT NULL,
        source_type TEXT NOT NULL, -- FILE, PROCESS, MEMORY, NETWORK, LOG
        file_path TEXT,
        file_size INTEGER,
        sha256_hash TEXT NOT NULL,
        md5_hash TEXT,
        mime_type TEXT,
        acquisition_timestamp TEXT NOT NULL,
        collector_id TEXT,
        collector_name TEXT,
        collection_method TEXT,
        integrity_status TEXT DEFAULT 'VERIFIED', -- VERIFIED, MISMATCH, TAMPERED
        metadata_json TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 6. System Information
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_info (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        os_name TEXT,
        os_version TEXT,
        hostname TEXT,
        username TEXT,
        architecture TEXT,
        cpu_count INTEGER,
        cpu_freq_mhz REAL,
        total_ram_gb REAL,
        available_ram_gb REAL,
        uptime_seconds REAL,
        boot_time TEXT,
        collected_at TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 7. Processes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS processes (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        pid INTEGER NOT NULL,
        ppid INTEGER,
        name TEXT NOT NULL,
        exe_path TEXT,
        cmdline TEXT,
        username TEXT,
        cpu_percent REAL,
        memory_mb REAL,
        start_time TEXT,
        status TEXT,
        is_suspicious INTEGER DEFAULT 0,
        suspicious_reason TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 8. Files
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        path TEXT NOT NULL,
        filename TEXT NOT NULL,
        extension TEXT,
        size_bytes INTEGER,
        created_time TEXT,
        modified_time TEXT,
        accessed_time TEXT,
        sha256 TEXT,
        md5 TEXT,
        is_suspicious INTEGER DEFAULT 0,
        suspicious_reason TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 9. Network Connections
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS network_connections (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        local_address TEXT NOT NULL,
        local_port INTEGER NOT NULL,
        remote_address TEXT,
        remote_port INTEGER,
        protocol TEXT NOT NULL,
        state TEXT,
        pid INTEGER,
        process_name TEXT,
        is_suspicious INTEGER DEFAULT 0,
        suspicious_reason TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 10. Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL,
        event_type TEXT NOT NULL,
        severity TEXT NOT NULL, -- INFO, LOW, MEDIUM, HIGH, CRITICAL
        user TEXT,
        host TEXT,
        message TEXT NOT NULL,
        raw_data TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 11. Timeline Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timeline_events (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        source TEXT NOT NULL, -- FILE, PROCESS, AUTH, NETWORK, LOG
        event_type TEXT NOT NULL,
        entity TEXT NOT NULL,
        details TEXT NOT NULL,
        severity TEXT DEFAULT 'INFO',
        evidence_id TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 12. Findings (Detection Rules Results)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS findings (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        title TEXT NOT NULL,
        severity TEXT NOT NULL, -- LOW, MEDIUM, HIGH, CRITICAL
        category TEXT NOT NULL, -- FILE, PROCESS, NETWORK, LOG, IOC
        description TEXT NOT NULL,
        evidence_ref TEXT,
        rule_id TEXT NOT NULL,
        rule_name TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 13. IOCs (Indicators of Compromise)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS iocs (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL, -- HASH, IP, DOMAIN, FILENAME
        value TEXT NOT NULL,
        description TEXT,
        severity TEXT DEFAULT 'HIGH',
        source TEXT DEFAULT 'INVESTIGATOR',
        created_at TEXT NOT NULL
    );
    """)

    # 14. Chain of Custody
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chain_of_custody (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        evidence_id TEXT,
        action TEXT NOT NULL,
        actor_name TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        details TEXT NOT NULL,
        integrity_hash TEXT NOT NULL,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 15. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        timestamp TEXT NOT NULL,
        actor_name TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        action TEXT NOT NULL,
        resource_type TEXT NOT NULL,
        resource_id TEXT,
        status TEXT NOT NULL, -- SUCCESS, BLOCKED, FAILURE
        details TEXT,
        ip_address TEXT,
        digest TEXT
    );
    """)

    # 16. Reports
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id TEXT PRIMARY KEY,
        case_id TEXT NOT NULL,
        report_number TEXT NOT NULL,
        title TEXT NOT NULL,
        format TEXT NOT NULL, -- PDF, JSON
        file_path TEXT,
        file_size INTEGER,
        sha256_hash TEXT NOT NULL,
        generated_by TEXT NOT NULL,
        generated_at TEXT NOT NULL,
        summary_json TEXT,
        FOREIGN KEY(case_id) REFERENCES cases(id)
    );
    """)

    # 17. Security Compatibility Simulation Events
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS security_events (
        id TEXT PRIMARY KEY,
        case_id TEXT,
        timestamp TEXT NOT NULL,
        mode TEXT NOT NULL, -- NORMAL, SIMULATION, AUTHORIZED
        event_type TEXT NOT NULL,
        component TEXT NOT NULL,
        policy_matched TEXT,
        decision TEXT NOT NULL, -- ALLOWED, BLOCKED, LOGGED, SIMULATED_ALERT
        audit_digest TEXT,
        details TEXT
    );
    """)

    conn.commit()
    conn.close()

def seed_default_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if default users already exist
    cursor.execute("SELECT COUNT(*) as cnt FROM users;")
    if cursor.fetchone()["cnt"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        users = [
            ("usr-admin", "admin", hash_password("Admin@NTRO2026"), "ADMIN", "Senior Forensics Lead", "NTRO-DIR-01", now),
            ("usr-investigator", "investigator", hash_password("Forensic@123"), "INVESTIGATOR", "Lead DFIR Analyst", "NTRO-INV-42", now),
            ("usr-viewer", "viewer", hash_password("Viewer@123"), "VIEWER", "Auditor / Reviewer", "NTRO-AUD-07", now),
        ]
        cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?)", users)

    # Seed Default IOCs
    cursor.execute("SELECT COUNT(*) as cnt FROM iocs;")
    if cursor.fetchone()["cnt"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        sample_iocs = [
            ("ioc-001", "HASH", "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "Empty file probe artifact", "LOW", "NTRO Threat Intel", now),
            ("ioc-002", "HASH", "8f4e2a6d5c1b9e0f3d7a8b4c2e6f1a9d8f4e2a6d5c1b9e0f3d7a8b4c2e6f1a9d", "CobaltStrike Beacon Synthetic Stager", "CRITICAL", "CERT-In Advisory", now),
            ("ioc-003", "IP", "198.51.100.45", "Suspicious C2 Server IP (FIN-APT29-Sim)", "HIGH", "NTRO Threat Intel", now),
            ("ioc-004", "IP", "203.0.113.88", "Known Exfiltration Endpoint", "CRITICAL", "Global Threat Exchange", now),
            ("ioc-005", "DOMAIN", "malicious-telemetry-sync.xyz", "Simulated DNS Exfiltration Domain", "HIGH", "NTRO Threat Intel", now),
            ("ioc-006", "FILENAME", "update_svc_helper.exe", "Masqueraded Persistence Binary", "HIGH", "Internal IOC Feed", now),
        ]
        cursor.executemany("INSERT INTO iocs VALUES (?, ?, ?, ?, ?, ?, ?)", sample_iocs)

    # Seed Demo Case CASE-2026-001 if not present
    cursor.execute("SELECT COUNT(*) as cnt FROM cases WHERE case_number = 'CASE-2026-001';")
    if cursor.fetchone()["cnt"] == 0:
        now = datetime.now(timezone.utc).isoformat()
        case_id = "case-2026-001-uuid"
        cursor.execute("""
        INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            "CASE-2026-001",
            "Suspicious Execution & Exfiltration on Workstation WS-FIN-04",
            "An employee finance workstation WS-FIN-04 is suspected of executing an unauthorized staging payload and initiating abnormal outbound network telemetry.",
            "ACTIVE",
            "usr-investigator",
            "Lead DFIR Analyst",
            "WS-FIN-04.fin.local",
            "DEMO",
            now,
            now
        ))

        # Add initial chain of custody entry
        cursor.execute("""
        INSERT INTO chain_of_custody VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "coc-001",
            case_id,
            None,
            "CASE_INITIALIZED",
            "Lead DFIR Analyst",
            "INVESTIGATOR",
            now,
            "Case CASE-2026-001 registered for digital forensics triaging under NTRO Protocol DFIR-7.",
            hashlib.sha256(f"CASE_INITIALIZED-{now}".encode()).hexdigest()
        ))

        # Add initial audit log
        cursor.execute("""
        INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "aud-001",
            now,
            "Lead DFIR Analyst",
            "INVESTIGATOR",
            "CASE_CREATE",
            "CASE",
            case_id,
            "SUCCESS",
            "Initialized case CASE-2026-001 with target WS-FIN-04",
            "127.0.0.1",
            hashlib.sha256(f"AUDIT-CASE-CREATE-{now}".encode()).hexdigest()
        ))

    conn.commit()
    conn.close()

    # Automatically purge duplicate records and keep canonical state
    deduplicate_database()

def deduplicate_database():
    """
    Ensures zero duplicate records across all core forensic tables:
    1. Evidence: Removes duplicate artifacts with the same name for a case, preserving unique records.
    2. Chain of Custody: Cleans identical consecutive duplicate entries.
    3. Reports: Keeps the latest 2 reports per case.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 1. Deduplicate Evidence
        cursor.execute("""
        DELETE FROM evidence 
        WHERE id NOT IN (
            SELECT MIN(id) FROM evidence GROUP BY case_id, name
        );
        """)

        # 2. Deduplicate Chain of Custody
        cursor.execute("""
        DELETE FROM chain_of_custody
        WHERE id NOT IN (
            SELECT MIN(id) FROM chain_of_custody GROUP BY case_id, action, details
        );
        """)

        # 3. Keep latest reports per case
        cursor.execute("""
        DELETE FROM reports WHERE id NOT IN (
            SELECT id FROM (
                SELECT id, ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY generated_at DESC) as rn FROM reports
            ) WHERE rn <= 2
        );
        """)

        conn.commit()
    except Exception as e:
        print(f"[-] Database deduplication notice: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    seed_default_data()
    print("Database initialized, seeded, and deduplicated successfully.")
