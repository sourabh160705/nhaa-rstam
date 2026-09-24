import React from 'react';
import { CheckCircle2, Clock, AlertTriangle, PlayCircle } from 'lucide-react';

export default function CaseTimeline({ events = [] }) {
  if (events.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-md border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-800 mb-6">Case Timeline</h3>
        <p className="text-center text-slate-400 text-sm py-4">No events recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-md border border-slate-200 p-5">
      <h3 className="font-semibold text-slate-800 mb-6">Case Timeline</h3>

      <div className="relative pl-3">
        {/* Vertical line */}
        <div className="absolute left-[27px] top-2 bottom-2 w-0.5 bg-slate-200"></div>

        <div className="space-y-6 relative">
          {events.map((event) => (
            <div key={event.id} className="flex gap-4">
              <div className="relative z-10 flex-shrink-0 bg-white mt-0.5">
                {event.status === 'done' ? (
                  <CheckCircle2 className="h-5 w-5 text-green-500 bg-white" />
                ) : event.status === 'alert' ? (
                  <AlertTriangle className="h-5 w-5 text-red-500 bg-white" />
                ) : event.status === 'active' ? (
                  <PlayCircle className="h-5 w-5 text-blue-500 bg-white" />
                ) : (
                  <Clock className="h-5 w-5 text-amber-500 bg-white" />
                )}
              </div>
              <div>
                <p className={`text-sm font-medium ${event.status === 'alert' ? 'text-red-700' : 'text-slate-800'}`}>
                  {event.title}
                </p>
                <div className="flex items-center gap-2 mt-1 text-xs text-slate-500">
                  <span>{event.timestamp}</span>
                  <span>•</span>
                  <span>{event.actor}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
