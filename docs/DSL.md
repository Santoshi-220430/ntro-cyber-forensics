# Forensic DSL (Domain-Specific Language) Reference
**Problem ID: SIH26148 | NTRO Cyber Forensics Prototype**

The **Forensic DSL** provides an intuitive, high-level grammar designed specifically for cyber-forensics investigators. It abstracts complex, low-level operating system APIs (Win32, Linux `/proc`, socket tables, event logs) into clear, auditable forensic commands while strictly preventing destructive mutations.

---

## 1. Syntax Overview

A Forensic DSL script consists of sequential commands, comments, and option blocks:

```dsl
# Comment lines start with '#' or '//'
CASE "CASE-2026-001"

SET MODE = "DEMO"
GET SYSTEM
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

---

## 2. Command Reference

### `CASE <string>`
Associates all subsequent forensic commands with a specific investigation case context.
- **Example:** `CASE "CASE-2026-001"`

### `SET <KEY> = <VALUE>`
Configures execution parameters.
- `SET MODE = "DEMO"` — Engages reproducible synthetic triage mode.
- `SET MODE = "LIVE"` — Engages safe live read-only system inspection.

### `GET <TARGET> [ARGUMENT] [OPTIONS]`
Performs read-only evidence acquisition for the target subsystem.
Allowed targets:
- `GET SYSTEM` — Collects OS name, architecture, CPU, memory, uptime, hostname.
- `GET USERS` — Inspects active logged-in user sessions.
- `GET PROCESSES` — Enumerates running processes, PIDs, parent PIDs, start times, command lines, memory.
- `GET SERVICES` — Queries installed background services.
- `GET NETWORK` or `GET CONNECTIONS` — Enumerates active network sockets, local/remote IP endpoints, ports, protocols, and socket states.
- `GET DNS` — Inspects DNS cache and resolver status.
- `GET LOGS` — Normalizes Windows Event Logs (4624, 4625, 7045, Sysmon) into standard schema.
- `GET FILES "<directory_path>"` — Acquires file metadata, MACB timestamps, and hashes in the target path.
- `GET PCAP "<filepath.pcap>"` — Reads an offline packet capture.

### `HASH <FILE|FILES> [PATH] [OPTIONS]`
Computes cryptographic integrity digests.
- `HASH FILES` — Calculates SHA-256 for all acquired case evidence.
- `HASH FILE "C:/path/file.exe" [ALGORITHM = "SHA256"]` — Computes hash for a specific file.

### `SEARCH <FILES|LOGS> "<keyword>" [PATH]`
Performs read-only inspection for indicators or filenames.
- **Example:** `SEARCH FILES "update_svc_helper.exe"`

### `BUILD TIMELINE`
Merges timestamps across file creation/modification, process spawns, network connections, and log events into a unified chronological sequence.

### `ANALYZE`
Triggers the deterministic rule engine to evaluate evidence against known attack patterns and Threat Intel IOCs:
- Suspicious binaries executing from `Temp` or `AppData`
- Hidden or encoded PowerShell downloads
- Outbound connections to unauthorized C2 IPs or suspicious ports (e.g. 4444, 8080)
- Brute-force authentication failures (Event 4625)

### `VERIFY INTEGRITY`
Recomputes SHA-256 hashes of all stored evidence items and compares them with their original acquisition records to detect tampering.

### `GENERATE REPORT [FORMAT]`
Compiles the complete investigation into an official signed PDF report.
- `GENERATE REPORT "PDF"`

---

## 3. Explicitly Blocked Destructive Verbs

To guarantee that forensic scripts cannot be weaponized or accidentally modify evidence systems, the DSL Lexer and AST Validator explicitly trap and reject the following destructive operations:

| Blocked Verb | Immediate Result | Safety Rationale |
|---|---|---|
| `DELETE` | **COMMAND BLOCKED** | Destructive deletion is prohibited by forensic integrity standards |
| `REMOVE` | **COMMAND BLOCKED** | Cannot delete files or evidence artifacts |
| `KILL` / `TERMINATE` | **COMMAND BLOCKED** | Mutating process states destroys live volatile memory evidence |
| `DROP` | **COMMAND BLOCKED** | Database drops are blocked |
| `MODIFY` / `UPDATE` | **COMMAND BLOCKED** | Evidence must remain read-only |
| `INJECT` / `HOOK` | **COMMAND BLOCKED** | Invasive memory modifications violate defensibility rules |
| `WIPE` | **COMMAND BLOCKED** | Anti-forensic commands are strictly forbidden |

### Example Blocked Execution:
```dsl
CASE "CASE-ATTACK"
DELETE SYSTEM FILES
```
**Parser/Validator Response:**
```
[!] COMMAND BLOCKED: 'DELETE SYSTEM FILES'.
    Reason: Destructive or mutating operation 'DELETE' is prohibited by forensic integrity rules.
    Code: DESTRUCTIVE_COMMAND_BLOCKED (Line 2, Col 1)
```

---

## 4. Role-Based Access Control (RBAC) in DSL

| Command Category | ADMIN | INVESTIGATOR | VIEWER / AUDITOR |
|---|:---:|:---:|:---:|
| `CASE` | Allowed | Allowed | Allowed |
| `GET <TARGET>` | Allowed | Allowed | Denied (`RBAC_PERMISSION_DENIED`) |
| `HASH FILES` | Allowed | Allowed | Allowed |
| `BUILD TIMELINE` | Allowed | Allowed | Denied |
| `ANALYZE` | Allowed | Allowed | Denied |
| `GENERATE REPORT` | Allowed | Allowed | Denied |
| `VERIFY INTEGRITY` | Allowed | Allowed | Allowed |
