import React, { useState, useEffect } from 'react';
import { Activity, Search, AlertTriangle, RefreshCw, CheckCircle2 } from 'lucide-react';
import { apiRequest } from '../api';

export default function ProcessesView({ activeCase }) {
  const [processes, setProcesses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchProcesses = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/processes`);
      setProcesses(data);
    } catch (err) {
      console.error("Failed to load processes:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProcesses();
  }, [activeCase]);

  const filtered = processes.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.pid.toString().includes(search) ||
    (p.cmdline && p.cmdline.toLowerCase().includes(search.toLowerCase())) ||
    (p.username && p.username.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <Activity className="w-5 h-5 text-sky-400" />
            <span>PROCESS EXECUTION & BEHAVIORAL INSPECTOR</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Running Process Hierarchy, Command Line Arguments, Memory Footprint & Anomaly Classification
          </p>
        </div>

        <button
          onClick={fetchProcesses}
          className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-3 text-soc-muted" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter by PID, process name, command line, or user..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Processes Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">PID / PPID</th>
                <th className="p-3">PROCESS NAME</th>
                <th className="p-3">USER ACCOUNT</th>
                <th className="p-3">RAM</th>
                <th className="p-3">COMMAND LINE INVOCATION</th>
                <th className="p-3">STATUS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Acquiring process table...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No process records cataloged. Execute <code>GET PROCESSES</code> in the Forensic Console.
                  </td>
                </tr>
              ) : (
                filtered.map((proc) => (
                  <tr key={proc.id} className={`hover:bg-soc-card/40 transition-colors ${
                    proc.is_suspicious ? "bg-rose-950/20" : ""
                  }`}>
                    <td className="p-3 font-bold text-sky-400">
                      {proc.pid} <span className="text-soc-muted font-normal">({proc.ppid})</span>
                    </td>
                    <td className="p-3">
                      <div className="font-bold text-white flex items-center space-x-2">
                        <span>{proc.name}</span>
                        {proc.is_suspicious === 1 && (
                          <span className="px-1.5 py-0.2 rounded bg-rose-950 text-rose-400 border border-rose-800 text-[10px]">
                            SUSPICIOUS
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-soc-muted truncate max-w-xs">{proc.exe_path}</div>
                    </td>
                    <td className="p-3 text-soc-muted">{proc.username || 'SYSTEM'}</td>
                    <td className="p-3 text-sky-300">{proc.memory_mb ? `${proc.memory_mb} MB` : 'N/A'}</td>
                    <td className="p-3 text-slate-300 font-mono text-[11px] max-w-md break-all">
                      {proc.cmdline || proc.name}
                      {proc.suspicious_reason && (
                        <div className="text-[10px] text-rose-400 font-sans mt-0.5 font-semibold">
                          ↳ {proc.suspicious_reason}
                        </div>
                      )}
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold">
                        {proc.status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
