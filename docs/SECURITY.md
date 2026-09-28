# Forensic Platform Security & Coexistence Model
**Problem ID: SIH26148 | NTRO Cyber Forensics Prototype**

---

## 1. Compliance with the Problem Statement

The official problem statement for SIH26148 reads:
> *"Creation of scripts/functions with new programming language to commence Computer & Network forensic analysis without triggering security solutions."*

### What this platform DOES NOT do (Strict Safety Rules):
- It does **NOT** implement malware-style evasion techniques:
  - No direct syscall bypassing or API unhooking
  - No reflective DLL injection or process hollowing
  - No kernel exploitation or Bring Your Own Vulnerable Driver (BYOVD)
  - No credential dumping or LSASS memory scraping
  - No disabling or blinding of real Antivirus or EDR agents.

### What this platform DOES do (Defensible Forensic Prototype):
- Implements an **Authorized Forensic Coexistence Architecture**:
  1. **Investigator Identity & RBAC**: Every session is authenticated using PBKDF2 HMAC-SHA256 credentials and verified with cryptographic JWT tokens.
  2. **Allow-Listed Grammar**: The custom Forensic DSL only permits strictly read-only inspection operations. Destructive verbs (`DELETE`, `KILL`, `MODIFY`, `DROP`) are blocked at the compiler AST level.
  3. **Script Signing & Integrity**: Prior to execution, scripts are hashed (FIPS 180-4 SHA-256) and signed using an HMAC-SHA256 digital certificate tied to the investigator's badge number.
  4. **Security Policy Coordination**: Scripts declare policy compliance under `FORENSIC_READ_ONLY`. In an enterprise deployment, this allows security products (e.g., Windows Defender, CrowdStrike, SentinelOne) to register an authorized exemption token for the investigator's session.
  5. **Interactive Coexistence Simulator**: Demonstrates:
     - **NORMAL MODE**: Shows what happens when an uncoordinated, unsigned tool inspects memory (EDR behavioral watchdog flags an alert).
     - **SIMULATION MODE**: Visualizes the 5-step mutual authentication handshake between the EDR agent and the Forensic Platform.
     - **AUTHORIZED FORENSIC MODE**: Demonstrates clean, policy-compliant execution with zero security alerts and complete audit logging.

---

## 2. Evidence Integrity Standard

Evidence collected by the platform adheres to international digital forensics standards (ISO/IEC 27037:2012):

1. **Read-Only Preservation**: Target evidence files are never modified in place; they are replicated into a secured, isolated vault directory.
2. **Cryptographic Sealing**: Both primary **SHA-256** and legacy **MD5** hashes are calculated at the instant of acquisition.
3. **Cryptographic Chain of Custody**: Every custody handoff, analysis run, and report export is written to an immutable SQLite ledger where each record is cryptographically linked to the preceding entry hash:
   $$\text{Hash}_n = \text{SHA-256}(\text{ID}_n \parallel \text{Hash}_{n-1} \parallel \text{Timestamp} \parallel \dots)$$
4. **Instant Tamper Verification**: Any deviation between the current disk hash and the stored acquisition record immediately triggers an `INTEGRITY_VERIFICATION_FAILED` status.

---

## 3. Defense Against Hostile Inputs

- **Path Traversal Protection**: Directory traversal attempts (`..`, `../..`, `../../etc/shadow`) within DSL commands are trapped and rejected by `DSLValidator`.
- **No Arbitrary Shell Execution**: The platform never calls `os.system()`, `subprocess.Popen(shell=True)`, or raw shell interpreters with user-supplied text. All DSL commands are strictly parsed into AST statements and dispatched to vetted internal Python collectors.
- **Role Enforcement**: Viewers cannot trigger data collection, file scans, rule analyses, or report compilations.
