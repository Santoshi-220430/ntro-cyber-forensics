import React, { useState } from 'react';
import { Radio, Upload, Play, Globe, CheckCircle2, FileCode, Search } from 'lucide-react';
import { apiRequest } from '../api';

export default function PCAPView() {
  const [pcapData, setPcapData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  const handleAnalyzeSample = async () => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('use_sample', 'true');
      const res = await apiRequest('/pcap/analyze', {
        method: 'POST',
        body: formData
      });
      setPcapData(res);
    } catch (err) {
      console.error("PCAP analysis failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('use_sample', 'false');
      const res = await apiRequest('/pcap/analyze', {
        method: 'POST',
        body: formData
      });
      setPcapData(res);
    } catch (err) {
      console.error("Upload PCAP failed:", err);
    } finally {
      setLoading(false);
    }
  };

  const packets = pcapData?.packets || [];
  const filtered = packets.filter(p =>
    p.source_ip.includes(search) ||
    p.destination_ip.includes(search) ||
    p.info.toLowerCase().includes(search.toLowerCase()) ||
    p.protocol.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <Radio className="w-5 h-5 text-sky-400" />
            <span>OFFLINE PCAP PACKET ANALYSIS & NETWORK RECONSTRUCTION</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Read-Only Offline Analysis of Investigator-Supplied Packet Captures (No Live Interception / Promiscuous Sniffing)
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <label className="px-4 py-2 rounded-lg bg-soc-bg hover:bg-slate-800 text-soc-text border border-soc-border text-xs font-mono cursor-pointer flex items-center space-x-2 transition-colors">
            <Upload className="w-3.5 h-3.5 text-sky-400" />
            <span>Upload PCAP File</span>
            <input type="file" accept=".pcap,.pcapng" onChange={handleFileUpload} className="hidden" />
          </label>

          <button
            onClick={handleAnalyzeSample}
            disabled={loading}
            className="px-4 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-mono font-bold flex items-center space-x-2 transition-all shadow-md shadow-sky-500/20 disabled:opacity-50"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>{loading ? "Parsing Frames..." : "Analyze Synthetic Traffic PCAP"}</span>
          </button>
        </div>
      </div>

      {pcapData && (
        <>
          {/* Protocol Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="bg-soc-surface p-3.5 rounded-xl border border-soc-border text-center font-mono">
              <div className="text-[10px] text-soc-muted">TOTAL FRAMES</div>
              <div className="text-lg font-bold text-white">{pcapData.total_packets}</div>
            </div>
            <div className="bg-soc-surface p-3.5 rounded-xl border border-soc-border text-center font-mono">
              <div className="text-[10px] text-soc-muted">TCP STREAMS</div>
              <div className="text-lg font-bold text-sky-400">{pcapData.protocol_breakdown?.TCP || 0}</div>
            </div>
            <div className="bg-soc-surface p-3.5 rounded-xl border border-soc-border text-center font-mono">
              <div className="text-[10px] text-soc-muted">UDP DATAGRAMS</div>
              <div className="text-lg font-bold text-indigo-400">{pcapData.protocol_breakdown?.UDP || 0}</div>
            </div>
            <div className="bg-soc-surface p-3.5 rounded-xl border border-soc-border text-center font-mono">
              <div className="text-[10px] text-soc-muted">DNS QUERIES</div>
              <div className="text-lg font-bold text-emerald-400">{pcapData.protocol_breakdown?.DNS || 0}</div>
            </div>
            <div className="bg-soc-surface p-3.5 rounded-xl border border-soc-border text-center font-mono">
              <div className="text-[10px] text-soc-muted">HTTP PAYLOADS</div>
              <div className="text-lg font-bold text-amber-400">{pcapData.protocol_breakdown?.HTTP || 0}</div>
            </div>
          </div>

          {/* Search */}
          <div className="relative max-w-md">
            <Search className="w-4 h-4 absolute left-3 top-3 text-soc-muted" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search packet frames by IP or protocol info..."
              className="w-full pl-9 pr-3 py-2 bg-soc-surface border border-soc-border rounded-lg text-xs text-white font-mono focus:outline-none focus:border-sky-500"
            />
          </div>

          {/* Packets Table */}
          <div className="bg-soc-surface rounded-xl border border-soc-border overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs font-mono">
                <thead className="bg-soc-card/70 text-soc-muted border-b border-soc-border">
                  <tr>
                    <th className="p-3">FRAME #</th>
                    <th className="p-3">TIMESTAMP</th>
                    <th className="p-3">PROTOCOL</th>
                    <th className="p-3">SOURCE IP:PORT</th>
                    <th className="p-3">DESTINATION IP:PORT</th>
                    <th className="p-3">LENGTH</th>
                    <th className="p-3">FRAME INFO</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-soc-border text-slate-300">
                  {filtered.map((pkt) => (
                    <tr key={pkt.packet_number} className="hover:bg-soc-card/40 transition-colors">
                      <td className="p-3 text-sky-400 font-bold">{pkt.packet_number}</td>
                      <td className="p-3 text-soc-muted">{pkt.timestamp.substring(11, 19)}</td>
                      <td className="p-3">
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold text-[10px]">
                          {pkt.protocol}
                        </span>
                      </td>
                      <td className="p-3 font-semibold text-white">
                        {pkt.source_ip}:{pkt.source_port}
                      </td>
                      <td className="p-3 font-semibold text-emerald-400">
                        {pkt.destination_ip}:{pkt.destination_port}
                      </td>
                      <td className="p-3 text-soc-muted">{pkt.length_bytes} B</td>
                      <td className="p-3 text-slate-300 truncate max-w-xs">{pkt.info}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {!pcapData && (
        <div className="bg-soc-surface p-12 rounded-xl border border-soc-border text-center text-soc-muted font-mono text-xs space-y-3">
          <p>No offline packet capture loaded.</p>
          <p className="text-[11px] text-slate-500">
            Click "Analyze Synthetic Traffic PCAP" above to load the pre-staged sample network capture.
          </p>
        </div>
      )}
    </div>
  );
}
