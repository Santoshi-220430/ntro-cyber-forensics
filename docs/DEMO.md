# SIH Jury Demonstration Script & Walkthrough
**Problem ID: SIH26148 | Organization: NTRO**

This guide provides a structured, 5-minute live demonstration workflow for the Smart India Hackathon jury.

---

## 1. Demo Scenario Overview

- **Case Number:** `CASE-2026-001`
- **Target Host:** `WS-FIN-04.fin.local` (Finance Department Workstation)
- **Incident Brief:** An employee workstation is suspected of executing an unauthorized staging payload and initiating abnormal outbound network telemetry to an external IP.

---

## 2. Step-by-Step Live Walkthrough

### STEP 1: Authentication & RBAC Gate
1. Navigate to `http://localhost:5173`.
2. Notice the dark SOC interface with NTRO Cyber Forensics branding.
3. Use the one-click quick login button: **INVESTIGATOR** (`investigator` / `Forensic@123`).
4. Point out to the jury: Access is strictly governed under role-based access control (ADMIN, INVESTIGATOR, AUDITOR/VIEWER).

### STEP 2: The Forensic Console & Scripting Engine
1. Click on **Forensic Console (DSL)** in the sidebar.
2. Show the custom Forensic DSL editor on the left and the interactive terminal on the right.
3. Select the preset **"Full Investigation Sequence"**:
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
4. Click **"Validate AST"**: Notice instant validation of allow-listed commands.
5. Click **"Execute Forensic DSL"**:
   - Watch the live terminal output scroll with green `[+]` success messages and cyan `[*]` telemetry lines.
   - Point out that within 3 seconds, all host telemetry, files, processes, active sockets, hashes, and timeline events are acquired.

### STEP 3: Demonstrating Destructive Command Safety Block
1. In the console preset dropdown, select **"Test Blocked Commands (Safety)"**:
   ```dsl
   CASE "CASE-2026-001"
   DELETE SYSTEM FILES
   KILL PROCESS 1337
   ```
2. Click **"Execute Forensic DSL"**:
   - The platform blocks execution immediately:
     `[!] COMMAND BLOCKED: 'DELETE SYSTEM FILES'. Reason: Destructive or mutating operation 'DELETE' is prohibited by forensic integrity rules.`
3. Explain to the jury: The language compiler explicitly protects system integrity and prevents evidence tampering.

### STEP 4: Demonstrating the Security Compatibility Layer (SIH Requirement)
1. Click on **Security Compatibility** in the sidebar.
2. Explain the core problem statement: *“Commencing computer and network forensic analysis without triggering security solutions.”*
3. Show the interactive simulator:
   - Select **NORMAL MODE** and click **Simulate**:
     - Result: `SIMULATED EDR ALERT: Unregistered forensic inspection tool invoked without cryptographic authorization token.`
   - Select **EDR HANDSHAKE SIMULATION** and click **Simulate**:
     - Visualizes the 5-step handshake between the EDR agent and the Forensic Platform.
   - Select **AUTHORIZED MODE** and click **Simulate**:
     - Result: `AUTHORIZED EXECUTION VERIFIED`. Digital signature matched, read-only policy active, zero alarms triggered!

### STEP 5: Correlated Forensic Evidence & Rule Engine Findings
1. Click on **Detection Findings**:
   - Observe deterministic findings:
     - `[CRITICAL] IOC Hash Match: CobaltStrike Beacon Synthetic Stager`
     - `[CRITICAL] IOC Outbound Network C2 Match: 198.51.100.45:4444`
     - `[HIGH] Obfuscated PowerShell Invocation Detected (PID:2104)`
     - `[HIGH] Executable in Monitored User Directory: update_svc_helper.exe`
2. Click on **Multi-Source Timeline**:
   - Point out how timestamps across file modification, process creation, network sockets, and authentication failures are correlated chronologically.

### STEP 6: Evidence Integrity & Chain of Custody
1. Click on **Evidence & Integrity**:
   - Show the FIPS 180-4 SHA-256 cryptographic digests for every artifact.
   - Click **"Verify All Evidence Integrity"**: Shows live re-computation and confirms `VERIFIED` (0 tampering).
2. Click on **Chain of Custody**:
   - Show the cryptographically linked ledger with sequential hash seals connecting every examiner action.

### STEP 7: One-Click Official PDF Forensic Report
1. Click on **Forensic PDF Reports**.
2. Click **"Generate Official Forensic Report"**.
3. Click **"Download PDF"**:
   - Open the generated PDF in the browser or PDF viewer.
   - Show the official header, case reference, executive summary, findings table, evidence inventory with SHA-256 hashes, chain of custody ledger, and examiner attestation.
