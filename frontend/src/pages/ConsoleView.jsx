import React, { useState } from 'react';
import {
  Terminal as TerminalIcon,
  Play,
  CheckCircle2,
  AlertTriangle,
  FileCode,
  Shield,
  Copy,
  Trash2,
  Sliders,
  Download,
  Info
} from 'lucide-react';
import { apiRequest } from '../api';

const SCRIPT_PRESETS = {
  full: `# Full Forensic Investigation Workflow
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
VERIFY INTEGRITY`,

  quick_triage: `# Rapid Host Triage
CASE "CASE-2026-001"

GET SYSTEM
GET PROCESSES
GET USERS
ANALYZE`,

  network_focus: `# Network & Socket Inspection
CASE "CASE-2026-001"

GET NETWORK
GET CONNECTIONS
GET LOGS
BUILD TIMELINE`,

  destructive_test: `# Safety Test: Prohibited Destructive Operations
# Demonstrates how the Forensic DSL rejects harmful commands
CASE "CASE-2026-001"

DELETE SYSTEM FILES
KILL PROCESS 1337
WIPE LOGS`
};

export default function ConsoleView({ activeCase, onRefreshData }) {
  const [script, setScript] = useState(SCRIPT_PRESETS.full);
  const [securityMode, setSecurityMode] = useState("AUTHORIZED");
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState(null);
  const [terminalLogs, setTerminalLogs] = useState([
    "[*] NTRO Authorized Cyber Forensics Shell v2.4 initialized.",
    "[*] Active Policy: FORENSIC_READ_ONLY (FIPS 180-4 compliant).",
    `[+] Context linked to: ${activeCase?.case_number || 'CASE-2026-001'} (Target: ${activeCase?.target_host || 'WS-FIN-04'}).`,
    "[*] Ready for forensic DSL execution sequence..."
  ]);
  const [executionStats, setExecutionStats] = useState(null);

  const handleValidate = async () => {
    setValidating(true);
    setValidationResult(null);
    try {
      const res = await apiRequest('/scripts/validate', {
        method: 'POST',
        body: { script, case_id: activeCase?.id }
      });
      setValidationResult(res);
      if (res.valid) {
        setTerminalLogs(prev => [
          ...prev,
          `[+] Syntax & AST check passed: ${res.statements_count} executable statements verified.`
        ]);
      } else {
        setTerminalLogs(prev => [
          ...prev,
          ...res.errors.map(e => `[!] AST VALIDATION ERROR (Line ${e.line}): ${e.message}`)
        ]);
      }
    } catch (err) {
      setTerminalLogs(prev => [...prev, `[!] Validation check failed: ${err.message}`]);
    } finally {
      setValidating(false);
    }
  };

  const handleExecute = async () => {
    setLoading(true);
    setExecutionStats(null);
    setTerminalLogs(prev => [
      ...prev,
      "----------------------------------------------------------------",
      `[*] Commencing execution in [${securityMode}] mode...`
    ]);

    try {
      const res = await apiRequest('/scripts/execute', {
        method: 'POST',
        body: {
          script,
          case_id: activeCase?.id,
          security_mode: securityMode
        }
      });

      if (res.logs && res.logs.length > 0) {
        setTerminalLogs(prev => [...prev, ...res.logs]);
      }

      if (res.status === "SUCCESS") {
        setExecutionStats(res.results);
        if (onRefreshData) onRefreshData();
      } else if (res.status === "BLOCKED") {
        setTerminalLogs(prev => [
          ...prev,
          "[!] SCRIPT EXECUTION HALTED BY SECURITY POLICY ENFORCER."
        ]);
      }
    } catch (err) {
      setTerminalLogs(prev => [...prev, `[!] Execution Error: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  };

  const handleAppendCommand = (cmd) => {
    setScript(prev => `${prev.trim()}\n${cmd}`);
  };

  const handleClearLogs = () => {
    setTerminalLogs([
      "[*] Terminal logs cleared.",
      `[+] Active Context: ${activeCase?.case_number || 'CASE-2026-001'}`
    ]);
  };

  return (
    <div className="h-full flex flex-col space-y-4">
      {/* Top Header / Mode Ribbon */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-soc-surface p-4 rounded-xl border border-soc-border">
        <div className="flex items-center space-x-3">
          <div className="p-2 rounded-lg bg-sky-500/15 text-sky-400 border border-sky-500/30">
            <TerminalIcon className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white flex items-center space-x-2">
              <span>FORENSIC CONSOLE & SCRIPTING ENGINE</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-sky-950 text-sky-400 border border-sky-800">
                DSL INTERPRETER
              </span>
            </h2>
            <p className="text-xs text-soc-muted">
              Write or load domain-specific forensic commands with safe read-only execution
            </p>
          </div>
        </div>

        {/* Security Execution Mode Selector */}
        <div className="flex items-center space-x-3">
          <span className="text-xs font-mono text-soc-muted">EXECUTION PROFILE:</span>
          <div className="flex bg-soc-bg p-1 rounded-lg border border-soc-border text-xs font-mono">
            <button
              onClick={() => setSecurityMode("AUTHORIZED")}
              className={`px-3 py-1.5 rounded-md transition-all font-semibold ${
                securityMode === "AUTHORIZED"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-sm"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              AUTHORIZED MODE
            </button>
            <button
              onClick={() => setSecurityMode("SIMULATION")}
              className={`px-3 py-1.5 rounded-md transition-all font-semibold ${
                securityMode === "SIMULATION"
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-sm"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              EDR SIMULATION
            </button>
            <button
              onClick={() => setSecurityMode("NORMAL")}
              className={`px-3 py-1.5 rounded-md transition-all font-semibold ${
                securityMode === "NORMAL"
                  ? "bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-sm"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              NORMAL (CHALLENGE)
            </button>
          </div>
        </div>
      </div>

      {/* Main Split Grid: Editor (Left) & Terminal (Right) */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-4 min-h-[500px]">
        {/* Left Column: DSL Editor */}
        <div className="lg:col-span-6 bg-soc-surface rounded-xl border border-soc-border flex flex-col overflow-hidden">
          {/* Editor Header & Presets */}
          <div className="bg-soc-card/70 border-b border-soc-border px-4 py-3 flex items-center justify-between">
            <div className="flex items-center space-x-2 text-xs font-mono text-white font-semibold">
              <FileCode className="w-4 h-4 text-sky-400" />
              <span>FORENSIC_SCRIPT.FDS</span>
            </div>

            {/* Presets dropdown */}
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-mono text-soc-muted">Presets:</span>
              <select
                onChange={(e) => setScript(SCRIPT_PRESETS[e.target.value])}
                className="bg-soc-bg border border-soc-border text-xs rounded px-2 py-1 text-sky-400 font-mono focus:outline-none cursor-pointer"
              >
                <option value="full">Full Investigation Sequence</option>
                <option value="quick_triage">Rapid Host Triage</option>
                <option value="network_focus">Network & Socket Triage</option>
                <option value="destructive_test">Test Blocked Commands (Safety)</option>
              </select>
            </div>
          </div>

          {/* Text Area Code Editor */}
          <div className="flex-1 relative p-3 bg-[#0a0f1d]">
            <textarea
              value={script}
              onChange={(e) => setScript(e.target.value)}
              spellCheck="false"
              className="w-full h-full bg-transparent text-emerald-400 font-mono text-xs leading-relaxed focus:outline-none resize-none"
              placeholder="# Enter Forensic DSL commands here..."
            />
          </div>

          {/* Quick Autocomplete Buttons Bar */}
          <div className="px-3 py-2 bg-soc-surface border-t border-soc-border flex flex-wrap gap-1.5 items-center">
            <span className="text-[10px] font-mono text-soc-muted mr-1">ADD COMMAND:</span>
            {["GET SYSTEM", "GET PROCESSES", "GET NETWORK", "GET LOGS", "BUILD TIMELINE", "ANALYZE", "GENERATE REPORT"].map((cmd) => (
              <button
                key={cmd}
                onClick={() => handleAppendCommand(cmd)}
                className="text-[10px] font-mono px-2 py-0.5 rounded bg-soc-bg hover:bg-slate-800 text-sky-300 border border-soc-border transition-colors"
              >
                + {cmd}
              </button>
            ))}
          </div>

          {/* Editor Action Buttons */}
          <div className="p-3 bg-soc-card/50 border-t border-soc-border flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <button
                onClick={handleValidate}
                disabled={validating}
                className="px-3 py-2 rounded-lg bg-soc-bg hover:bg-slate-800 text-soc-muted hover:text-white border border-soc-border text-xs font-mono flex items-center space-x-1.5 transition-colors"
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span>{validating ? "Validating..." : "Validate AST"}</span>
              </button>

              {validationResult && (
                <span className={`text-[11px] font-mono px-2 py-1 rounded ${
                  validationResult.valid
                    ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800'
                    : 'bg-rose-950/80 text-rose-400 border border-rose-800'
                }`}>
                  {validationResult.valid ? "VALID SCRIPT" : "VALIDATION FAILED"}
                </span>
              )}
            </div>

            <button
              onClick={handleExecute}
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-mono text-xs font-bold flex items-center space-x-2 shadow-lg shadow-sky-500/20 transition-all disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{loading ? "Executing Pipeline..." : "Execute Forensic DSL"}</span>
            </button>
          </div>
        </div>

        {/* Right Column: Terminal Console */}
        <div className="lg:col-span-6 bg-[#070b14] rounded-xl border border-soc-border flex flex-col overflow-hidden shadow-inner">
          {/* Terminal Title Bar */}
          <div className="bg-[#0b1220] border-b border-soc-border px-4 py-2.5 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-2.5 h-2.5 rounded-full bg-rose-500/80"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-amber-500/80"></div>
              <div className="w-2.5 h-2.5 rounded-full bg-emerald-500/80"></div>
              <span className="text-xs font-mono text-slate-400 ml-2">NTRO-DFIR-TERMINAL://WS-FIN-04</span>
            </div>

            <button
              onClick={handleClearLogs}
              title="Clear terminal window"
              className="text-soc-muted hover:text-white p-1 rounded hover:bg-slate-800 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Terminal Output Log Area */}
          <div className="flex-1 p-4 font-mono text-xs overflow-y-auto space-y-1.5 text-slate-300">
            {terminalLogs.map((log, i) => {
              let color = "text-slate-300";
              if (log.startsWith("[+]")) color = "text-emerald-400 font-semibold";
              else if (log.startsWith("[*]")) color = "text-sky-400";
              else if (log.startsWith("[!]")) color = "text-rose-400 font-semibold";
              else if (log.startsWith("    [CRITICAL]")) color = "text-rose-400 font-bold";
              else if (log.startsWith("    [HIGH]")) color = "text-amber-400 font-semibold";
              else if (log.startsWith("    [SHA-256]")) color = "text-indigo-300";

              return (
                <div key={i} className={`${color} leading-relaxed break-all`}>
                  {log}
                </div>
              );
            })}
          </div>

          {/* Bottom Execution Stats Bar */}
          {executionStats && (
            <div className="p-3 bg-[#0d1627] border-t border-soc-border grid grid-cols-4 gap-2 text-center font-mono">
              <div className="p-1.5 rounded bg-soc-bg border border-soc-border">
                <div className="text-[10px] text-soc-muted">PROCESSES</div>
                <div className="text-sm font-bold text-sky-400">{executionStats.processes_count}</div>
              </div>
              <div className="p-1.5 rounded bg-soc-bg border border-soc-border">
                <div className="text-[10px] text-soc-muted">FILES</div>
                <div className="text-sm font-bold text-indigo-400">{executionStats.files_count}</div>
              </div>
              <div className="p-1.5 rounded bg-soc-bg border border-soc-border">
                <div className="text-[10px] text-soc-muted">FINDINGS</div>
                <div className="text-sm font-bold text-rose-400">{executionStats.findings_count}</div>
              </div>
              <div className="p-1.5 rounded bg-soc-bg border border-soc-border">
                <div className="text-[10px] text-soc-muted">INTEGRITY</div>
                <div className="text-sm font-bold text-emerald-400">
                  {executionStats.integrity_verified ? "PASSED" : "CHECK"}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
