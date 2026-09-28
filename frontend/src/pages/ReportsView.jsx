import React, { useState, useEffect } from 'react';
import { FileSearch, Download, Play, RefreshCw, CheckCircle2, ShieldCheck, FileText } from 'lucide-react';
import { apiRequest } from '../api';

export default function ReportsView({ activeCase }) {
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [recentGen, setRecentGen] = useState(null);

  const fetchReports = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/reports`);
      setReports(data);
    } catch (err) {
      console.error("Failed to load reports:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReports();
  }, [activeCase]);

  const handleGenerateReport = async () => {
    setGenerating(true);
    setRecentGen(null);
    try {
      const res = await apiRequest(`/cases/${activeCase.id}/report`, { method: 'POST' });
      setRecentGen(res);
      fetchReports();
    } catch (err) {
      console.error("Report generation failed:", err);
    } finally {
      setGenerating(false);
    }
  };

  const handleDownload = async (reportId, filename) => {
    try {
      const blob = await apiRequest(`/reports/${reportId}/download`);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename || 'Forensic_Report.pdf';
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Download failed:", err);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <FileSearch className="w-5 h-5 text-sky-400" />
            <span>FORENSIC PDF REPORT REPOSITORY</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Official Examination Reports with Cryptographically Sealed Hashes (FIPS 180-4 SHA-256)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchReports}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={handleGenerateReport}
            disabled={generating}
            className="px-4 py-2 rounded-lg bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-sky-500/20 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{generating ? "Compiling PDF Document..." : "Generate Official Forensic Report"}</span>
          </button>
        </div>
      </div>

      {recentGen && (
        <div className="p-4 rounded-xl bg-emerald-950/60 border border-emerald-800 text-emerald-300 text-xs font-mono flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            <span>Report generated: <strong>{recentGen.filename}</strong> (SHA-256: {recentGen.sha256_hash?.substring(0, 24)}...)</span>
          </div>
          <button
            onClick={() => handleDownload(recentGen.id, recentGen.filename)}
            className="px-3 py-1 bg-emerald-600 hover:bg-emerald-500 text-white rounded font-bold transition-colors flex items-center space-x-1"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Download Now</span>
          </button>
        </div>
      )}

      {/* Reports Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">REPORT NUMBER</th>
                <th className="p-3">REPORT TITLE</th>
                <th className="p-3">FORMAT</th>
                <th className="p-3">FILE SIZE</th>
                <th className="p-3">SHA-256 CRYPTOGRAPHIC SEAL</th>
                <th className="p-3">GENERATED AT</th>
                <th className="p-3 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-soc-muted">
                    Loading report archive...
                  </td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="p-8 text-center text-soc-muted">
                    No reports compiled yet for this case. Click "Generate Official Forensic Report" above or execute <code>GENERATE REPORT</code> in the console.
                  </td>
                </tr>
              ) : (
                reports.map((rep) => (
                  <tr key={rep.id} className="hover:bg-soc-card/40 transition-colors">
                    <td className="p-3 font-bold text-sky-400">{rep.report_number}</td>
                    <td className="p-3 font-semibold text-white flex items-center space-x-2">
                      <FileText className="w-4 h-4 text-sky-400" />
                      <span>{rep.title}</span>
                    </td>
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800 text-[10px] font-bold">
                        {rep.format}
                      </span>
                    </td>
                    <td className="p-3 text-soc-muted font-mono">
                      {rep.file_size ? `${(rep.file_size / 1024).toFixed(1)} KB` : "N/A"}
                    </td>
                    <td className="p-3 text-indigo-300 font-mono text-[11px] truncate max-w-xs">
                      {rep.sha256_hash}
                    </td>
                    <td className="p-3 text-soc-muted">
                      {rep.generated_at.replace('T', ' ').substring(0, 19)}
                    </td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleDownload(rep.id, `${rep.report_number}.pdf`)}
                        className="px-3 py-1 rounded bg-soc-bg hover:bg-sky-600 hover:text-white border border-soc-border text-sky-400 font-bold transition-all inline-flex items-center space-x-1.5"
                      >
                        <Download className="w-3.5 h-3.5" />
                        <span>Download PDF</span>
                      </button>
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
