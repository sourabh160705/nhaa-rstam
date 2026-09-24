import React, { useState } from 'react';
import ConsentGate from '../components/ConsentGate';
import VoiceRecorder from '../components/VoiceRecorder';
import TextInput from '../components/TextInput';
import SVIGauge from '../components/SVIGauge';
import RiskCard from '../components/RiskCard';
import RecommendationPanel from '../components/RecommendationPanel';
import { Loader2, Mic, Type, FileAudio, RotateCcw } from 'lucide-react';

export default function AssessmentPage() {
  const [step, setStep] = useState(1); // 1: Consent, 2: Input, 3: Processing, 4: Results
  const [inputType, setInputType] = useState('voice'); // voice, text, both
  const [assessmentData, setAssessmentData] = useState(null);

  const handleConsent = (data) => {
    console.log("Consent recorded:", data);
    setStep(2);
  };

  const handleAnalyze = (data) => {
    setStep(3);
    // Mock processing delay and result generation
    setTimeout(() => {
      setAssessmentData({
        score: 82,
        components: [
          { name: 'Voice Emotion', value: 88, color: '#ef4444' },
          { name: 'Text Sentiment', value: 75, color: '#eab308' },
          { name: 'Urgency Lexicon', value: 90, color: '#7f1d1d' },
          { name: 'Hesitation/Pauses', value: 65, color: '#ef4444' }
        ]
      });
      setStep(4);
    }, 3000);
  };

  const resetAssessment = () => {
    setStep(1);
    setAssessmentData(null);
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Progress Indicator */}
      <div className="flex justify-center mb-8">
        <div className="flex items-center gap-2">
          {[1, 2, 3, 4].map((s) => (
            <React.Fragment key={s}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${step >= s ? 'bg-nhaa-blue text-white' : 'bg-slate-200 text-slate-500'}`}>
                {s}
              </div>
              {s < 4 && <div className={`w-12 h-1 transition-colors ${step > s ? 'bg-nhaa-blue' : 'bg-slate-200'}`}></div>}
            </React.Fragment>
          ))}
        </div>
      </div>

      {step === 1 && <ConsentGate onComplete={handleConsent} />}

      {step === 2 && (
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="flex border-b border-slate-200">
            <button onClick={() => setInputType('voice')} className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${inputType === 'voice' ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50' : 'text-slate-500 hover:bg-slate-50'}`}>
              <Mic size={18} /> Voice Assessment
            </button>
            <button onClick={() => setInputType('text')} className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${inputType === 'text' ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50' : 'text-slate-500 hover:bg-slate-50'}`}>
              <Type size={18} /> Text Assessment
            </button>
            <button onClick={() => setInputType('both')} className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${inputType === 'both' ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50' : 'text-slate-500 hover:bg-slate-50'}`}>
              <FileAudio size={18} /> Combined Assessment
            </button>
          </div>
          
          <div className="p-8 bg-slate-50 min-h-[400px] flex items-center justify-center">
            {inputType === 'voice' && <VoiceRecorder onAnalyze={handleAnalyze} />}
            {inputType === 'text' && <TextInput onAnalyze={handleAnalyze} />}
            {inputType === 'both' && (
              <div className="w-full space-y-6">
                <VoiceRecorder onAnalyze={() => {}} />
                <div className="relative flex py-2 items-center">
                  <div className="flex-grow border-t border-slate-300"></div>
                  <span className="flex-shrink-0 mx-4 text-slate-400 text-sm">AND</span>
                  <div className="flex-grow border-t border-slate-300"></div>
                </div>
                <TextInput onAnalyze={handleAnalyze} />
              </div>
            )}
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="bg-white rounded-xl shadow-md border border-slate-200 p-16 flex flex-col items-center justify-center">
          <Loader2 className="h-16 w-16 text-nhaa-blue animate-spin mb-6" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Analyzing Assessment Data</h2>
          <p className="text-slate-500 text-center max-w-md">Processing audio features, computing textual sentiment, and generating SVI score via AI pipeline...</p>
        </div>
      )}

      {step === 4 && assessmentData && (
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-2xl font-bold text-slate-800">Assessment Results</h2>
            <button onClick={resetAssessment} className="flex items-center gap-2 bg-white border border-slate-300 px-4 py-2 rounded-lg text-slate-700 hover:bg-slate-50 font-medium">
              <RotateCcw size={16} /> New Assessment
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1 bg-white rounded-xl shadow-md border border-slate-200 p-6 flex items-center justify-center">
              <SVIGauge score={assessmentData.score} />
            </div>
            <div className="md:col-span-2">
              <RiskCard score={assessmentData.score} components={assessmentData.components} />
            </div>
          </div>
          
          <div className="mt-6">
            <RecommendationPanel />
          </div>
        </div>
      )}
    </div>
  );
}
