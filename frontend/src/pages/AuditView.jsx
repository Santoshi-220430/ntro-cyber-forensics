import React, { useState, useEffect } from 'react';
import { History, Search, RefreshCw, CheckCircle2, ShieldCheck, Lock } from 'lucide-react';
import { apiRequest } from '../api';

export default function AuditView() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchAudit = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/audit');
      setLogs(data);
    } catch (err) {
      console.error("Failed to load audit logs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  const filtered = logs.filter(l =>
    l.action.toLowerCase().includes(search.toLowerCase()) ||
    l.actor_name.toLowerCase().includes(search.toLowerCase()) ||
    (l.details && l.details.toLowerCase().includes(search.toLowerCase())) ||
    (l.digest && l.digest.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <History className="w-5 h-5 text-sky-400" />
            <span>IMMUTABLE FORENSIC AUDIT RECORD</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Tamper-Proof Audit Trail of Investigator Actions, Script Invocations & Access Verification
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-xs font-mono flex items-center space-x-2">
            <ShieldCheck className="w-4 h-4" />
            <span>AUDIT DIGEST: CRYPTOGRAPHICALLY SEALED</span>
          </div>
          <button
            onClick={fetchAudit}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-3 text-soc-muted" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter audit logs by action, investigator, or digest..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Audit Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">EVENT TIMESTAMP</th>
                <th className="p-3">INVESTIGATOR / ACTOR</th>
                <th className="p-3">OPERATION</th>
                <th className="p-3">STATUS</th>
                <th className="p-3">EVENT DETAILS</th>
                <th className="p-3">FIPS SHA-256 DIGEST</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Loading audit trail records...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No audit records match search query.
                  </td>
                </tr>
              ) : (
                filtered.map((log) => (
                  <tr key={log.id} className="hover:bg-soc-card/40 transition-colors">
                    <td className="p-3 text-soc-muted whitespace-nowrap">
                      {log.timestamp.replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="p-3">
                      <span className="font-bold text-white">{log.actor_name}</span>{" "}
                      <span className="text-[10px] text-sky-400">({log.actor_role})</span>
                    </td>
                    <td className="p-3 font-semibold text-white">{log.action}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        log.status === 'SUCCESS' ? 'bg-emerald-950 text-emerald-400 border border-emerald-800' :
                        log.status === 'SIMULATED_ALERT' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        'bg-amber-950 text-amber-400 border border-amber-800'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="p-3 text-slate-300 max-w-sm truncate">{log.details}</td>
                    <td className="p-3 text-indigo-300 font-mono text-[11px] truncate max-w-xs">
                      {log.digest}
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
