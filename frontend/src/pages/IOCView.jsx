import React, { useState, useEffect } from 'react';
import { Target, Plus, Trash2, RefreshCw, Search, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { apiRequest } from '../api';

export default function IOCView() {
  const [iocs, setIocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({
    type: 'HASH',
    value: '',
    description: '',
    severity: 'HIGH',
    source: 'NTRO Threat Intel'
  });

  const fetchIocs = async () => {
    setLoading(true);
    try {
      const data = await apiRequest('/iocs');
      setIocs(data);
    } catch (err) {
      console.error("Failed to load IOCs:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIocs();
  }, []);

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await apiRequest('/iocs', {
        method: 'POST',
        body: formData
      });
      setShowAddModal(false);
      setFormData({ type: 'HASH', value: '', description: '', severity: 'HIGH', source: 'NTRO Threat Intel' });
      fetchIocs();
    } catch (err) {
      console.error("Failed to add IOC:", err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await apiRequest(`/iocs/${id}`, { method: 'DELETE' });
      fetchIocs();
    } catch (err) {
      console.error("Failed to delete IOC:", err);
    }
  };

  const filtered = iocs.filter(i =>
    i.value.toLowerCase().includes(search.toLowerCase()) ||
    i.description.toLowerCase().includes(search.toLowerCase()) ||
    i.type.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <Target className="w-5 h-5 text-sky-400" />
            <span>INDICATORS OF COMPROMISE (IOC) MANAGEMENT</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Investigator Threat Intelligence Feeds (File Hashes, C2 IP Addresses, Domains, Filenames)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={fetchIocs}
            className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-sky-500/20"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Test Indicator</span>
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
          placeholder="Filter IOCs by value, type, or threat feed..."
          className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
        />
      </div>

      {/* IOC Table */}
      <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
              <tr>
                <th className="p-3">TYPE</th>
                <th className="p-3">INDICATOR VALUE</th>
                <th className="p-3">DESCRIPTION</th>
                <th className="p-3">SEVERITY</th>
                <th className="p-3">INTEL SOURCE</th>
                <th className="p-3 text-right">ACTION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-soc-border text-slate-300">
              {loading ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    Loading threat IOC database...
                  </td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan={6} className="p-8 text-center text-soc-muted">
                    No threat indicators found. Click "Add Test Indicator" to register new IOCs.
                  </td>
                </tr>
              ) : (
                filtered.map((ioc) => (
                  <tr key={ioc.id} className="hover:bg-soc-card/40 transition-colors">
                    <td className="p-3">
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-sky-400 font-bold text-[10px]">
                        {ioc.type}
                      </span>
                    </td>
                    <td className="p-3 font-bold text-white font-mono truncate max-w-xs">{ioc.value}</td>
                    <td className="p-3 text-soc-muted font-sans text-xs">{ioc.description}</td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        ioc.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' :
                        ioc.severity === 'HIGH' ? 'bg-amber-950 text-amber-400 border border-amber-800' :
                        'bg-slate-800 text-slate-400'
                      }`}>
                        {ioc.severity}
                      </span>
                    </td>
                    <td className="p-3 text-soc-muted">{ioc.source}</td>
                    <td className="p-3 text-right">
                      <button
                        onClick={() => handleDelete(ioc.id)}
                        className="text-soc-muted hover:text-rose-400 p-1 rounded hover:bg-rose-950/30 transition-colors"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Add Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center p-4">
          <div className="bg-soc-surface border border-soc-border rounded-xl p-6 max-w-md w-full space-y-4">
            <h3 className="text-sm font-bold text-white font-mono flex items-center space-x-2">
              <Target className="w-4 h-4 text-sky-400" />
              <span>ADD THREAT INDICATOR (IOC)</span>
            </h3>

            <form onSubmit={handleAdd} className="space-y-3 font-mono text-xs">
              <div>
                <label className="block text-soc-muted mb-1">TYPE</label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                >
                  <option value="HASH">HASH (SHA-256 / MD5)</option>
                  <option value="IP">IP Address</option>
                  <option value="DOMAIN">Domain Name</option>
                  <option value="FILENAME">Filename</option>
                </select>
              </div>

              <div>
                <label className="block text-soc-muted mb-1">VALUE</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. 198.51.100.45 or hash"
                  value={formData.value}
                  onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-soc-muted mb-1">DESCRIPTION</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Suspected C2 Exfiltration Node"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                />
              </div>

              <div>
                <label className="block text-soc-muted mb-1">SEVERITY</label>
                <select
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  className="w-full p-2 bg-soc-bg border border-soc-border rounded text-white focus:outline-none"
                >
                  <option value="CRITICAL">CRITICAL</option>
                  <option value="HIGH">HIGH</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="LOW">LOW</option>
                </select>
              </div>

              <div className="flex justify-end space-x-2 pt-3 border-t border-soc-border">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 rounded bg-soc-bg text-soc-muted hover:text-white border border-soc-border"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded bg-sky-600 hover:bg-sky-500 text-white font-bold"
                >
                  Save Indicator
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
