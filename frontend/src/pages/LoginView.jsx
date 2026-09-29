import React, { useState } from 'react';
import { Shield, KeyRound, User, Lock, AlertCircle, ArrowRight, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function LoginView() {
  const { login } = useAuth();
  const [username, setUsername] = useState('investigator');
  const [password, setPassword] = useState('Forensic@123');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = (u, p) => {
    setUsername(u);
    setPassword(p);
  };

  return (
    <div className="min-h-screen bg-soc-bg flex items-center justify-center p-4 relative overflow-hidden select-none">
      {/* Decorative Background Grid & Accents */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a15_1px,transparent_1px),linear-gradient(to_bottom,#0f172a15_1px,transparent_1px)] bg-[size:4rem_4rem]"></div>
      <div className="absolute -top-40 -left-40 w-96 h-96 bg-sky-500/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10">
        {/* Card */}
        <div className="bg-soc-surface/95 border border-soc-border rounded-2xl shadow-2xl p-8 backdrop-blur-xl">
          {/* Logo & Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-sky-600 to-indigo-600 mx-auto flex items-center justify-center shadow-xl shadow-sky-500/20 mb-4 border border-sky-400/30">
              <Shield className="w-9 h-9 text-white" />
            </div>
            <h1 className="text-xl font-bold tracking-wider text-white">CYBER INVESTIGATORS</h1>
            <p className="text-xs text-sky-400 font-mono mt-1">NTRO FORENSIC PLATFORM • SIH26148</p>
            <p className="text-xs text-soc-muted mt-2">
              Cryptographically Governed Digital Evidence & Network Investigation System
            </p>
          </div>

          {error && (
            <div className="mb-6 p-3 rounded-lg bg-rose-950/50 border border-rose-800 text-rose-300 text-xs flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-mono text-soc-muted mb-1">INVESTIGATOR IDENTIFIER</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-soc-muted">
                  <User className="w-4 h-4" />
                </div>
                <input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  placeholder="e.g. investigator"
                  className="w-full pl-10 pr-3 py-2.5 bg-soc-bg border border-soc-border rounded-lg text-sm text-white focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 font-mono"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-soc-muted mb-1">SECURITY TOKEN / PASSWORD</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-soc-muted">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••••••"
                  className="w-full pl-10 pr-3 py-2.5 bg-soc-bg border border-soc-border rounded-lg text-sm text-white focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 font-mono"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full mt-2 py-2.5 px-4 bg-gradient-to-r from-sky-600 to-indigo-600 hover:from-sky-500 hover:to-indigo-500 text-white font-medium rounded-lg text-sm transition-all shadow-lg shadow-sky-500/20 flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{loading ? 'Authenticating Investigator...' : 'Authenticate & Open Console'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick Login Presets for SIH Evaluation */}
          <div className="mt-8 pt-6 border-t border-soc-border">
            <p className="text-[11px] font-mono text-soc-muted text-center mb-3">
              SIH JURY QUICK ACCESS CREDENTIALS:
            </p>
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => handleQuickLogin('investigator', 'Forensic@123')}
                className="p-2 text-left bg-soc-bg hover:bg-slate-800 border border-soc-border rounded-lg transition-colors group"
              >
                <div className="text-[10px] font-bold text-sky-400 font-mono">INVESTIGATOR</div>
                <div className="text-[9px] text-soc-muted">Lead DFIR</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('admin', 'Admin@NTRO2026')}
                className="p-2 text-left bg-soc-bg hover:bg-slate-800 border border-soc-border rounded-lg transition-colors group"
              >
                <div className="text-[10px] font-bold text-emerald-400 font-mono">ADMIN</div>
                <div className="text-[9px] text-soc-muted">Forensic Lead</div>
              </button>
              <button
                type="button"
                onClick={() => handleQuickLogin('viewer', 'Viewer@123')}
                className="p-2 text-left bg-soc-bg hover:bg-slate-800 border border-soc-border rounded-lg transition-colors group"
              >
                <div className="text-[10px] font-bold text-amber-400 font-mono">AUDITOR</div>
                <div className="text-[9px] text-soc-muted">Viewer RBAC</div>
              </button>
            </div>
          </div>
        </div>

        {/* Security Declaration */}
        <div className="mt-4 text-center text-[11px] text-soc-muted flex items-center justify-center space-x-2 font-mono">
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
          <span>FIPS 180-4 SHA-256 Chain of Custody Protected</span>
        </div>
      </div>
    </div>
  );
}
