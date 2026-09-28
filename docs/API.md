# Forensic Platform — REST API Reference
**Problem ID: SIH26148 | NTRO Cyber Forensics Prototype**

Base URL: `http://127.0.0.1:8000/api`  
Interactive OpenAPI Documentation (Swagger UI): `http://127.0.0.1:8000/docs`

---

## 1. Authentication Endpoints

### `POST /auth/login`
Authenticates an investigator and issues a JWT bearer token.
- **Request Body:**
  ```json
  {
    "username": "investigator",
    "password": "Forensic@123"
  }
  ```
- **Response (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
      "id": "usr-investigator",
      "username": "investigator",
      "role": "INVESTIGATOR",
      "full_name": "Lead DFIR Analyst",
      "badge_number": "NTRO-INV-42"
    }
  }
  ```

### `GET /auth/me`
Returns profile details of the authenticated investigator.
- **Headers:** `Authorization: Bearer <token>`

---

## 2. Case Management Endpoints

### `GET /cases`
Lists all registered investigation cases with artifact counts.

### `POST /cases`
Creates a new forensic investigation case.
- **Request Body:**
  ```json
  {
    "case_number": "CASE-2026-002",
    "title": "Corporate Gateway Exfiltration Triage",
    "description": "Suspicious outbound beaconing investigation.",
    "target_host": "GW-SRV-01.local",
    "mode": "DEMO"
  }
  ```

### `GET /cases/{case_id}`
Returns details for a single case.

---

## 3. Forensic DSL Endpoints

### `POST /scripts/validate`
Validates DSL script syntax, allow-lists, and RBAC permissions without executing.
- **Request Body:**
  ```json
  {
    "script": "GET SYSTEM\nGET PROCESSES\nDELETE SYSTEM FILES",
    "case_id": "case-2026-001-uuid"
  }
  ```
- **Response:**
  ```json
  {
    "valid": false,
    "errors": [
      {
        "message": "COMMAND BLOCKED: 'DELETE SYSTEM FILES'. Reason: Destructive or mutating operation 'DELETE' is prohibited by forensic integrity rules",
        "line": 3,
        "col": 1,
        "severity": "ERROR",
        "code": "DESTRUCTIVE_COMMAND_BLOCKED"
      }
    ]
  }
  ```

### `POST /scripts/execute`
Executes an allowed Forensic DSL script under the chosen security compatibility profile.
- **Request Body:**
  ```json
  {
    "script": "GET SYSTEM\nGET PROCESSES\nBUILD TIMELINE\nANALYZE\nGENERATE REPORT",
    "case_id": "case-2026-001-uuid",
    "security_mode": "AUTHORIZED"
  }
  ```

---

## 4. Telemetry & Evidence Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/cases/{id}/system` | GET | System hardware, OS kernel & RAM diagnostics |
| `/cases/{id}/processes` | GET | Running process list with suspicious flags |
| `/cases/{id}/files` | GET | Catalog of inspected files with SHA-256 hashes |
| `/cases/{id}/network` | GET | Active network sockets & C2 connections |
| `/cases/{id}/logs` | GET | Normalized Windows & Sysmon security logs |
| `/cases/{id}/evidence` | GET | Complete evidence vault catalog |
| `/cases/{id}/evidence/verify` | POST | Performs cryptographic hash integrity check |
| `/cases/{id}/timeline` | GET | Correlated chronological event stream |
| `/cases/{id}/findings` | GET | Suspicious detection rule findings |
| `/cases/{id}/analyze` | POST | Re-evaluates rule-based detection engine |
| `/cases/{id}/chain-of-custody` | GET | Cryptographically-chained custody ledger |
| `/cases/{id}/report` | POST | Generates official PDF forensic report |
| `/reports/{id}/download` | GET | Streams generated PDF binary to browser |
| `/pcap/analyze` | POST | Parses offline PCAP packet captures |
| `/security/compatibility` | GET | Security compatibility status & EDR log |
| `/security/simulate` | POST | Simulates EDR interaction profiles |
| `/audit` | GET | Returns immutable audit log entries |
| `/iocs` | GET / POST | Threat IOC indicator management |
