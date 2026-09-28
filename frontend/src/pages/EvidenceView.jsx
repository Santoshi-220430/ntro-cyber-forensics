import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  FolderLock,
  Search,
  Upload,
  FileCheck2,
  Lock
} from 'lucide-react';
import { apiRequest } from '../api';

export default function EvidenceView({ activeCase }) {
  const [evidenceList, setEvidenceList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [verifying, setVerifying] = useState(false);
  const [search, setSearch] = useState('');
  const [verifyMessage, setVerifyMessage] = useState(null);

  const fetchEvidence = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/evidence`);
      setEvidenceList(data);
    } catch (err) {
      console.error("Failed to fetch evidence:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvidence();
  }, [activeCase]);

  const handleVerifyAll = async () => {
    setVerifying(true);
    setVerifyMessage(null);
    try {
      const results = await apiRequest(`/cases/${activeCase.id}/evidence/verify`, {
        method: 'POST'
      });
      const failed = results.filter(r => r.status !== 'VERIFIED');
      if (failed.length === 0) {
        setVerifyMessage({
          type: 'success',
          text: `All ${results.length} evidence items verified! Hashes match with 0 tampering detected.`
        });
      } else {
        setVerifyMessage({
          type: 'error',
          text: `Integrity check failed for ${failed.length} evidence item(s)!`
        });
      }
      fetchEvidence();
    } catch (err) {
      setVerifyMessage({ type: 'error', text: `Verification failed: ${err.message}` });
    } finally {
      setVerifying(false);
    }
  };

  const handleDeduplicate = async () => {
    if (!activeCase) return;
    try {
      await apiRequest(`/cases/${activeCase.id}/deduplicate`, { method: 'POST' });
      fetchEvidence();
      setVerifyMessage({ type: 'success', text: 'Evidence repository verified & deduplicated. Zero duplicate records.' });
    } catch (err) {
      console.error("Deduplication failed:", err);
    }
  };

  const filtered = evidenceList.filter(e =>
    e.name.toLowerCase().includes(search.toLowerCase()) ||
    e.evidence_number.toLowerCase().includes(search.toLowerCase()) ||
    e.sha256_hash.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex flex-wrap items-center justify-between gap-4 bg-soc-surface p-5 rounded-xl border border-soc-border">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <FolderLock className="w-5 h-5 text-sky-400" />
            <span>CRYPTOGRAPHIC EVIDENCE VAULT & INTEGRITY VERIFIER</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            FIPS 180-4 SHA-256 Sealed Evidence Repository with Real-Time Hash Integrity Verification (Idempotent & Deduplicated)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleDeduplicate}
            title="Deduplicate Evidence Vault"
            className="px-3 py-2 rounded-lg bg-sky-950/60 border border-sky-800 text-sky-300 hover:text-white hover:bg-sky-900/60 text-xs font-mono flex items-center space-x-1.5 transition-all"
          >
            <FileCheck2 className="w-4 h-4 text-sky-400" />
            <span>Deduplicate Vault</span>
          </button>
          <button
            onClick={fetchEvidence}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleVerifyAll}
            disabled={verifying || evidenceList.length === 0}
            className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-emerald-500/20 disabled:opacity-50"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{verifying ? "Computing Hashes..." : "Verify All Evidence Integrity"}</span>
          </button>
        </div>
      </div>

      {verifyMessage && (
        <div className={`p-4 rounded-xl border flex items-center space-x-3 text-xs font-mono ${
          verifyMessage.type === 'success'
            ? 'bg-emerald-950/60 border-emerald-800 text-emerald-300'
            : 'bg-rose-950/60 border-rose-800 text-rose-300'
        }`}>
          {verifyMessage.type === 'success' ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-rose-400 flex-shrink-0" />
          )}
          <span>{verifyMessage.text}</span>
        </div>
      )}

      {/* Filter & Search Bar */}
      <div className="flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-3 text-soc-muted" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by evidence ID, artifact name, or SHA-256 hash..."
            className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
          />
        </div>
        <div className="text-xs font-mono text-soc-muted">
          Showing <span className="text-white font-bold">{filtered.length}</span> of {evidenceList.length} artifacts
        </div>
      </div>

      {/* Evidence Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">EVIDENCE ID</th>
                <th className="p-3">ARTIFACT NAME</th>
                <th className="p-3">SOURCE TYPE</th>
                <th className="p-3">FIPS SHA-256 CRYPTOGRAPHIC DIGEST</th>
                <th className="p-3">SIZE</th>
                <th className="p-3">ACQUIRED TIMESTAMP</th>
                <th className="p-3">INTEGRITY</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-soc-muted">
                    Loading evidence vault catalog...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-soc-muted">
                    No evidence items registered yet for this case. Execute <code>GET FILES</code> or <code>GET SYSTEM</code> in the Forensic Console.
                  </td>
                </tr>
              ) : (
                filtered.map((ev) => (
                  <tr key={ev.id} className="hover:bg-soc-card/40 transition-colors">
                    <td className="p-3 font-bold text-sky-400">{ev.evidence_number}</td>
                    <td className="p-3 font-semibold text-white">{ev.name}</td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold">
                        {ev.source_type}
                      </span>
                    </td>
                    <td className="p-3 text-[11px] text-indigo-300 font-mono">
                      {ev.sha256_hash}
                    </td>
                    <td className="p-3 text-soc-muted">
                      {ev.file_size ? `${(ev.file_size / 1024).toFixed(1)} KB` : "N/A"}
                    </td>
                    <td className="p-3 text-soc-muted">
                      {ev.acquisition_timestamp ? ev.acquisition_timestamp.replace('T', ' ').substring(0, 19) : "N/A"}
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold flex items-center space-x-1 w-max ${
                        ev.integrity_status === 'VERIFIED'
                          ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                          : 'bg-rose-950 text-rose-400 border border-rose-800'
                      }`}>
                        {ev.integrity_status === 'VERIFIED' ? (
                          <CheckCircle2 className="w-3 h-3" />
                        ) : (
                          <AlertTriangle className="w-3 h-3" />
                        )}
                        <span>{ev.integrity_status}</span>
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
