import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  AlertTriangle,
  Play,
  CheckCircle2,
  Lock,
  Cpu,
  Layers,
  FileCheck,
  Terminal,
  Activity,
  ArrowRight
} from 'lucide-react';
import { apiRequest } from '../api';

export default function SecurityCompatibilityView({ activeCase }) {
  const [securityStatus, setSecurityStatus] = useState(null);
  const [selectedMode, setSelectedMode] = useState("AUTHORIZED");
  const [simulationScript, setSimulationScript] = useState("GET SYSTEM\nGET PROCESSES\nGET NETWORK");
  const [simulationResult, setSimulationResult] = useState(null);
  const [running, setRunning] = useState(false);

  useEffect(() => {
    async function loadStatus() {
      try {
        const res = await apiRequest('/security/compatibility');
        setSecurityStatus(res);
      } catch (err) {
        console.error("Failed to load security status:", err);
      }
    }
    loadStatus();
  }, []);

  const handleSimulate = async () => {
    setRunning(true);
    try {
      const res = await apiRequest('/security/simulate', {
        method: 'POST',
        body: {
          mode: selectedMode,
          script: simulationScript,
          case_id: activeCase?.id
        }
      });
      setSimulationResult(res);

      // Refresh recent security events
      const updated = await apiRequest('/security/compatibility');
      setSecurityStatus(updated);
    } catch (err) {
      console.error("Simulation error:", err);
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: SIH26148 Architectural Explanation */}
      <div className="bg-gradient-to-r from-soc-surface via-soc-card to-soc-surface p-6 rounded-2xl border border-soc-border">
        <div className="flex items-center space-x-2 text-sky-400 font-mono text-xs font-bold mb-2">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>SIH26148 NTRO REQUIREMENT IMPLEMENTATION</span>
        </div>
        <h2 className="text-xl font-bold text-white tracking-wide">
          Security-Compatibility & Authorized Forensic Coexistence Layer
        </h2>
        <p className="text-xs text-soc-muted mt-2 max-w-3xl leading-relaxed">
          Forensic investigations on modern enterprise endpoints frequently collide with Endpoint Detection & Response (EDR)
          and Antivirus systems. Rather than resorting to dangerous malware-style evasion (unhooking, direct syscalls, reflective injection),
          this platform demonstrates a <b>defensible architectural coexistence model</b>: authorized execution, allow-listed read-only DSL commands,
          cryptographic script signing, and real-time policy coordination.
        </p>
      </div>

      {/* Core Architectural Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border space-y-2">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 text-sky-400 flex items-center justify-center font-bold font-mono">
            01
          </div>
          <h3 className="text-sm font-bold text-white font-mono">CRYPTOGRAPHIC AUTHORIZATION</h3>
          <p className="text-xs text-soc-muted leading-relaxed">
            Every script execution requires an authenticated investigator badge and produces an HMAC-SHA256 digital signature
            before any forensic collector runs.
          </p>
        </div>

        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border space-y-2">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold font-mono">
            02
          </div>
          <h3 className="text-sm font-bold text-white font-mono">READ-ONLY KERNEL POLICY</h3>
          <p className="text-xs text-soc-muted leading-relaxed">
            Forensic DSL operates strictly under <code>FORENSIC_READ_ONLY</code>. Destructive actions (process killing, file deletion,
            memory modification) are rejected at the AST parser stage.
          </p>
        </div>

        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border space-y-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold font-mono">
            03
          </div>
          <h3 className="text-sm font-bold text-white font-mono">IMMUTABLE AUDIT TRAIL</h3>
          <p className="text-xs text-soc-muted leading-relaxed">
            Every inspection event is cryptographically sealed in the immutable audit log and chained into the evidence vault
            with FIPS 180-4 SHA-256 digests.
          </p>
        </div>
      </div>

      {/* Interactive EDR Simulation Sandbox */}
      <div className="bg-soc-surface rounded-2xl border border-soc-border p-6 space-y-6">
        <div className="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-soc-border">
          <div>
            <h3 className="text-base font-bold text-white font-mono flex items-center space-x-2">
              <Activity className="w-4 h-4 text-sky-400" />
              <span>LIVE SECURITY-CONTROL INTERACTION SIMULATOR</span>
            </h3>
            <p className="text-xs text-soc-muted mt-0.5">
              Demonstrate how different execution modes interact with endpoint security watchdogs
            </p>
          </div>

          {/* Mode Selector */}
          <div className="flex bg-soc-bg p-1 rounded-lg border border-soc-border text-xs font-mono">
            <button
              onClick={() => setSelectedMode("AUTHORIZED")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                selectedMode === "AUTHORIZED"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              AUTHORIZED MODE
            </button>
            <button
              onClick={() => setSelectedMode("SIMULATION")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                selectedMode === "SIMULATION"
                  ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              EDR HANDSHAKE SIMULATION
            </button>
            <button
              onClick={() => setSelectedMode("NORMAL")}
              className={`px-3 py-1.5 rounded-md font-semibold transition-all ${
                selectedMode === "NORMAL"
                  ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                  : "text-soc-muted hover:text-white"
              }`}
            >
              NORMAL (CHALLENGE TRIGGER)
            </button>
          </div>
        </div>

        {/* Script & Run */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-6 space-y-3">
            <label className="block text-xs font-mono text-soc-muted">
              TARGET FORENSIC DSL COMMANDS TO SUBMIT:
            </label>
            <textarea
              value={simulationScript}
              onChange={(e) => setSimulationScript(e.target.value)}
              rows={4}
              className="w-full p-3 bg-soc-bg border border-soc-border rounded-lg text-emerald-400 font-mono text-xs focus:outline-none focus:border-sky-500"
            />
            <button
              onClick={handleSimulate}
              disabled={running}
              className="w-full py-2.5 px-4 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-mono text-xs font-bold flex items-center justify-center space-x-2 transition-all shadow-md shadow-sky-500/20"
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{running ? "Simulating Interceptor Response..." : `Simulate [${selectedMode}] Execution`}</span>
            </button>
          </div>

          {/* Result Card */}
          <div className="lg:col-span-6 bg-soc-bg rounded-xl border border-soc-border p-4 min-h-[160px] flex flex-col justify-center font-mono text-xs">
            {!simulationResult ? (
              <div className="text-center text-soc-muted">
                Select an execution mode and click "Simulate" to observe the endpoint security watchdog response.
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between pb-2 border-b border-soc-border">
                  <span className="text-soc-muted">DECISION:</span>
                  <span className={`px-2 py-0.5 rounded font-bold ${
                    simulationResult.security_status === "AUTHORIZED" ? "bg-emerald-950 text-emerald-400 border border-emerald-800" :
                    simulationResult.security_status === "COMPATIBLE_SIMULATED" ? "bg-amber-950 text-amber-400 border border-amber-800" :
                    "bg-rose-950 text-rose-400 border border-rose-800"
                  }`}>
                    {simulationResult.security_status}
                  </span>
                </div>

                {simulationResult.simulated_alert && (
                  <div className="p-2.5 rounded bg-rose-950/40 border border-rose-800/80 text-rose-300">
                    <div className="font-bold flex items-center space-x-1.5 mb-1">
                      <AlertTriangle className="w-4 h-4 text-rose-400" />
                      <span>{simulationResult.simulated_alert}</span>
                    </div>
                    <div className="text-[11px] text-rose-200/80 mt-1">
                      Remedy: {simulationResult.remedy}
                    </div>
                  </div>
                )}

                {simulationResult.simulation_steps && (
                  <div className="space-y-1.5">
                    <div className="text-amber-400 font-bold text-[11px]">5-STEP EDR HANDSHAKE PIPELINE:</div>
                    {simulationResult.simulation_steps.map((st, i) => (
                      <div key={i} className="flex items-center space-x-2 text-[11px] text-slate-300">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span className="text-sky-400">[{st.agent}]</span>
                        <span>{st.message}</span>
                      </div>
                    ))}
                  </div>
                )}

                {simulationResult.mode === "AUTHORIZED" && (
                  <div className="space-y-1.5 text-slate-300">
                    <div className="flex items-center space-x-2 text-emerald-400 font-bold">
                      <CheckCircle2 className="w-4 h-4" />
                      <span>AUTHORIZED EXECUTION VERIFIED</span>
                    </div>
                    <div>Script Hash: <span className="text-sky-400">{simulationResult.script_hash?.substring(0, 24)}...</span></div>
                    <div>Digital Signature: <span className="text-indigo-400">{simulationResult.signature_status}</span></div>
                    <div>Active Policy: <span className="text-emerald-400">{simulationResult.policy}</span></div>
                    <div className="text-emerald-300/80 text-[11px] mt-1">
                      Zero security alerts generated. Operation audited and allowed under NTRO Protocol #402.
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Recent Security Simulation Events Table */}
        {securityStatus?.recent_security_events && (
          <div className="pt-4 border-t border-soc-border">
            <h4 className="text-xs font-mono text-soc-muted font-bold mb-3">RECENT SECURITY LOGGED EVENTS:</h4>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-soc-bg text-soc-muted border-b border-soc-border">
                  <tr>
                    <th className="p-2.5">TIMESTAMP</th>
                    <th className="p-2.5">MODE</th>
                    <th className="p-2.5">EVENT TYPE</th>
                    <th className="p-2.5">COMPONENT</th>
                    <th className="p-2.5">DECISION</th>
                    <th className="p-2.5">DETAILS</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-soc-border text-slate-300">
                  {securityStatus.recent_security_events.slice(0, 6).map((ev, i) => (
                    <tr key={i} className="hover:bg-soc-card/40 transition-colors">
                      <td className="p-2.5 text-soc-muted">{ev.timestamp?.substring(0, 19)}</td>
                      <td className="p-2.5">
                        <span className="px-1.5 py-0.5 rounded bg-slate-800 text-sky-400 font-bold">
                          {ev.mode}
                        </span>
                      </td>
                      <td className="p-2.5 text-white">{ev.event_type}</td>
                      <td className="p-2.5 text-sky-300">{ev.component}</td>
                      <td className="p-2.5">
                        <span className={`px-1.5 py-0.5 rounded font-bold ${
                          ev.decision === "ALLOWED" ? "bg-emerald-950 text-emerald-400" : "bg-rose-950 text-rose-400"
                        }`}>
                          {ev.decision}
                        </span>
                      </td>
                      <td className="p-2.5 text-soc-muted truncate max-w-xs">{ev.details}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
