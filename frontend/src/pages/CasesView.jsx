import React, { useState } from 'react';
import { FolderLock, Plus, Server, RefreshCw, CheckCircle2, User, Globe, ArrowRight } from 'lucide-react';
import { apiRequest } from '../api';

export default function CasesView({ cases, activeCase, onSelectCase, onRefreshCases }) {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    case_number: `CASE-2026-${Math.floor(100 + Math.random() * 900)}`,
    title: '',
    description: '',
    target_host: 'WS-FIN-05.fin.local',
    mode: 'DEMO'
  });
  const [creating, setCreating] = useState(false);

  const handleCreateCase = async (e) => {
    e.preventDefault();
    setCreating(true);
    try {
      const res = await apiRequest('/cases', {
        method: 'POST',
        body: formData
      });
      setShowCreateModal(false);
      setFormData({
        case_number: `CASE-2026-${Math.floor(100 + Math.random() * 900)}`,
        title: '',
        description: '',
        target_host: 'WS-FIN-05.fin.local',
        mode: 'DEMO'
      });
      if (onRefreshCases) onRefreshCases();
    } catch (err) {
      console.error("Failed to create case:", err);
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <FolderLock className="w-5 h-5 text-sky-400" />
            <span>CASE MANAGEMENT & INVESTIGATION REGISTRY</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Registered Cyber Forensics Engagements, Target Host Metadata & Mode Configuration
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onRefreshCases}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-sky-500/20"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Create New Case</span>
          </button>
        </div>
      </div>

      {/* Cases Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cases.map((c) => {
          const isSelected = activeCase?.id === c.id;
          return (
            <div
              key={c.id}
              onClick={() => onSelectCase(c)}
              className={`p-5 rounded-xl border transition-all cursor-pointer bg-soc-surface relative flex flex-col justify-between space-y-4 ${
                isSelected
                  ? 'border-sky-500 ring-1 ring-sky-500 shadow-lg shadow-sky-500/10'
                  : 'border-soc-border hover:border-slate-600'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2">
                  <span className="text-xs font-mono font-bold text-sky-400 bg-sky-950 px-2 py-0.5 rounded border border-sky-800">
                    {c.case_number}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                      {c.mode || 'DEMO'}
                    </span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-950 text-emerald-400 border border-emerald-800 font-bold">
                      {c.status}
                    </span>
                  </div>
                </div>

                <h3 className="text-sm font-bold text-white tracking-wide mt-2">
                  {c.title}
                </h3>
                <p className="text-xs text-soc-muted line-clamp-2 mt-1">
                  {c.description || 'No detailed case scope provided.'}
                </p>
              </div>

              <div className="pt-3 border-t border-soc-border space-y-2 text-xs font-mono text-soc-muted">
                <div className="flex justify-between items-center">
                  <span>Target Host:</span>
                  <span className="text-sky-300 font-bold flex items-center space-x-1">
                    <Server className="w-3.5 h-3.5" />
                    <span>{c.target_host || 'N/A'}</span>
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Lead Examiner:</span>
                  <span className="text-white font-semibold">{c.investigator_name || 'Lead DFIR'}</span>
                </div>
                <div className="flex justify-between items-center pt-2">
                  <div className="text-[11px] text-soc-muted">
                    {c.evidence_count || 0} Artifacts • {c.findings_count || 0} Findings
                  </div>
                  {isSelected ? (
                    <span className="text-emerald-400 font-bold flex items-center space-x-1 text-[11px]">
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>ACTIVE CONTEXT</span>
                    </span>
                  ) : (
                    <span className="text-sky-400 text-[11px] flex items-center space-x-1">
                      <span>Switch Context</span>
                      <ArrowRight className="w-3 h-3" />
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Create Case Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-soc-surface border border-soc-border rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
              <FolderLock className="w-4 h-4 text-sky-400" />
              <span>INITIALIZE FORENSIC CASE</span>
            </h3>

            <form onSubmit={handleCreateCase} className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-soc-muted mb-1">CASE REFERENCE NUMBER</label>
                <input
                  type="text"
                  required
                  value={formData.case_number}
                  onChange={(e) => setFormData({ ...formData, case_number: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-soc-muted mb-1">CASE TITLE</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Host Compromise & Exfiltration Investigation"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-soc-muted mb-1">TARGET HOSTNAME / IP</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. WS-FIN-05.fin.local"
                  value={formData.target_host}
                  onChange={(e) => setFormData({ ...formData, target_host: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-soc-muted mb-1">EXECUTION MODE</label>
                <select
                  value={formData.mode}
                  onChange={(e) => setFormData({ ...formData, mode: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                >
                  <option value="DEMO">DEMO / SYNTHETIC DATA (SIH Safe Evaluation)</option>
                  <option value="LIVE">LIVE AUDITED (Host Machine Read-Only Inspection)</option>
                </select>
              </div>

              <div>
                <label className="block text-soc-muted mb-1">INVESTIGATION SCOPE / DESCRIPTION</label>
                <textarea
                  rows={3}
                  placeholder="Describe suspicion, triage objective, or incident report..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-soc-border">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded bg-soc-bg text-soc-muted hover:text-white border border-soc-border"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={creating}
                  className="px-4 py-2 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold disabled:opacity-50"
                >
                  {creating ? "Creating..." : "Initialize Case"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
