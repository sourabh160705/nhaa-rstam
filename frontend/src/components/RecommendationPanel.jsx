import React, { useState } from 'react';
import { AlertCircle, Phone, Truck, Shield, Scale, HeartPulse, Home, Info, CalendarClock, CheckCircle2 } from 'lucide-react';

export default function RecommendationPanel({ recommendations = [] }) {
  const [items, setItems] = useState([]);

  // Sync state when recommendations prop changes
  React.useEffect(() => {
    setItems(recommendations.map((r, i) => ({
      id: r.id || i,
      type: r.intervention_type || r.type || 'info',
      title: r.description || r.title || 'Intervention',
      desc: r.action_details || r.desc || '',
      sla: r.response_sla || r.sla || '—',
      priority: r.priority != null ? r.priority : 4,
      status: r.status?.toLowerCase() || 'pending',
    })));
  }, [recommendations]);

  const getIcon = (type) => {
    const t = (type || '').toUpperCase();
    if (t.includes('POLICE') || t.includes('DISPATCH')) return <Truck className="h-5 w-5 text-blue-600" />;
    if (t.includes('COUNSEL') || t.includes('CRISIS')) return <Phone className="h-5 w-5 text-purple-600" />;
    if (t.includes('LEGAL')) return <Scale className="h-5 w-5 text-indigo-600" />;
    if (t.includes('MEDICAL')) return <HeartPulse className="h-5 w-5 text-pink-600" />;
    if (t.includes('PROTECT') || t.includes('WITNESS')) return <Shield className="h-5 w-5 text-amber-600" />;
    if (t.includes('REHAB')) return <Home className="h-5 w-5 text-teal-600" />;
    if (t.includes('FOLLOW') || t.includes('SCHEDULE')) return <CalendarClock className="h-5 w-5 text-sky-600" />;
    if (t.includes('INFO')) return <Info className="h-5 w-5 text-slate-600" />;
    return <AlertCircle className="h-5 w-5 text-slate-600" />;
  };

  const getPriorityStyle = (priority) => {
    if (priority <= 1) return 'border-l-4 border-l-red-600';
    if (priority <= 2) return 'border-l-4 border-l-orange-500';
    return '';
  };

  const handleAction = (id) => {
    setItems(items.map(item => item.id === id ? { ...item, status: 'dispatched' } : item));
    setTimeout(() => {
      setItems(current => current.map(item => item.id === id ? { ...item, status: 'completed' } : item));
    }, 2000);
  };

  if (items.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
        <div className="p-4 bg-slate-50 border-b border-slate-200">
          <h3 className="font-semibold text-slate-800">Recommended Interventions</h3>
        </div>
        <div className="p-8 text-center text-slate-400">
          No interventions recommended for this case.
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
      <div className="p-4 bg-slate-50 border-b border-slate-200">
        <h3 className="font-semibold text-slate-800">Recommended Interventions ({items.length})</h3>
      </div>
      <div className="p-0">
        {items.map((item, idx) => (
          <div
            key={item.id}
            className={`p-4 border-b border-slate-100 flex items-start gap-4 transition-colors hover:bg-slate-50 ${getPriorityStyle(item.priority)} ${idx === items.length - 1 ? 'border-b-0' : ''}`}
          >
            <div className={`p-2 rounded-full mt-1 ${item.priority <= 1 ? 'bg-red-100' : 'bg-slate-100'}`}>
              {getIcon(item.type)}
            </div>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <h4 className="font-medium text-slate-900">{item.title}</h4>
                <span className="text-xs font-semibold px-2 py-1 bg-slate-100 text-slate-600 rounded">SLA: {item.sla}</span>
              </div>
              <p className="text-sm text-slate-600 mt-1 mb-3">{item.desc}</p>

              <div className="flex items-center gap-3">
                {item.status === 'pending' ? (
                  <button
                    onClick={() => handleAction(item.id)}
                    className="text-sm px-4 py-1.5 rounded font-medium text-white shadow-sm transition-colors bg-nhaa-blue hover:bg-blue-700"
                  >
                    Execute
                  </button>
                ) : item.status === 'dispatched' ? (
                  <span className="flex items-center gap-1.5 text-sm font-medium text-amber-600">
                    <span className="animate-spin h-4 w-4 border-2 border-amber-600 border-t-transparent rounded-full"></span>
                    Processing...
                  </span>
                ) : (
                  <span className="flex items-center gap-1.5 text-sm font-medium text-green-600">
                    <CheckCircle2 className="h-5 w-5" />
                    Completed
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
