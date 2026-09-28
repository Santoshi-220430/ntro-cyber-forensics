import React, { useState, useEffect } from 'react';
import { AlertTriangle, Play, RefreshCw, ShieldAlert, CheckCircle2, Search, Target } from 'lucide-react';
import { apiRequest } from '../api';

export default function FindingsView({ activeCase }) {
  const [findings, setFindings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [search, setSearch] = useState('');

  const fetchFindings = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/findings`);
      setFindings(data);
    } catch (err) {
      console.error("Failed to load findings:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFindings();
  }, [activeCase]);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      await apiRequest(`/cases/${activeCase.id}/analyze`, { method: 'POST' });
      fetchFindings();
    } catch (err) {
      console.error("Analysis failed:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const filtered = findings.filter(f =>
    f.title.toLowerCase().includes(search.toLowerCase()) ||
    f.description.toLowerCase().includes(search.toLowerCase()) ||
    f.rule_id.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>DETERMINISTIC FORENSIC DETECTION FINDINGS</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Rule-Based Expert Threat Detection & IOC Correlation (No Staged / Hallucinatory Models)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchFindings}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleRunAnalysis}
            disabled={analyzing}
            className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-sky-500/20 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{analyzing ? "Evaluating Detection Rules..." : "Re-Run Forensic Rule Engine"}</span>
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="relative max-w-md">
        <Search className="w-4 h-4 absolute left-3 top-3 text-soc-muted" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter findings by rule, artifact, or description..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Findings Cards Grid */}
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs bg-soc-surface rounded-xl border border-soc-border">
            Evaluating evidence store against detection rules...
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs bg-soc-surface rounded-xl border border-soc-border">
            No suspicious findings detected. Run <code>ANALYZE</code> in the Forensic Console.
          </div>
        ) : (
          filtered.map((finding) => (
            <div
              key={finding.id}
              className={`p-5 rounded-xl border transition-all bg-soc-surface ${
                finding.severity === 'CRITICAL' ? 'border-rose-900/60 hover:border-rose-600' :
                finding.severity === 'HIGH' ? 'border-amber-900/60 hover:border-amber-600' :
                'border-soc-border hover:border-sky-500/50'
              }`}
            >
              <div className="flex flex-wrap items-start justify-between gap-3 mb-3">
                <div className="flex items-center space-x-3">
                  <span className={`px-2.5 py-1 rounded text-xs font-mono font-bold ${
                    finding.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                    finding.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                    'bg-sky-950 text-sky-400 border border-sky-800'
                  }`}>
                    {finding.severity}
                  </span>
                  <span className="text-sm font-bold text-white tracking-wide">
                    {finding.title}
                  </span>
                </div>

                <div className="text-[11px] font-mono text-soc-muted flex items-center space-x-2">
                  <span>Category: <strong className="text-white">{finding.category}</strong></span>
                  <span>•</span>
                  <span>Detected: {finding.timestamp?.substring(0, 19)}</span>
                </div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed mb-4">
                {finding.description}
              </p>

              <div className="pt-3 border-t border-soc-border flex flex-wrap items-center justify-between gap-2 text-xs font-mono">
                <div className="text-soc-muted">
                  Rule ID: <span className="text-sky-400 font-semibold">{finding.rule_id}</span> ({finding.rule_name})
                </div>
                <div className="text-soc-muted">
                  Evidence Ref: <span className="text-amber-400 font-semibold">{finding.evidence_ref}</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
