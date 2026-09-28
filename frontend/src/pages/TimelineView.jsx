import React, { useState, useEffect } from 'react';
import { Clock, Filter, Search, RefreshCw, Activity, Files, Network, FileText, AlertTriangle } from 'lucide-react';
import { apiRequest } from '../api';

export default function TimelineView({ activeCase }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sourceFilter, setSourceFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [search, setSearch] = useState('');

  const fetchTimeline = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      let query = '';
      if (severityFilter !== 'ALL') query += `severity=${severityFilter}&`;
      if (sourceFilter !== 'ALL') query += `source=${sourceFilter}&`;
      const data = await apiRequest(`/cases/${activeCase.id}/timeline?${query}`);
      setEvents(data);
    } catch (err) {
      console.error("Failed to fetch timeline:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, [activeCase, sourceFilter, severityFilter]);

  const filtered = events.filter(e =>
    e.entity.toLowerCase().includes(search.toLowerCase()) ||
    e.details.toLowerCase().includes(search.toLowerCase()) ||
    e.event_type.toLowerCase().includes(search.toLowerCase())
  );

  const getSourceIcon = (src) => {
    switch (src) {
      case 'PROCESS': return <Activity className="w-3.5 h-3.5 text-sky-400" />;
      case 'FILE_SYSTEM': return <Files className="w-3.5 h-3.5 text-indigo-400" />;
      case 'NETWORK': return <Network className="w-3.5 h-3.5 text-emerald-400" />;
      case 'LOGS': return <FileText className="w-3.5 h-3.5 text-amber-400" />;
      default: return <Clock className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <Clock className="w-5 h-5 text-sky-400" />
            <span>UNIFIED MULTI-SOURCE FORENSIC TIMELINE</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Chronological Correlation of File Timestamps, Process Executions, Active Sockets, and System Events
          </p>
        </div>

        <button
          onClick={fetchTimeline}
          className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Filter Ribbon */}
      <div className="bg-soc-surface p-4 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4 text-xs font-mono">
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center space-x-2">
            <span className="text-soc-muted">SOURCE:</span>
            <select
              value={sourceFilter}
              onChange={(e) => setSourceFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-white focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Sources</option>
              <option value="PROCESS">Process Execution</option>
              <option value="FILE_SYSTEM">File System</option>
              <option value="NETWORK">Network Sockets</option>
              <option value="LOGS">Normalized Logs</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-soc-muted">SEVERITY:</span>
            <select
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value)}
              className="bg-soc-bg border border-soc-border rounded px-2.5 py-1.5 text-white focus:outline-none cursor-pointer"
            >
              <option value="ALL">All Severities</option>
              <option value="CRITICAL">Critical Only</option>
              <option value="HIGH">High</option>
              <option value="MEDIUM">Medium</option>
              <option value="LOW">Low</option>
              <option value="INFO">Info</option>
            </select>
          </div>
        </div>

        <div className="relative min-w-[240px]">
          <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-soc-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search timeline events..."
            className="w-full pl-8 pr-3 py-1.5 bg-soc-bg border border-soc-border rounded-lg text-white focus:outline-none focus:border-sky-500"
          />
        </div>
      </div>

      {/* Timeline Stream */}
      <div className="bg-soc-surface rounded-xl border border-soc-border p-6">
        {loading ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs">
            Correlating timeline events...
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs">
            No events match the current filter. Run <code>BUILD TIMELINE</code> in the Forensic Console.
          </div>
        ) : (
          <div className="relative border-l border-soc-border ml-3 space-y-4 pl-6 font-mono text-xs">
            {filtered.map((ev, i) => (
              <div key={i} className="relative group">
                {/* Node indicator */}
                <div className={`absolute -left-[30px] top-1.5 w-3 h-3 rounded-full border-2 ${
                  ev.severity === 'CRITICAL' ? 'bg-rose-500 border-rose-300 animate-ping' :
                  ev.severity === 'HIGH' ? 'bg-amber-500 border-amber-300' :
                  'bg-slate-700 border-slate-500'
                }`}></div>

                <div className="p-3 bg-soc-bg rounded-lg border border-soc-border hover:border-sky-500/40 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-2">
                  <div className="space-y-1">
                    <div className="flex items-center space-x-2">
                      <span className="text-sky-400 font-bold">{ev.timestamp.replace('T', ' ').substring(0, 19)} UTC</span>
                      <span className="flex items-center space-x-1 px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                        {getSourceIcon(ev.source)}
                        <span>{ev.source}</span>
                      </span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ev.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        ev.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {ev.severity}
                      </span>
                    </div>

                    <div className="text-white font-bold font-sans text-xs">
                      {ev.event_type} — <span className="text-sky-300">{ev.entity}</span>
                    </div>
                    <div className="text-soc-muted font-sans text-[11px] leading-relaxed">
                      {ev.details}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
