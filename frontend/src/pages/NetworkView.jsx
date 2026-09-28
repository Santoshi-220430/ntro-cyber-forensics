import React, { useState, useEffect } from 'react';
import { Network as NetworkIcon, Search, AlertTriangle, RefreshCw, CheckCircle2, Globe } from 'lucide-react';
import { apiRequest } from '../api';

export default function NetworkView({ activeCase }) {
  const [connections, setConnections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchNetwork = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/network`);
      setConnections(data);
    } catch (err) {
      console.error("Failed to load network connections:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNetwork();
  }, [activeCase]);

  const filtered = connections.filter(c =>
    (c.remote_address && c.remote_address.includes(search)) ||
    (c.process_name && c.process_name.toLowerCase().includes(search.toLowerCase())) ||
    c.local_port.toString().includes(search) ||
    (c.remote_port && c.remote_port.toString().includes(search))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <NetworkIcon className="w-5 h-5 text-sky-400" />
            <span>ACTIVE NETWORK SOCKETS & TELEMETRY</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Endpoint Network Connections, Remote Sockets, Bound Ports & C2 Threat Intel Cross-Correlation
          </p>
        </div>

        <button
          onClick={fetchNetwork}
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
          placeholder="Filter by remote IP, process, or port..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Network Connections Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">LOCAL ENDPOINT</th>
                <th className="p-3">REMOTE ENDPOINT</th>
                <th className="p-3">PROTOCOL</th>
                <th className="p-3">SOCKET STATE</th>
                <th className="p-3">PID / PROCESS</th>
                <th className="p-3">SECURITY ASSESSMENT</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Acquiring network sockets...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No active sockets cataloged. Execute <code>GET NETWORK</code> in the Forensic Console.
                  </td>
                </tr>
              ) : (
                filtered.map((c) => (
                  <tr key={c.id} className={`hover:bg-soc-card/40 transition-colors ${
                    c.is_suspicious ? "bg-rose-950/20" : ""
                  }`}>
                    <td className="p-3 font-semibold text-white">
                      {c.local_address}:{c.local_port}
                    </td>
                    <td className="p-3">
                      <div className="font-bold flex items-center space-x-1.5 text-sky-400">
                        <Globe className="w-3.5 h-3.5" />
                        <span>{c.remote_address ? `${c.remote_address}:${c.remote_port}` : 'LISTENING'}</span>
                      </div>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 text-[10px] font-bold">
                        {c.protocol}
                      </span>
                    </td>
                    <td className="p-3 text-soc-muted">{c.state}</td>
                    <td className="p-3">
                      <span className="text-white font-bold">{c.process_name}</span>{" "}
                      <span className="text-soc-muted font-mono">({c.pid})</span>
                    </td>
                    <td className="p-3">
                      {c.is_suspicious === 1 ? (
                        <div className="space-y-0.5">
                          <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 text-[10px] font-bold">
                            C2 ALERT
                          </span>
                          <div className="text-[10px] text-rose-300 font-sans">{c.suspicious_reason}</div>
                        </div>
                      ) : (
                        <span className="px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 text-[10px] font-bold">
                          NORMAL
                        </span>
                      )}
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
