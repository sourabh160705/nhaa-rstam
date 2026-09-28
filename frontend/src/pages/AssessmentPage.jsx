import React, { useState } from 'react';
import ConsentGate from '../components/ConsentGate';
import VoiceRecorder from '../components/VoiceRecorder';
import TextInput from '../components/TextInput';
import SVIGauge from '../components/SVIGauge';
import RiskCard from '../components/RiskCard';
import RecommendationPanel from '../components/RecommendationPanel';
import { api } from '../services/api';
import { Loader2, Mic, Type, FileAudio, RotateCcw, AlertTriangle, CheckCircle, ShieldAlert } from 'lucide-react';

const COMPONENT_LABELS = {
  text_sentiment: 'Text Sentiment',
  trauma_keywords: 'Trauma Keywords',
  suicidal_ideation: 'Suicidal Ideation',
  acoustic_distress: 'Acoustic Distress',
  voice_emotion: 'Voice Emotion',
  contextual: 'Contextual Factors'
};

export default function AssessmentPage() {
  const [step, setStep] = useState(1); // 1: Consent, 2: Input, 3: Processing, 4: Results
  const [inputType, setInputType] = useState('text'); // 'text', 'voice', 'both'
  const [assessmentData, setAssessmentData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Store inputs for 'both' mode
  const [recordedAudio, setRecordedAudio] = useState(null);
  const [narrativeText, setNarrativeText] = useState('');

  const handleConsent = (data) => {
    console.log("Consent recorded:", data);
    setStep(2);
  };

  const processResponse = (res) => {
    const svi = res.data.svi || {};
    const rawComponents = svi.components || [];

    const formattedComponents = rawComponents.map((c) => {
      const raw = Math.round(c.raw_score || 0);
      let color = '#22c55e'; // Green (Low)
      if (raw > 75) color = '#7f1d1d'; // Dark Red (Critical)
      else if (raw > 50) color = '#ef4444'; // Red (High)
      else if (raw > 25) color = '#eab308'; // Amber (Moderate)

      return {
        name: COMPONENT_LABELS[c.name] || c.name.replace(/_/g, ' '),
        value: raw,
        color: color
      };
    });

    setAssessmentData({
      caseId: res.data.case_id,
      score: Math.round(svi.total_score || 0),
      riskLevel: (svi.risk_level || 'LOW').toUpperCase(),
      autoEscalated: svi.auto_escalated || false,
      escalationReason: svi.escalation_reason || '',
      components: formattedComponents,
      recommendations: res.data.recommendations || [],
      voiceAnalysis: res.data.voice_analysis || null,
      textAnalysis: res.data.text_analysis || null,
      createdAt: res.data.created_at || new Date().toISOString()
    });

    setStep(4);
  };

  const handleAnalyzeText = async (text) => {
    setLoading(true);
    setError(null);
    setStep(3);

    try {
      const res = await api.assessText({
        text: text,
        language: 'en',
        channel: 'PORTAL'
      });
      processResponse(res);
    } catch (err) {
      console.error('Text assessment error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to complete text assessment.');
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeVoice = async (audioFile) => {
    if (!audioFile) {
      alert('Please provide an audio recording or file.');
      return;
    }
    setLoading(true);
    setError(null);
    setStep(3);

    try {
      const formData = new FormData();
      formData.append('audio', audioFile);
      formData.append('channel', 'VOICE_CALL');

      const res = await api.assessVoice(formData);
      processResponse(res);
    } catch (err) {
      console.error('Voice assessment error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to complete voice assessment.');
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeCombined = async (text) => {
    if (!recordedAudio) {
      alert('Please record or upload an audio file first for combined assessment.');
      return;
    }
    setLoading(true);
    setError(null);
    setStep(3);

    try {
      const formData = new FormData();
      formData.append('audio', recordedAudio);
      formData.append('text', text || narrativeText);
      formData.append('channel', 'PORTAL');

      const res = await api.assessCombined(formData);
      processResponse(res);
    } catch (err) {
      console.error('Combined assessment error:', err);
      setError(err.response?.data?.detail || err.message || 'Failed to complete combined assessment.');
      setStep(2);
    } finally {
      setLoading(false);
    }
  };

  const resetAssessment = () => {
    setStep(1);
    setAssessmentData(null);
    setError(null);
    setRecordedAudio(null);
    setNarrativeText('');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Progress Indicator */}
      <div className="flex justify-center mb-8">
        <div className="flex items-center gap-2">
          {[
            { num: 1, label: 'Consent' },
            { num: 2, label: 'Input' },
            { num: 3, label: 'Analysis' },
            { num: 4, label: 'Results' }
          ].map((s) => (
            <React.Fragment key={s.num}>
              <div className="flex flex-col items-center">
                <div
                  className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm transition-colors ${
                    step >= s.num ? 'bg-nhaa-blue text-white shadow' : 'bg-slate-200 text-slate-500'
                  }`}
                >
                  {step > s.num ? <CheckCircle size={16} /> : s.num}
                </div>
                <span className={`text-xs mt-1 font-medium ${step >= s.num ? 'text-nhaa-blue' : 'text-slate-400'}`}>
                  {s.label}
                </span>
              </div>
              {s.num < 4 && (
                <div
                  className={`w-16 h-1 mb-4 transition-colors ${
                    step > s.num ? 'bg-nhaa-blue' : 'bg-slate-200'
                  }`}
                />
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-xl flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0" />
            <span className="text-sm font-medium">{error}</span>
          </div>
          <button
            onClick={() => setError(null)}
            className="text-xs bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded-lg font-semibold"
          >
            Dismiss
          </button>
        </div>
      )}

      {step === 1 && <ConsentGate onComplete={handleConsent} />}

      {step === 2 && (
        <div className="bg-white rounded-xl shadow-md border border-slate-200 overflow-hidden">
          <div className="flex border-b border-slate-200">
            <button
              onClick={() => setInputType('text')}
              className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${
                inputType === 'text'
                  ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50'
                  : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              <Type size={18} /> Text Assessment
            </button>
            <button
              onClick={() => setInputType('voice')}
              className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${
                inputType === 'voice'
                  ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50'
                  : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              <Mic size={18} /> Voice Assessment
            </button>
            <button
              onClick={() => setInputType('both')}
              className={`flex-1 py-4 flex justify-center items-center gap-2 font-medium transition-colors ${
                inputType === 'both'
                  ? 'text-nhaa-blue border-b-2 border-nhaa-blue bg-blue-50'
                  : 'text-slate-500 hover:bg-slate-50'
              }`}
            >
              <FileAudio size={18} /> Combined Assessment
            </button>
          </div>

          <div className="p-8 bg-slate-50 min-h-[400px] flex items-center justify-center">
            {inputType === 'text' && <TextInput onAnalyze={handleAnalyzeText} />}
            {inputType === 'voice' && <VoiceRecorder onAnalyze={handleAnalyzeVoice} />}
            {inputType === 'both' && (
              <div className="w-full space-y-6 max-w-3xl">
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-2">Step A: Voice Recording</h4>
                  <VoiceRecorder onAnalyze={(f) => setRecordedAudio(f)} />
                  {recordedAudio && (
                    <p className="text-xs text-green-600 font-semibold mt-2">
                      Audio file loaded: {recordedAudio.name}
                    </p>
                  )}
                </div>
                <div className="relative flex py-2 items-center">
                  <div className="flex-grow border-t border-slate-300"></div>
                  <span className="flex-shrink-0 mx-4 text-slate-400 text-sm font-bold">AND</span>
                  <div className="flex-grow border-t border-slate-300"></div>
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-700 mb-2">Step B: Narrative Text</h4>
                  <TextInput onAnalyze={handleAnalyzeCombined} />
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="bg-white rounded-xl shadow-md border border-slate-200 p-16 flex flex-col items-center justify-center">
          <Loader2 className="h-16 w-16 text-nhaa-blue animate-spin mb-6" />
          <h2 className="text-2xl font-bold text-slate-800 mb-2">Running Real-Time AI Assessment</h2>
          <p className="text-slate-500 text-center max-w-md">
            Executing acoustic feature extraction, sentiment analysis, trauma keyword detection, and calculating composite SVI score...
          </p>
        </div>
      )}

      {step === 4 && assessmentData && (
        <div className="space-y-6">
          <div className="flex justify-between items-center bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div>
              <h2 className="text-xl font-bold text-slate-800 flex items-center gap-3">
                Assessment Results
                <span
                  className={`text-xs px-3 py-1 rounded-full font-bold uppercase ${
                    assessmentData.score > 75
                      ? 'bg-red-100 text-red-800 border border-red-300'
                      : assessmentData.score > 50
                      ? 'bg-orange-100 text-orange-800 border border-orange-300'
                      : assessmentData.score > 25
                      ? 'bg-amber-100 text-amber-800 border border-amber-300'
                      : 'bg-green-100 text-green-800 border border-green-300'
                  }`}
                >
                  {assessmentData.riskLevel} RISK
                </span>
              </h2>
              {assessmentData.caseId && (
                <p className="text-xs text-slate-500 mt-1 font-mono">
                  Case ID: {assessmentData.caseId}
                </p>
              )}
            </div>
            <button
              onClick={resetAssessment}
              className="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 border border-slate-300 px-4 py-2 rounded-lg text-slate-700 font-medium transition-colors"
            >
              <RotateCcw size={16} /> New Assessment
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-1 bg-white rounded-xl shadow-md border border-slate-200 p-6 flex flex-col items-center justify-center">
              <h3 className="w-full text-left font-semibold text-slate-800 mb-4">Overall SVI Score</h3>
              <SVIGauge score={assessmentData.score} />
            </div>
            <div className="md:col-span-2">
              <RiskCard
                score={assessmentData.score}
                components={assessmentData.components}
                autoEscalated={assessmentData.autoEscalated}
                escalationReason={assessmentData.escalationReason}
              />
            </div>
          </div>

          {/* AI Details: Keywords, Sentiment, Transcript */}
          {assessmentData.textAnalysis && (
            <div className="bg-white rounded-xl shadow-md border border-slate-200 p-6 space-y-4">
              <h3 className="font-semibold text-slate-800 border-b pb-2">Analysis Breakdown</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-500 font-medium">Detected Language: </span>
                  <span className="font-semibold text-slate-700 uppercase">
                    {assessmentData.textAnalysis.detected_language || 'EN'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-500 font-medium">Sentiment Score: </span>
                  <span className="font-semibold text-slate-700">
                    {assessmentData.textAnalysis.sentiment != null ? assessmentData.textAnalysis.sentiment.toFixed(2) : '—'}
                  </span>
                </div>
              </div>

              {assessmentData.textAnalysis.trauma_keywords?.length > 0 && (
                <div>
                  <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-2">
                    Trauma Keywords Detected
                  </span>
                  <div className="flex flex-wrap gap-2">
                    {assessmentData.textAnalysis.trauma_keywords.map((kw, i) => (
                      <span
                        key={i}
                        className="px-2.5 py-1 bg-red-50 text-red-700 border border-red-200 rounded-md text-xs font-semibold"
                      >
                        {kw.keyword} ({kw.category})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div>
            <RecommendationPanel recommendations={assessmentData.recommendations} />
          </div>
        </div>
      )}
    </div>
  );
}
