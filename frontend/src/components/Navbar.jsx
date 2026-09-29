import React from 'react';
import { Shield, Terminal, LogOut, User, Server, AlertCircle, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function Navbar({ activeCase, cases, onSelectCase, activeTab }) {
  const { user, logout } = useAuth();

  return (
    <header className="h-16 bg-soc-surface border-b border-soc-border px-6 flex items-center justify-between select-none z-20">
      {/* Brand & Emblem */}
      <div className="flex items-center space-x-3">
        <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-soc-primary to-blue-700 flex items-center justify-center shadow-lg shadow-sky-500/20">
          <Shield className="w-6 h-6 text-white" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold text-white tracking-wider">CYBER INVESTIGATORS</h1>
            <span className="text-[10px] px-2 py-0.5 rounded bg-sky-950/80 text-sky-400 border border-sky-800/60 font-mono font-semibold">
              SIH26148
            </span>
          </div>
          <p className="text-xs text-soc-muted">NTRO Forensics & Domain-Specific Scripting Platform</p>
        </div>
      </div>

      {/* Center: Case Selector & Target */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2 bg-soc-bg border border-soc-border px-3 py-1.5 rounded-lg">
          <Server className="w-4 h-4 text-sky-400" />
          <span className="text-xs text-soc-muted">Case:</span>
          <select
            value={activeCase?.id || ''}
            onChange={(e) => {
              const selected = cases.find(c => c.id === e.target.value);
              if (selected) onSelectCase(selected);
            }}
            className="bg-transparent text-xs font-mono font-bold text-white focus:outline-none cursor-pointer"
          >
            {cases.map(c => (
              <option key={c.id} value={c.id} className="bg-soc-surface text-white">
                {c.case_number} — {c.target_host}
              </option>
            ))}
          </select>
        </div>

        {/* Security Compatibility Badge */}
        <div className="hidden lg:flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-emerald-950/40 border border-emerald-800/60 text-emerald-400 text-xs font-mono">
          <CheckCircle2 className="w-4 h-4 text-emerald-400 animate-pulse" />
          <span>POLICY: FORENSIC_READ_ONLY (AUTHORIZED)</span>
        </div>
      </div>

      {/* Right: Investigator Info & Logout */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3 text-right">
          <div>
            <div className="text-xs font-bold text-white flex items-center justify-end space-x-1">
              <span>{user?.full_name}</span>
            </div>
            <div className="text-[11px] text-soc-muted font-mono">
              Badge: <span className="text-sky-400">{user?.badge_number || 'NTRO-INV'}</span> • <span className="text-amber-400">{user?.role}</span>
            </div>
          </div>
          <div className="w-9 h-9 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-sky-400">
            <User className="w-5 h-5" />
          </div>
        </div>

        <button
          onClick={logout}
          title="Sign Out"
          className="p-2 text-soc-muted hover:text-rose-400 hover:bg-rose-950/30 rounded-lg transition-colors border border-transparent hover:border-rose-900/50"
        >
          <LogOut className="w-4 h-4" />
        </button>
      </div>
    </header>
  );
}
