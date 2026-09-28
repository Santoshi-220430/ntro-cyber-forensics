import React, { useState, useEffect } from 'react';
import { Cpu, Server, HardDrive, Clock, User, ShieldCheck, RefreshCw } from 'lucide-react';
import { apiRequest } from '../api';

export default function SystemView({ activeCase }) {
  const [sysInfo, setSysInfo] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchSystem = async () => {
    if (!activeCase) return;
    setLoading(true);
    try {
      const data = await apiRequest(`/cases/${activeCase.id}/system`);
      setSysInfo(data);
    } catch (err) {
      console.error("Failed to load system info:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystem();
  }, [activeCase]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-soc-surface p-5 rounded-xl border border-soc-border flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-bold text-white font-mono flex items-center space-x-2">
            <Cpu className="w-5 h-5 text-sky-400" />
            <span>SYSTEM ARCHITECTURE & HARDWARE TELEMETRY</span>
          </h2>
          <p className="text-xs text-soc-muted mt-1">
            Host Diagnostics, Operating System Kernel Profile & Memory Allocation
          </p>
        </div>

        <button
          onClick={fetchSystem}
          className="p-2 rounded-lg bg-soc-bg border border-soc-border text-soc-muted hover:text-white transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {!sysInfo || Object.keys(sysInfo).length === 0 ? (
        <div className="bg-soc-surface p-12 rounded-xl border border-soc-border text-center text-soc-muted font-mono text-xs">
          No system hardware data collected yet for this case. Execute <code>GET SYSTEM</code> in the Forensic Console.
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Card 1: Operating System */}
          <div className="bg-soc-surface p-6 rounded-xl border border-soc-border space-y-4">
            <div className="flex items-center space-x-3 text-sky-400">
              <Server className="w-5 h-5" />
              <h3 className="text-sm font-bold text-white font-mono">OPERATING SYSTEM</h3>
            </div>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">OS Name:</span>
                <span className="text-white font-bold">{sysInfo.os_name}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Kernel Build:</span>
                <span className="text-slate-300">{sysInfo.os_version}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Architecture:</span>
                <span className="text-emerald-400 font-bold">{sysInfo.architecture}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-soc-muted">Hostname:</span>
                <span className="text-sky-400 font-bold">{sysInfo.hostname}</span>
              </div>
            </div>
          </div>

          {/* Card 2: CPU & Resources */}
          <div className="bg-soc-surface p-6 rounded-xl border border-soc-border space-y-4">
            <div className="flex items-center space-x-3 text-emerald-400">
              <Cpu className="w-5 h-5" />
              <h3 className="text-sm font-bold text-white font-mono">PROCESSOR & MEMORY</h3>
            </div>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Logical Cores:</span>
                <span className="text-white font-bold">{sysInfo.cpu_count} Threads</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Clock Speed:</span>
                <span className="text-slate-300">{sysInfo.cpu_freq_mhz} MHz</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Total Physical RAM:</span>
                <span className="text-sky-400 font-bold">{sysInfo.total_ram_gb} GB</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-soc-muted">Available RAM:</span>
                <span className="text-emerald-400 font-bold">{sysInfo.available_ram_gb} GB</span>
              </div>
            </div>
          </div>

          {/* Card 3: Session & Uptime */}
          <div className="bg-soc-surface p-6 rounded-xl border border-soc-border space-y-4">
            <div className="flex items-center space-x-3 text-indigo-400">
              <Clock className="w-5 h-5" />
              <h3 className="text-sm font-bold text-white font-mono">SESSION & TIMING</h3>
            </div>
            <div className="space-y-2 text-xs font-mono">
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Logged User:</span>
                <span className="text-white font-bold">{sysInfo.username}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Uptime (Seconds):</span>
                <span className="text-slate-300">{sysInfo.uptime_seconds}s</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-soc-border">
                <span className="text-soc-muted">Boot Timestamp:</span>
                <span className="text-slate-300">{sysInfo.boot_time ? sysInfo.boot_time.substring(0, 19).replace('T', ' ') : 'N/A'}</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-soc-muted">Telemetry Harvest:</span>
                <span className="text-sky-400">{sysInfo.collected_at ? sysInfo.collected_at.substring(0, 19).replace('T', ' ') : 'N/A'}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
