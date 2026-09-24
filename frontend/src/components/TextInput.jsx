import React, { useState } from 'react';
import { FileText } from 'lucide-react';

export default function TextInput({ onAnalyze }) {
  const [text, setText] = useState('');
  
  const minChars = 10;
  const maxChars = 50000;
  const isValid = text.length >= minChars && text.length <= maxChars;

  return (
    <div className="w-full max-w-3xl mx-auto bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col">
      <div className="bg-slate-50 border-b border-slate-200 p-3 flex justify-between items-center">
        <div className="flex items-center gap-2 text-slate-700 font-medium text-sm">
          <FileText size={16} />
          Victim Narrative
        </div>
        <div className="text-xs text-slate-500 flex gap-4">
          <span>Auto-detect language: <span className="text-green-600 font-medium">Active</span></span>
        </div>
      </div>
      
      <textarea
        className="w-full h-64 p-4 focus:outline-none resize-none text-slate-800"
        placeholder="Enter the victim/complainant narrative here..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      
      <div className="p-4 border-t border-slate-100 flex justify-between items-center bg-slate-50">
        <span className={`text-xs ${text.length > maxChars ? 'text-red-500' : 'text-slate-500'}`}>
          {text.length} / {maxChars} characters {text.length < minChars && `(Min ${minChars})`}
        </span>
        
        <button
          onClick={() => onAnalyze(text)}
          disabled={!isValid}
          className={`px-5 py-2 rounded-lg font-medium transition-colors ${
            isValid 
              ? 'bg-nhaa-blue text-white hover:bg-blue-700 shadow-sm' 
              : 'bg-slate-200 text-slate-400 cursor-not-allowed'
          }`}
        >
          Analyze Text
        </button>
      </div>
    </div>
  );
}
