import React from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { AlertTriangle, Clock } from 'lucide-react';

export default function RiskCard({ score, components }) {
  // Default fallback data if none provided
  const data = components || [
    { name: 'Voice Emotion', value: 65, color: '#ef4444' },
    { name: 'Text Sentiment', value: 45, color: '#eab308' },
    { name: 'Urgency Lexicon', value: 80, color: '#7f1d1d' },
    { name: 'Hesitation', value: 30, color: '#22c55e' }
  ];

  const isCritical = score > 75;
  const isHigh = score > 50 && score <= 75;

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
        {isCritical && (
          <div className="bg-red-600 text-white p-3 rounded-lg text-sm font-medium mb-4 flex items-center gap-2 animate-pulse">
            <AlertTriangle className="h-4 w-4" />
            AUTO-ESCALATION TRIGGERED: Immediate supervisor attention required.
          </div>
        )}

        <div className="flex-1 w-full min-h-[200px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
              <XAxis type="number" domain={[0, 100]} hide />
              <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{ fill: '#475569', fontSize: 12 }} width={120} />
              <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
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
