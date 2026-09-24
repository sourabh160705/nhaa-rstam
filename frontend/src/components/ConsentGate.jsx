import React from 'react';
import LanguageSelector from './LanguageSelector';
import { AlertCircle } from 'lucide-react';

export default function ConsentGate({ onComplete }) {
  const [language, setLanguage] = React.useState('');
  const [channel, setChannel] = React.useState('');
  const [consentGiven, setConsentGiven] = React.useState(false);

  const isFormValid = language !== '' && channel !== '' && consentGiven;

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isFormValid) {
      onComplete({ language, channel, consentGiven });
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-xl shadow-md border border-slate-200 p-8">
      <h2 className="text-2xl font-bold text-nhaa-navy mb-6 border-b pb-4">Pre-Assessment Verification</h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-6">
          <LanguageSelector value={language} onChange={setLanguage} />
          
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Communication Channel</label>
            <select 
              value={channel} 
              onChange={(e) => setChannel(e.target.value)}
              className="w-full border border-slate-300 rounded-md shadow-sm p-2 bg-white focus:ring-nhaa-blue focus:border-nhaa-blue outline-none"
            >
              <option value="" disabled>Select channel...</option>
              <option value="voice">Voice Call</option>
              <option value="portal">Web Portal</option>
              <option value="chatbot">Chatbot</option>
              <option value="ivrs">IVRS</option>
              <option value="mobile">Mobile App</option>
            </select>
          </div>
        </div>

        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
          <div className="flex gap-3 mb-3 text-slate-700">
            <AlertCircle className="text-nhaa-blue flex-shrink-0" />
            <h3 className="font-semibold">Required Consent Script</h3>
          </div>
          <p className="text-sm text-slate-600 mb-4 ml-9">
            "Before we proceed, I would like to inform you that this conversation may be analyzed by our stress assessment system to better understand your situation and provide appropriate support. Your data will be kept confidential and you have the right to withdraw at any time. Do you consent to this?"
          </p>
          
          <label className="flex items-start gap-3 ml-9 p-3 bg-white rounded border border-slate-200 cursor-pointer hover:bg-slate-50">
            <input 
              type="checkbox" 
              checked={consentGiven}
              onChange={(e) => setConsentGiven(e.target.checked)}
              className="mt-1 h-4 w-4 text-nhaa-blue border-gray-300 rounded focus:ring-nhaa-blue"
            />
            <span className="text-sm font-medium text-slate-800">
              I have informed the caller about the assessment and they have given explicit verbal consent.
            </span>
          </label>
        </div>

        <div className="flex justify-end pt-4 border-t border-slate-100">
          <button
            type="submit"
            disabled={!isFormValid}
            className={`px-6 py-2.5 rounded-lg font-medium transition-colors ${
              isFormValid 
                ? 'bg-nhaa-blue text-white hover:bg-blue-700 shadow-sm' 
                : 'bg-slate-200 text-slate-400 cursor-not-allowed'
            }`}
          >
            Proceed to Assessment
          </button>
        </div>
      </form>
    </div>
  );
}
