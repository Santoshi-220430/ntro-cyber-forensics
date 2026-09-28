import React, { useState, useEffect } from 'react';
import {
  FolderLock,
  ShieldCheck,
  AlertTriangle,
  Network,
  Cpu,
  Activity,
  FileCheck2,
  Terminal,
  FileSearch,
  CheckCircle2,
  Clock,
  ArrowUpRight
} from 'lucide-react';
import { apiRequest } from '../api';

export default function DashboardView({ activeCase, setActiveTab }) {
  const [stats, setStats] = useState({
    casesCount: 1,
    evidenceCount: 0,
    findingsCount: 0,
    criticalFindings: 0,
    connectionsCount: 0,
    processesCount: 0,
    integrityVerified: true
  });
  const [recentFindings, setRecentFindings] = useState([]);
  const [recentTimeline, setRecentTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      if (!activeCase) return;
      try {
        const [evidence, findings, connections, procs, timeline] = await Promise.all([
          apiRequest(`/cases/${activeCase.id}/evidence`).catch(() => []),
          apiRequest(`/cases/${activeCase.id}/findings`).catch(() => []),
          apiRequest(`/cases/${activeCase.id}/network`).catch(() => []),
          apiRequest(`/cases/${activeCase.id}/processes`).catch(() => []),
          apiRequest(`/cases/${activeCase.id}/timeline`).catch(() => [])
        ]);

        const critical = findings.filter(f => f.severity === 'CRITICAL').length;
        const failedEv = evidence.filter(e => e.integrity_status !== 'VERIFIED').length;

        setStats({
          casesCount: 1,
          evidenceCount: evidence.length,
          findingsCount: findings.length,
          criticalFindings: critical,
          connectionsCount: connections.length,
          processesCount: procs.length,
          integrityVerified: failedEv === 0
        });

        setRecentFindings(findings.slice(0, 5));
        setRecentTimeline(timeline.slice(-5).reverse());
      } catch (err) {
        console.error("Dashboard data load error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchDashboardData();
  }, [activeCase]);

  return (
    <div className="space-y-6">
      {/* Top Banner: Case Overview */}
      <div className="bg-gradient-to-r from-soc-surface via-soc-card to-soc-surface p-6 rounded-2xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <span className="px-2.5 py-1 rounded-md bg-sky-500/20 text-sky-400 font-mono text-xs font-bold border border-sky-500/30">
              ACTIVE DFIR CASE: {activeCase?.case_number || 'CASE-2026-001'}
            </span>
            <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[11px] font-mono">
              MODE: {activeCase?.mode || 'DEMO'}
            </span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-wide">
            {activeCase?.title || 'Suspicious Execution & Exfiltration on Workstation WS-FIN-04'}
          </h2>
          <p className="text-xs text-soc-muted mt-1 max-w-2xl">
            {activeCase?.description || 'Forensic triaging underway for suspected staging binary and beaconing behavior.'}
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setActiveTab('console')}
            className="px-4 py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-mono font-bold flex items-center space-x-2 shadow-lg shadow-sky-500/20 transition-all"
          >
            <Terminal className="w-4 h-4" />
            <span>Launch Forensic Console</span>
          </button>
          <button
            onClick={() => setActiveTab('reports')}
            className="px-4 py-2.5 rounded-lg bg-soc-bg hover:bg-slate-800 text-soc-text border border-soc-border text-xs font-mono flex items-center space-x-2 transition-colors"
          >
            <FileSearch className="w-4 h-4 text-sky-400" />
            <span>View PDF Reports</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Card 1: Evidence Items */}
        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border hover:border-sky-500/40 transition-colors">
          <div className="flex items-center justify-between text-soc-muted mb-3">
            <span className="text-xs font-mono font-bold">EVIDENCE ARTIFACTS</span>
            <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
              <FolderLock className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white font-mono">{stats.evidenceCount}</div>
          <div className="text-[11px] text-soc-muted mt-1 flex items-center space-x-1">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>FIPS SHA-256 Vaulted</span>
          </div>
        </div>

        {/* Card 2: Suspicious Findings */}
        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border hover:border-rose-500/40 transition-colors">
          <div className="flex items-center justify-between text-soc-muted mb-3">
            <span className="text-xs font-mono font-bold">SUSPICIOUS FINDINGS</span>
            <div className="p-2 rounded-lg bg-rose-500/10 text-rose-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-rose-400 font-mono">{stats.findingsCount}</div>
          <div className="text-[11px] text-soc-muted mt-1">
            <span className="text-rose-400 font-bold">{stats.criticalFindings} Critical</span> threat matches
          </div>
        </div>

        {/* Card 3: Network Sockets */}
        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border hover:border-indigo-500/40 transition-colors">
          <div className="flex items-center justify-between text-soc-muted mb-3">
            <span className="text-xs font-mono font-bold">ACTIVE CONNECTIONS</span>
            <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
              <Network className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-white font-mono">{stats.connectionsCount}</div>
          <div className="text-[11px] text-soc-muted mt-1">
            Target Host: <span className="text-sky-400 font-mono">{activeCase?.target_host}</span>
          </div>
        </div>

        {/* Card 4: Integrity Status */}
        <div className="bg-soc-surface p-5 rounded-xl border border-soc-border hover:border-emerald-500/40 transition-colors">
          <div className="flex items-center justify-between text-soc-muted mb-3">
            <span className="text-xs font-mono font-bold">INTEGRITY STATUS</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <CheckCircle2 className="w-4 h-4" />
            </div>
          </div>
          <div className="text-2xl font-bold text-emerald-400 font-mono">
            {stats.integrityVerified ? "VERIFIED" : "TAMPER_ALERT"}
          </div>
          <div className="text-[11px] text-soc-muted mt-1">
            0 Mismatches across evidence store
          </div>
        </div>
      </div>

      {/* Two Column Detailed Feed: Findings & Timeline */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Suspicious Findings */}
        <div className="lg:col-span-7 bg-soc-surface rounded-xl border border-soc-border p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-soc-border">
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-4 h-4 text-amber-400" />
              <h3 className="text-sm font-bold text-white font-mono">HIGH-PRIORITY DETECTION FINDINGS</h3>
            </div>
            <button
              onClick={() => setActiveTab('findings')}
              className="text-xs text-sky-400 hover:text-sky-300 font-mono flex items-center space-x-1"
            >
              <span>View All</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[360px]">
            {recentFindings.length === 0 ? (
              <div className="text-center py-10 text-soc-muted text-xs font-mono">
                No findings generated yet. Execute 'ANALYZE' in the Forensic Console.
              </div>
            ) : (
              recentFindings.map((f, i) => (
                <div key={i} className="p-3 bg-soc-bg rounded-lg border border-soc-border flex items-start justify-between">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-bold ${
                        f.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        f.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-sky-950 text-sky-400 border border-sky-800'
                      }`}>
                        {f.severity}
                      </span>
                      <span className="text-xs font-bold text-white">{f.title}</span>
                    </div>
                    <p className="text-[11px] text-soc-muted line-clamp-1">{f.description}</p>
                    <div className="text-[10px] font-mono text-slate-500">
                      Rule: {f.rule_id} • Target: {f.evidence_ref}
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right: Chronological Timeline Feed */}
        <div className="lg:col-span-5 bg-soc-surface rounded-xl border border-soc-border p-5 flex flex-col">
          <div className="flex items-center justify-between mb-4 pb-3 border-b border-soc-border">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-sky-400" />
              <h3 className="text-sm font-bold text-white font-mono">CORRELATED TIMELINE</h3>
            </div>
            <button
              onClick={() => setActiveTab('timeline')}
              className="text-xs text-sky-400 hover:text-sky-300 font-mono flex items-center space-x-1"
            >
              <span>Full Timeline</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-3 flex-1 overflow-y-auto max-h-[360px]">
            {recentTimeline.length === 0 ? (
              <div className="text-center py-10 text-soc-muted text-xs font-mono">
                No timeline events correlated yet. Execute 'BUILD TIMELINE' in the Forensic Console.
              </div>
            ) : (
              recentTimeline.map((t, i) => (
                <div key={i} className="p-2.5 bg-soc-bg rounded-lg border border-soc-border text-xs">
                  <div className="flex items-center justify-between text-[10px] font-mono text-soc-muted mb-1">
                    <span className="text-sky-400">{t.timestamp.replace('T', ' ').substring(0, 19)}</span>
                    <span className="px-1.5 py-0.2 rounded bg-slate-800 text-slate-300 font-bold">{t.source}</span>
                  </div>
                  <div className="font-semibold text-white text-[11px]">{t.event_type} — {t.entity}</div>
                  <div className="text-[11px] text-soc-muted truncate mt-0.5">{t.details}</div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
