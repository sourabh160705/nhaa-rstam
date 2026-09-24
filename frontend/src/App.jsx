import React, { useState, useEffect } from 'react';
import { Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, FileAudio, Users, Settings, LogOut, ShieldAlert } from 'lucide-react';
import OperatorDashboard from './pages/OperatorDashboard';
import AssessmentPage from './pages/AssessmentPage';
import CaseDetailPage from './pages/CaseDetailPage';

function App() {
  const [time, setTime] = useState(new Date().toLocaleTimeString());
  const location = useLocation();

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex h-screen bg-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-nhaa-navy text-white flex flex-col">
        <div className="p-4 flex items-center gap-3 border-b border-slate-700">
          <ShieldAlert className="text-nhaa-blue h-8 w-8" />
          <div>
            <h1 className="font-bold text-lg tracking-wider">NHAA 14566</h1>
            <p className="text-xs text-slate-400">RSTAM Dashboard</p>
          </div>
        </div>
        
        <nav className="flex-1 p-4 space-y-2">
          <NavLink 
            to="/" 
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-nhaa-blue text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            <LayoutDashboard size={20} />
            Dashboard
          </NavLink>
          <NavLink 
            to="/assess" 
            className={({isActive}) => `flex items-center gap-3 p-3 rounded-lg transition-colors ${isActive ? 'bg-nhaa-blue text-white' : 'text-slate-300 hover:bg-slate-800'}`}
          >
            <FileAudio size={20} />
            New Assessment
          </NavLink>
        </nav>

        <div className="p-4 border-t border-slate-700">
          <button className="flex items-center gap-3 p-3 rounded-lg text-slate-300 hover:bg-slate-800 w-full transition-colors">
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-slate-200 h-16 flex items-center justify-between px-6 shadow-sm">
          <h2 className="text-lg font-semibold text-slate-800">
            {location.pathname === '/' && 'Operator Dashboard'}
            {location.pathname === '/assess' && 'Stress & Trauma Assessment'}
            {location.pathname.startsWith('/case/') && 'Case Details'}
          </h2>
          <div className="flex items-center gap-6 text-sm text-slate-600">
            <span className="font-mono bg-slate-100 px-3 py-1 rounded-md">{time}</span>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-full bg-nhaa-blue flex items-center justify-center text-white font-bold">
                OP
              </div>
              <span>Operator 1</span>
            </div>
            <span className="text-xs text-slate-400">v1.0.0</span>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-auto p-6">
          <Routes>
            <Route path="/" element={<OperatorDashboard />} />
            <Route path="/assess" element={<AssessmentPage />} />
            <Route path="/case/:caseId" element={<CaseDetailPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;
