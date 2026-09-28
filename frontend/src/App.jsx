import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { apiRequest } from './api';

import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';

import LoginView from './pages/LoginView';
import DashboardView from './pages/DashboardView';
import ConsoleView from './pages/ConsoleView';
import CasesView from './pages/CasesView';
import SystemView from './pages/SystemView';
import ProcessesView from './pages/ProcessesView';
import FilesView from './pages/FilesView';
import NetworkView from './pages/NetworkView';
import LogsView from './pages/LogsView';
import PCAPView from './pages/PCAPView';
import TimelineView from './pages/TimelineView';
import EvidenceView from './pages/EvidenceView';
import ChainOfCustodyView from './pages/ChainOfCustodyView';
import FindingsView from './pages/FindingsView';
import IOCView from './pages/IOCView';
import SecurityCompatibilityView from './pages/SecurityCompatibilityView';
import ReportsView from './pages/ReportsView';
import AuditView from './pages/AuditView';

function AppContent() {
  const { isAuthenticated, loading } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [cases, setCases] = useState([]);
  const [activeCase, setActiveCase] = useState(null);

  const fetchCases = async () => {
    try {
      const data = await apiRequest('/cases');
      setCases(data);
      if (data.length > 0 && !activeCase) {
        setActiveCase(data[0]);
      } else if (data.length > 0 && activeCase) {
        const found = data.find(c => c.id === activeCase.id);
        if (found) setActiveCase(found);
      }
    } catch (err) {
      console.error("Failed to fetch cases:", err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchCases();
    }
  }, [isAuthenticated]);

  if (loading) {
    return (
      <div className="min-h-screen bg-soc-bg flex items-center justify-center font-mono text-xs text-sky-400">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-8 h-8 border-2 border-sky-400 border-t-transparent rounded-full animate-spin"></div>
          <span>INITIALIZING NTRO FORENSIC ENVIRONMENT...</span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <LoginView />;
  }

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardView activeCase={activeCase} setActiveTab={setActiveTab} />;
      case 'console':
        return <ConsoleView activeCase={activeCase} onRefreshData={fetchCases} />;
      case 'cases':
        return (
          <CasesView
            cases={cases}
            activeCase={activeCase}
            onSelectCase={(c) => setActiveCase(c)}
            onRefreshCases={fetchCases}
          />
        );
      case 'system':
        return <SystemView activeCase={activeCase} />;
      case 'processes':
        return <ProcessesView activeCase={activeCase} />;
      case 'files':
        return <FilesView activeCase={activeCase} />;
      case 'network':
        return <NetworkView activeCase={activeCase} />;
      case 'logs':
        return <LogsView activeCase={activeCase} />;
      case 'pcap':
        return <PCAPView />;
      case 'timeline':
        return <TimelineView activeCase={activeCase} />;
      case 'evidence':
        return <EvidenceView activeCase={activeCase} />;
      case 'chain_of_custody':
        return <ChainOfCustodyView activeCase={activeCase} />;
      case 'findings':
        return <FindingsView activeCase={activeCase} />;
      case 'iocs':
        return <IOCView />;
      case 'security':
        return <SecurityCompatibilityView activeCase={activeCase} />;
      case 'reports':
        return <ReportsView activeCase={activeCase} />;
      case 'audit':
        return <AuditView />;
      default:
        return <DashboardView activeCase={activeCase} setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-soc-bg text-soc-text flex flex-col font-sans">
      <Navbar
        activeCase={activeCase}
        cases={cases}
        onSelectCase={(c) => setActiveCase(c)}
        activeTab={activeTab}
      />
      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <main className="flex-1 overflow-y-auto p-6 bg-soc-bg">
          <div className="max-w-7xl mx-auto">
            {renderActiveTab()}
          </div>
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}
