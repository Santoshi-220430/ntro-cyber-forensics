import React, { useState, useEffect } from 'react';
import { Files as FilesIcon, Search, AlertTriangle, RefreshCw, FileCode, CheckCircle2 } from 'lucide-react';
import { apiRequest } from '../api';

export default function FilesView({ activeCase }) {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');

  const fetchFiles = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/files`);
      setFiles(data);
    } catch (err) {
      console.error("Failed to load files:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, [activeCase]);

  const filtered = files.filter(f =>
    f.filename.toLowerCase().includes(search.toLowerCase()) ||
    f.path.toLowerCase().includes(search.toLowerCase()) ||
    (f.sha256 && f.sha256.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <FilesIcon className="w-5 h-5 text-sky-400" />
            <span>FILE SYSTEM METADATA & HASH CATALOG</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Read-Only Acquisition of File Timestamps (MACB), Executable Staging Heuristics & SHA-256 Digests
          </p>
        </div>

        <button
          onClick={fetchFiles}
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
          placeholder="Filter by filename, full path, or SHA-256 hash..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* Files Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">FILENAME</th>
                <th className="p-3">FULL PATH</th>
                <th className="p-3">SIZE</th>
                <th className="p-3">CREATED / MODIFIED</th>
                <th className="p-3">SHA-256 HASH</th>
                <th className="p-3">CLASSIFICATION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Loading file system evidence...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No files cataloged yet. Execute <code>GET FILES</code> in the Forensic Console.
                  </td>
                </tr>
              ) : (
                filtered.map((file) => (
                  <tr key={file.id} className={`hover:bg-soc-card/40 transition-colors ${
                    file.is_suspicious ? "bg-rose-950/20" : ""
                  }`}>
                    <td className="p-3 font-bold text-white flex items-center space-x-2">
                      <FileCode className="w-4 h-4 text-sky-400" />
                      <span>{file.filename}</span>
                    </td>
                    <td className="p-3 text-soc-muted truncate max-w-xs">{file.path}</td>
                    <td className="p-3 text-sky-300 font-mono">
                      {file.size_bytes ? `${(file.size_bytes / 1024).toFixed(1)} KB` : "0 B"}
                    </td>
                    <td className="p-3 text-soc-muted">
                      <div>C: {file.created_time ? file.created_time.substring(0, 19).replace('T', ' ') : 'N/A'}</div>
                      <div className="text-[10px]">M: {file.modified_time ? file.modified_time.substring(0, 19).replace('T', ' ') : 'N/A'}</div>
                    </td>
                    <td className="p-3 font-mono text-[11px] text-indigo-300 truncate max-w-xs">
                      {file.sha256 || 'N/A'}
                    </td>
                    <td className="p-3">
                      {file.is_suspicious === 1 ? (
                        <div className="space-y-0.5">
                          <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-400 border border-rose-800 text-[10px] font-bold">
                            SUSPICIOUS
                          </span>
                          <div className="text-[10px] text-rose-300 font-sans">{file.suspicious_reason}</div>
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
