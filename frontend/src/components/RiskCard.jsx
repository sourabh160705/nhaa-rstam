import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, Clock } from 'lucide-react';

export default function RiskCard({ score = 0, components = [], autoEscalated = false, escalationReason = '' }) {
  const isCritical = score > 75 || autoEscalated;
  const isHigh = score > 50 && score <= 75;

  const data = components.length > 0 ? components : [
    { name: 'Analysis', value: Math.round(score), color: score > 75 ? '#ef4444' : score > 50 ? '#f97316' : score > 25 ? '#eab308' : '#22c55e' }
  ];

  return (
    <div className={`bg-white rounded-xl shadow-md border ${isCritical ? 'border-red-500' : 'border-slate-200'} overflow-hidden flex flex-col h-full`}>
      <div className={`p-4 flex justify-between items-center ${isCritical ? 'bg-red-50' : 'bg-slate-50'} border-b ${isCritical ? 'border-red-200' : 'border-slate-200'}`}>
        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
          {isCritical && <AlertTriangle className="text-red-600 h-5 w-5" />}
          Risk Analysis Breakdown
        </h3>
        <div className="flex items-center gap-1 text-sm font-medium text-slate-600 bg-white px-3 py-1 rounded-full border border-slate-200 shadow-sm">
          <Clock className="h-4 w-4" />
          SLA: {isCritical ? '< 2 mins' : isHigh ? '< 15 mins' : '< 1 hr'}
        </div>
      </div>

      <div className="p-5 flex-1 flex flex-col">
        {autoEscalated && (
          <div className="bg-red-600 text-white p-3 rounded-lg text-sm font-medium mb-4 flex items-center gap-2 animate-pulse">
            <AlertTriangle className="h-4 w-4 flex-shrink-0" />
            <span>AUTO-ESCALATION TRIGGERED: {escalationReason || 'Immediate supervisor attention required.'}</span>
          </div>
        )}

        <div className="flex-1 w-full min-h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} width={140} />
              <Tooltip
                cursor={{ fill: '#f1f5f9' }}
                contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                formatter={(val) => [`${val} / 100`, 'Score']}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
