import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { ShieldAlert, Users, Clock, ArrowRight, AlertTriangle, Loader2, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function OperatorDashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [trends, setTrends] = useState([]);
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsRes, alertsRes, trendsRes, casesRes] = await Promise.all([
        api.getDashboardStats(),
        api.getAlerts(),
        api.getTrends(),
        api.getCases({ limit: 10 }),
      ]);
      setStats(statsRes.data);
      setAlerts(alertsRes.data);
      setTrends(trendsRes.data);
      setCases(Array.isArray(casesRes.data) ? casesRes.data : casesRes.data.cases || []);
    } catch (err) {
      console.error('Dashboard fetch error:', err);
      setError('Failed to load dashboard data. Is the backend running?');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const getRiskBadge = (risk) => {
    const r = (risk || '').toUpperCase();
    const styles = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
      MODERATE: 'bg-amber-100 text-amber-800 border-amber-200',
      LOW: 'bg-green-100 text-green-800 border-green-200',
    };
    return (
      <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${styles[r] || 'bg-slate-100 text-slate-600 border-slate-200'}`}>
        {r}
      </span>
    );
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    const d = new Date(dateStr);
    const now = new Date();
    const isToday = d.toDateString() === now.toDateString();
    const time = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return isToday ? `Today, ${time}` : `${d.toLocaleDateString()}, ${time}`;
  };

  // Prepare trend chart data
  const trendChartData = trends.map((t) => ({
    name: t.date ? new Date(t.date).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' }) : t.date,
    critical: t.CRITICAL || 0,
    high: t.HIGH || 0,
    moderate: t.MODERATE || 0,
    low: t.LOW || 0,
  }));

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 text-nhaa-blue animate-spin" />
        <span className="ml-3 text-slate-500 text-lg">Loading dashboard...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertTriangle className="h-10 w-10 text-amber-500" />
        <p className="text-slate-600">{error}</p>
        <button onClick={fetchDashboardData} className="px-4 py-2 bg-nhaa-blue text-white rounded-lg hover:bg-blue-600 transition-colors">
          Retry
        </button>
      </div>
    );
  }

  const totalToday = stats?.total_cases_today || 0;
  const criticalAlerts = stats?.critical_alerts || 0;
  const highRisk = stats?.risk_distribution?.HIGH || 0;
  const pendingActions = stats?.pending_actions || 0;

  // Find the most critical alert for the banner
  const topAlert = alerts.length > 0 ? alerts[0] : null;

  return (
    <div className="space-y-6">
      {/* Alert Banner — only show if there's a real critical alert */}
      {topAlert && (
        <div className="bg-red-600 text-white px-4 py-3 rounded-lg shadow-sm flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ShieldAlert className="h-5 w-5 animate-pulse" />
            <span className="font-medium">
              Critical Alert: Case {topAlert.case_id?.substring(0, 8)}... — SVI Score {topAlert.svi_score?.toFixed(1)} — {topAlert.auto_escalated ? 'AUTO-ESCALATED' : 'Requires Action'}
            </span>
          </div>
          <button
            onClick={() => navigate(`/case/${topAlert.case_id}`)}
            className="text-sm bg-white text-red-600 px-3 py-1 rounded font-bold hover:bg-red-50"
          >
            Action Now
          </button>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg"><Users className="h-6 w-6" /></div>
          <div>
            <p className="text-slate-500 text-sm">Total Cases Today</p>
            <p className="text-2xl font-bold text-slate-800">{totalToday}</p>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-red-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-red-100 text-red-600 rounded-lg"><ShieldAlert className="h-6 w-6" /></div>
          <div>
            <p className="text-red-600 text-sm font-medium">Critical Alerts</p>
            <p className="text-2xl font-bold text-red-700">{criticalAlerts}</p>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-orange-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-orange-100 text-orange-600 rounded-lg"><AlertTriangle className="h-6 w-6" /></div>
          <div>
            <p className="text-orange-600 text-sm font-medium">High Risk Cases</p>
            <p className="text-2xl font-bold text-orange-700">{highRisk}</p>
          </div>
        </div>
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-100 text-blue-600 rounded-lg"><Clock className="h-6 w-6" /></div>
          <div>
            <p className="text-slate-500 text-sm">Pending Actions</p>
            <p className="text-2xl font-bold text-slate-800">{pendingActions}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Cases Table */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex justify-between items-center bg-slate-50">
            <h3 className="font-semibold text-slate-800">Recent Cases</h3>
            <div className="flex items-center gap-2">
              <button onClick={fetchDashboardData} className="p-1.5 text-slate-400 hover:text-nhaa-blue hover:bg-blue-50 rounded transition-colors" title="Refresh">
                <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button onClick={() => navigate('/cases')} className="text-sm text-nhaa-blue font-medium hover:underline">View All</button>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-50 text-slate-600 border-b border-slate-200">
                <tr>
                  <th className="p-4 font-medium">Case ID</th>
                  <th className="p-4 font-medium">Risk Level</th>
                  <th className="p-4 font-medium">SVI</th>
                  <th className="p-4 font-medium">Channel</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium">Date</th>
                  <th className="p-4 font-medium">Action</th>
                </tr>
              </thead>
              <tbody>
                {cases.length === 0 ? (
                  <tr>
                    <td colSpan="7" className="p-8 text-center text-slate-400">
                      No cases found. New assessments will appear here.
                    </td>
                  </tr>
                ) : (
                  cases.map((c) => (
                    <tr key={c.case_id || c.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                      <td className="p-4 font-mono text-slate-700">{(c.case_id || c.id || '').substring(0, 8)}...</td>
                      <td className="p-4">{getRiskBadge(c.risk_level)}</td>
                      <td className="p-4 font-bold text-slate-700">{c.svi_score != null ? c.svi_score.toFixed(1) : '—'}</td>
                      <td className="p-4 text-slate-600">{c.channel || '—'}</td>
                      <td className="p-4 text-slate-600">{c.status || '—'}</td>
                      <td className="p-4 text-slate-500 text-xs">{formatDate(c.created_at)}</td>
                      <td className="p-4">
                        <button
                          onClick={() => navigate(`/case/${c.case_id || c.id}`)}
                          className="p-1.5 text-slate-400 hover:text-nhaa-blue hover:bg-blue-50 rounded transition-colors"
                        >
                          <ArrowRight className="h-5 w-5" />
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trend Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4">
          <h3 className="font-semibold text-slate-800 mb-4">30-Day Risk Trends</h3>
          <div className="h-[300px]">
            {trendChartData.length === 0 ? (
              <div className="flex items-center justify-center h-full text-slate-400">
                No trend data yet. Assessments will populate this chart.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={trendChartData}>
                  <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                  <Tooltip />
                  <Bar dataKey="critical" stackId="a" fill="#7f1d1d" name="Critical" />
                  <Bar dataKey="high" stackId="a" fill="#ef4444" name="High" />
                  <Bar dataKey="moderate" stackId="a" fill="#eab308" name="Moderate" />
                  <Bar dataKey="low" stackId="a" fill="#22c55e" name="Low" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
