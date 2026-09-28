import React, { useState, useEffect } from 'react';
import { Link as LinkIcon, ShieldCheck, User, Clock, FileText, CheckCircle2 } from 'lucide-react';
import { apiRequest } from '../api';

export default function ChainOfCustodyView({ activeCase }) {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadChain() {
      if (!activeCase) return;
      setLoading(true);
      try {
        const data = await apiRequest(`/cases/${activeCase.id}/chain-of-custody`);
        setEntries(data);
      } catch (err) {
        console.error("Failed to load chain of custody:", err);
      } finally {
        setLoading(false);
      }
    }
    loadChain();
  }, [activeCase]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <LinkIcon className="w-5 h-5 text-sky-400" />
            <span>CRYPTOGRAPHICALLY-LINKED CHAIN OF CUSTODY</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Tamper-Evident Chronological Ledger with Hash-Chained Signatures (Legal Forensic Admissibility)
          </p>
        </div>

        <div className="px-3 py-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-400 text-xs font-mono flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4" />
          <span>CHAIN INTEGRITY: CONTINUOUS</span>
        </div>
      </div>

      {/* Custody Timeline */}
      <div className="bg-soc-surface rounded-xl border border-soc-border p-6">
        {loading ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs">
            Loading chain of custody ledger...
          </div>
        ) : entries.length === 0 ? (
          <div className="text-center py-12 text-soc-muted font-mono text-xs">
            No chain of custody events recorded yet for this case.
          </div>
        ) : (
          <div className="relative border-l-2 border-sky-500/30 ml-4 space-y-8 pl-6">
            {entries.map((entry, idx) => (
              <div key={entry.id} className="relative group">
                {/* Node Dot */}
                <div className="absolute -left-[31px] top-1 w-4 h-4 rounded-full bg-soc-bg border-2 border-sky-400 flex items-center justify-center">
                  <div className="w-1.5 h-1.5 rounded-full bg-sky-400"></div>
                </div>

                <div className="bg-soc-bg rounded-xl border border-soc-border p-4 hover:border-sky-500/40 transition-all space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2 border-b border-soc-border pb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-mono font-bold text-sky-400">#{idx + 1}</span>
                      <span className="text-xs font-bold text-white font-mono">{entry.action}</span>
                    </div>
                    <div className="text-[11px] font-mono text-soc-muted flex items-center space-x-2">
                      <Clock className="w-3.5 h-3.5 text-sky-400" />
                      <span>{entry.timestamp.replace('T', ' ').substring(0, 19)} UTC</span>
                    </div>
                  </div>

                  <p className="text-xs text-slate-300 leading-relaxed font-sans">
                    {entry.details}
                  </p>

                  <div className="pt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] font-mono text-soc-muted border-t border-soc-border/60">
                    <div className="flex items-center space-x-1.5">
                      <User className="w-3.5 h-3.5 text-slate-400" />
                      <span>Examiner: <span className="text-white font-semibold">{entry.actor_name}</span> ({entry.actor_role})</span>
                    </div>
                    <div className="text-[10px] text-indigo-400 truncate max-w-sm">
                      Chain Seal: <span className="text-slate-400">{entry.integrity_hash}</span>
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
