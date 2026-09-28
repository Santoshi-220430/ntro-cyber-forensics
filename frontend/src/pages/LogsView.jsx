import React, { useState, useEffect } from 'react';
import { FileText, Search, RefreshCw, AlertCircle } from 'lucide-react';
import { apiRequest } from '../api';

export default function LogsView({ activeCase }) {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const fetchLogs = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/logs`);
      setLogs(data);
    } catch (err) {
      console.error("Failed to load logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [activeCase]);

  const filtered = logs.filter(l => {
    const matchSearch =
      l.message.toLowerCase().includes(search.toLowerCase()) ||
      l.event_type.toLowerCase().includes(search.toLowerCase()) ||
      (l.user && l.user.toLowerCase().includes(search.toLowerCase()));
    const matchSeverity = severityFilter === 'ALL' || l.severity === severityFilter;
    return matchSearch && matchSeverity;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <FileText className="w-5 h-5 text-sky-400" />
            <span>NORMALIZED SECURITY & AUDIT EVENT LOGS</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Windows Security & Sysmon Event Ingestion into Standardized DFIR Schema
          </p>
        </div>

        <button
          onClick={fetchLogs}
          className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Ribbon */}
      <div className="bg-soc-surface p-4 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex items-center space-x-2">
          <span className="text-soc-muted">SEVERITY:</span>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-white focus:outline-none cursor-pointer"
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="INFO">Info</option>
          </select>
        </div>

        <div className="relative min-w-[260px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-soc-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search event logs..."
            className="w-full pl-8 pr-3 py-1.5 bg-soc-bg border border-soc-border rounded-lg text-white focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      {/* Logs Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">TIMESTAMP</th>
                <th className="p-3">SOURCE</th>
                <th className="p-3">EVENT TYPE</th>
                <th className="p-3">SEVERITY</th>
                <th className="p-3">ACCOUNT</th>
                <th className="p-3">MESSAGE DETAILS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Loading security log events...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No log events found. Execute <code>GET LOGS</code> in the Forensic Console.
                  </td>
                </tr>
              ) : (
                filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-soc-card/40 transition-colors">
                    <td className="p-3 text-sky-400 font-bold whitespace-nowrap">
                      {log.timestamp.replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="p-3 text-slate-300">{log.source}</td>
                    <td className="p-3 font-semibold text-white">{log.event_type}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        log.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        log.severity === 'MEDIUM' ? 'bg-yellow-950 text-yellow-400 border border-yellow-800' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {log.severity}
                      </span>
                    </td>
                    <td className="p-3 text-soc-muted">{log.user || 'N/A'}</td>
                    <td className="p-3 font-sans text-slate-300 max-w-lg">
                      {log.message}
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
