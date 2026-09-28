# NTRO Cyber Forensics Platform — System Architecture
**Problem ID: SIH26148**  
**Organization:** National Technical Research Organisation (NTRO)  
**Statement:** *"Creation of scripts/functions with new programming language to commence Computer & Network forensic analysis without triggering security solutions."*

---

## 1. Executive Architectural Overview

The platform addresses the critical challenge faced by national cybersecurity and digital forensics teams: **legitimate forensic acquisition tooling triggering Endpoint Detection & Response (EDR), Antivirus (AV), or Host Intrusion Prevention Systems (HIPS) alarms**, leading to blocked triage or false incident escalations.

Rather than implementing dangerous, non-defensible malware techniques (direct syscall evasion, unhooking, reflective DLL injection, or BYOVD exploitation), this platform establishes a **cryptographically governed, policy-compliant coexistence model**:

```
                 ┌──────────────────────────────────────────────┐
                 │       AUTHORIZED INVESTIGATOR CONSOLE        │
                 │   (Web GUI / Terminal / Monospace Editor)    │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │           FORENSIC SCRIPTING DSL             │
                 │ (High-level, non-intrusive domain language)  │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │       LEXER / PARSER / AST VALIDATOR         │
                 │  - Allow-list verification                   │
                 │  - Destructive command blocker (e.g. DELETE) │
                 │  - Path traversal & sanitization check       │
                 │  - RBAC permission check (ADMIN/INV/VIEWER)  │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │        SECURITY COMPATIBILITY LAYER          │
                 │  - Investigator badge verification           │
                 │  - Script SHA-256 integrity hash             │
                 │  - HMAC-SHA256 digital signature             │
                 │  - Policy Enforcement: FORENSIC_READ_ONLY    │
                 │  - EDR Coexistence Simulation Engine         │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │               FORENSIC ENGINE                │
                 └──────┬───────────────┼───────────────┬───────┘
                        │               │               │
                        ▼               ▼               ▼
                 HOST SYSTEM       FILE SYSTEM       NETWORK
                 TELEMETRY         ACQUISITION      TELEMETRY
                 ────────────      ───────────      ─────────
                 • OS & Kernel     • Hashes (SHA)   • Active sockets
                 • CPU & Memory    • MACB times     • Remote IPs & C2
                 • Processes       • Metadata       • DNS telemetry
                 • Windows Logs    • Read-only copy • Offline PCAP
                        │               │               │
                        └───────────────┼───────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │          EVIDENCE INTEGRITY VAULT            │
                 │  • Read-only artifact isolation              │
                 │  • FIPS 180-4 SHA-256 sealing                │
                 │  • Dual-hash legacy MD5 calculation          │
                 │  • Cryptographic verification on demand      │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │     TIMELINE & CORRELATION ENGINE            │
                 │  • Normalized chronological event stream     │
                 │  • Files + Processes + Network + Logs        │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │    RULE-BASED FORENSIC ANALYSIS & IOCS       │
                 │  • Suspicious binary in Temp/AppData path    │
                 │  • Obfuscated PowerShell execution           │
                 │  • Outbound C2 socket to untrusted IP/port   │
                 │  • Threat Intel IOC cross-matching           │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │          CHAIN OF CUSTODY LEDGER             │
                 │  • Tamper-evident hash-chained entries       │
                 │  • Signed investigator attribution           │
                 └──────────────────────┬───────────────────────┘
                                        │
                                        ▼
                 ┌──────────────────────────────────────────────┐
                 │      OFFICIAL FORENSIC REPORT ENGINE         │
                 │  • ReportLab vector PDF compilation          │
                 │  • Cryptographic document seal (SHA-256)     │
                 │  • Executive summary, findings & attestation │
                 └──────────────────────────────────────────────┘
```

---

## 2. Component Directory Architecture

```
forensic-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── endpoints.py        # Complete REST API router
│   │   ├── auth/
│   │   │   └── auth_service.py     # JWT & PBKDF2 authentication, RBAC
│   │   ├── audit/
│   │   │   └── audit_service.py    # Immutable audit logging with SHA-256 seal
│   │   ├── evidence/
│   │   │   ├── evidence_service.py # Evidence vault & integrity verification
│   │   │   └── chain_of_custody.py # Cryptographically chained custody ledger
│   │   ├── forensic/
│   │   │   └── collectors.py       # Safe system, process, file, network & PCAP collectors
│   │   ├── timeline/
│   │   │   └── timeline_service.py # Multi-source chronological correlation engine
│   │   ├── analysis/
│   │   │   └── analysis_engine.py  # Deterministic detection rules & IOC matcher
│   │   ├── reports/
│   │   │   └── report_generator.py # ReportLab PDF report generation
│   │   ├── security/
│   │   │   └── compatibility.py    # Security Compatibility Layer & EDR simulator
│   │   ├── config.py               # Platform settings & directory layout
│   │   ├── database.py             # SQLite schema, WAL mode, default seeding
│   │   └── main.py                 # FastAPI application root & middleware
│   └── requirements.txt
│
├── forensic_dsl/
│   ├── __init__.py                 # Package exports
│   ├── tokens.py                   # Token types, keywords, allowed/blocked verbs
│   ├── lexer.py                    # Custom lexical analyzer with position tracking
│   ├── ast_nodes.py                # AST statement node definitions
│   ├── parser.py                   # Recursive descent parser
│   ├── validator.py                # AST policy & permission enforcement
│   └── interpreter.py              # Execution engine coordinating collectors & vault
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx          # Top SOC navigation, status pills, profile
│   │   │   └── Sidebar.jsx         # Sectioned cybersecurity menu
│   │   ├── pages/
│   │   │   ├── LoginView.jsx       # Auth portal with 1-click jury presets
│   │   │   ├── DashboardView.jsx   # Metrics, KPI cards, real-time telemetry
│   │   │   ├── ConsoleView.jsx     # Split DSL editor & live terminal console
│   │   │   ├── CasesView.jsx       # Case management & target host setup
│   │   │   ├── SystemView.jsx      # Host architecture & memory profile
│   │   │   ├── ProcessesView.jsx   # Process hierarchy & anomaly inspector
│   │   │   ├── FilesView.jsx       # File system explorer & MACB metadata
│   │   │   ├── NetworkView.jsx     # Active sockets & C2 exfiltration detection
│   │   │   ├── LogsView.jsx        # Normalized event logs
│   │   │   ├── PCAPView.jsx        # Offline PCAP packet analyzer
│   │   │   ├── TimelineView.jsx    # Unified multi-source event timeline
│   │   │   ├── EvidenceView.jsx    # Evidence vault & live hash verifier
│   │   │   ├── ChainOfCustodyView.jsx # Cryptographically linked chain of custody
│   │   │   ├── FindingsView.jsx    # Rule-based threat detections
│   │   │   ├── IOCView.jsx         # Threat intel indicator manager
│   │   │   ├── SecurityCompatibilityView.jsx # EDR coexistence demonstration
│   │   │   ├── ReportsView.jsx     # PDF report compiler & download
│   │   │   └── AuditView.jsx       # Immutable audit log
│   │   ├── context/
│   │   │   └── AuthContext.jsx     # Session & RBAC state provider
│   │   ├── api.js                  # Centralized REST client
│   │   ├── App.jsx                 # Application root & tab routing
│   │   ├── main.jsx                # DOM entrypoint
│   │   └── index.css               # SOC dark design system
│   ├── tailwind.config.js          # SOC theme tokens
│   ├── package.json
│   └── vite.config.js
│
├── sample_data/
│   ├── sample_traffic.pcap         # Valid synthetic libpcap capture
│   └── generate_sample_pcap.py     # Deterministic PCAP generator script
│
├── tests/
│   ├── test_dsl.py                 # Unit tests for Lexer, Parser, AST, Validator
│   ├── test_full_pipeline.py       # Integration test for end-to-end execution
│   └── test_api.py                 # FastAPI TestClient endpoint integration suite
│
└── README.md
```

---

## 3. Data Integrity & Chain of Custody Model

For any digital evidence to be admissible in a court of law or government tribunal, evidence integrity is non-negotiable.

1. **Acquisition Phase**: When an evidence artifact is acquired (via `GET FILES`, `GET SYSTEM`, or manual upload), a FIPS 180-4 **SHA-256** digest and legacy **MD5** digest are immediately computed.
2. **Vault Isolation**: Physical/logical files are copied into `evidence_vault/` and marked with read-only attributes.
3. **Chain of Custody Linking**:
   Each custody action generates an entry with:
   $$\text{Hash}_n = \text{SHA-256}(\text{ID}_n \parallel \text{Hash}_{n-1} \parallel \text{CaseID} \parallel \text{Action} \parallel \text{Actor} \parallel \text{Timestamp} \parallel \text{Details})$$
   This forms a cryptographic hash-chain where modifying any historical record invalidates all subsequent entries.
4. **On-Demand Verification**: When `VERIFY INTEGRITY` is executed, the engine re-reads every file on disk, recomputes the SHA-256 digest, and compares it with the acquisition record. Any mismatch immediately triggers an `INTEGRITY_VERIFICATION_FAILED` status.
