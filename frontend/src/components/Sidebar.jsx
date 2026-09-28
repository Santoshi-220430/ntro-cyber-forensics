import React from 'react';
import {
  LayoutDashboard,
  Terminal,
  FolderLock,
  Cpu,
  Activity,
  Files,
  Network,
  FileCode,
  Clock,
  ShieldCheck,
  Link,
  Target,
  AlertTriangle,
  FileText,
  FileSearch,
  Radio,
  Sliders,
  History
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab }) {
  const sections = [
    {
      label: "COMMAND & CONTROL",
      items: [
        { id: "dashboard", label: "Overview Dashboard", icon: LayoutDashboard },
        { id: "console", label: "Forensic Console (DSL)", icon: Terminal, highlight: true },
        { id: "cases", label: "Case Management", icon: FolderLock },
      ]
    },
    {
      label: "EVIDENCE ACQUISITION",
      items: [
        { id: "system", label: "System Diagnostics", icon: Cpu },
        { id: "processes", label: "Running Processes", icon: Activity },
        { id: "files", label: "File System & Hashes", icon: Files },
        { id: "network", label: "Network Sockets", icon: Network },
        { id: "logs", label: "Normalized Logs", icon: FileText },
        { id: "pcap", label: "Offline PCAP Parser", icon: Radio },
      ]
    },
    {
      label: "CORRELATION & INTEGRITY",
      items: [
        { id: "timeline", label: "Multi-Source Timeline", icon: Clock },
        { id: "evidence", label: "Evidence & Integrity", icon: ShieldCheck },
        { id: "chain_of_custody", label: "Chain of Custody", icon: Link },
        { id: "findings", label: "Detection Findings", icon: AlertTriangle },
        { id: "iocs", label: "Threat IOC Feeds", icon: Target },
      ]
    },
    {
      label: "SECURITY & COMPLIANCE",
      items: [
        { id: "security", label: "Security Compatibility", icon: Sliders, badge: "CORE SIH" },
        { id: "reports", label: "Forensic PDF Reports", icon: FileSearch },
        { id: "audit", label: "Immutable Audit Log", icon: History },
      ]
    }
  ];

  return (
    <aside className="w-64 bg-soc-surface/90 border-r border-soc-border flex flex-col h-[calc(100vh-4rem)] select-none">
      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-6">
        {sections.map((sec, idx) => (
          <div key={idx}>
            <div className="text-[10px] font-mono tracking-wider font-bold text-soc-muted/80 px-3 mb-2">
              {sec.label}
            </div>
            <nav className="space-y-1">
              {sec.items.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                      isActive
                        ? 'bg-sky-500/15 text-sky-400 border border-sky-500/40 shadow-sm font-semibold'
                        : 'text-soc-muted hover:text-white hover:bg-soc-card/70 border border-transparent'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-sky-400' : 'text-soc-muted'}`} />
                      <span>{item.label}</span>
                    </div>
                    {item.badge && (
                      <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-400 font-mono font-bold border border-amber-500/30">
                        {item.badge}
                      </span>
                    )}
                    {item.highlight && !item.badge && (
                      <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse"></span>
                    )}
                  </button>
                );
              })}
            </nav>
          </div>
        ))}
      </div>

      {/* Footer System Status */}
      <div className="p-3 border-t border-soc-border bg-soc-bg/50">
        <div className="flex items-center justify-between text-[11px] font-mono text-soc-muted">
          <span>FRAMEWORK STATUS</span>
          <span className="text-emerald-400 flex items-center space-x-1">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping mr-1"></span>
            ACTIVE
          </span>
        </div>
      </div>
    </aside>
  );
}
