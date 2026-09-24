import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Printer, Download, Loader2, AlertTriangle } from 'lucide-react';
import SVIGauge from '../components/SVIGauge';
import RiskCard from '../components/RiskCard';
import RecommendationPanel from '../components/RecommendationPanel';
import CaseTimeline from '../components/CaseTimeline';
import { api } from '../services/api';

export default function CaseDetailPage() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCase = async () => {
      setLoading(true);
      setError(null);
      try {
        const [caseRes, recsRes] = await Promise.all([
          api.getAssessment(caseId),
          api.getRecommendations(caseId).catch(() => ({ data: [] })),
        ]);
        setCaseData(caseRes.data);
        setRecommendations(Array.isArray(recsRes.data) ? recsRes.data : []);
      } catch (err) {
        console.error('Case fetch error:', err);
        setError('Failed to load case details.');
      } finally {
        setLoading(false);
      }
    };
    if (caseId) fetchCase();
  }, [caseId]);

  const formatDate = (dateStr) => {
    if (!dateStr) return '—';
    return new Date(dateStr).toLocaleString([], {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  const getRiskBadgeStyle = (level) => {
    const r = (level || '').toUpperCase();
    const styles = {
      CRITICAL: 'bg-red-100 text-red-800 border-red-200',
      HIGH: 'bg-orange-100 text-orange-800 border-orange-200',
      MODERATE: 'bg-amber-100 text-amber-800 border-amber-200',
      LOW: 'bg-green-100 text-green-800 border-green-200',
    };
    return styles[r] || 'bg-slate-100 text-slate-600 border-slate-200';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 text-nhaa-blue animate-spin" />
        <span className="ml-3 text-slate-500 text-lg">Loading case details...</span>
      </div>
    );
  }

  if (error || !caseData) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <AlertTriangle className="h-10 w-10 text-amber-500" />
        <p className="text-slate-600">{error || 'Case not found.'}</p>
        <button onClick={() => navigate(-1)} className="px-4 py-2 bg-nhaa-blue text-white rounded-lg hover:bg-blue-600">
          Go Back
        </button>
      </div>
    );
  }

  const svi = caseData.svi || {};
  const score = svi.total_score || 0;
  const riskLevel = (svi.risk_level || caseData.risk_level || '').toUpperCase();
  const components = (svi.components || []).map((c, i) => ({
    name: c.name || `Component ${i + 1}`,
    value: c.weighted_score || c.raw_score || 0,
    color: c.weighted_score > 60 ? '#ef4444' : c.weighted_score > 30 ? '#eab308' : '#22c55e',
  }));

  const voiceAnalysis = caseData.voice_analysis;
  const textAnalysis = caseData.text_analysis;

  // Build timeline from real data
  const timelineEvents = [];
  timelineEvents.push({
    id: 'created',
    title: 'Case Created',
    timestamp: formatDate(caseData.created_at),
    actor: 'System',
    status: 'done',
  });
  if (voiceAnalysis) {
    timelineEvents.push({
      id: 'voice',
      title: `Voice Assessment Completed — ${voiceAnalysis.detected_language || 'unknown'} detected`,
      timestamp: formatDate(caseData.created_at),
      actor: 'System (AI)',
      status: 'done',
    });
  }
  if (textAnalysis) {
    timelineEvents.push({
      id: 'text',
      title: `Text Assessment Completed`,
      timestamp: formatDate(caseData.created_at),
      actor: 'System (AI)',
      status: 'done',
    });
  }
  timelineEvents.push({
    id: 'svi',
    title: `SVI Computed (Score: ${score.toFixed(1)})`,
    timestamp: formatDate(svi.timestamp || caseData.created_at),
    actor: 'System (AI)',
    status: riskLevel === 'CRITICAL' || riskLevel === 'HIGH' ? 'alert' : 'done',
  });
  if (svi.auto_escalated) {
    timelineEvents.push({
      id: 'escalated',
      title: `Auto-Escalated: ${svi.escalation_reason || 'Risk threshold exceeded'}`,
      timestamp: formatDate(svi.timestamp || caseData.created_at),
      actor: 'System',
      status: 'alert',
    });
  }
  if (recommendations.length > 0) {
    timelineEvents.push({
      id: 'recs',
      title: `${recommendations.length} Interventions Recommended`,
      timestamp: formatDate(caseData.created_at),
      actor: 'System',
      status: 'pending',
    });
  }

  const handleExportJSON = () => {
    const blob = new Blob([JSON.stringify(caseData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `case-${caseId}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 pb-12">
      {/* Header Actions */}
      <div className="flex items-center justify-between bg-white p-4 rounded-xl shadow-sm border border-slate-200">
        <div className="flex items-center gap-4">
          <button onClick={() => navigate(-1)} className="p-2 text-slate-500 hover:bg-slate-100 rounded-full transition-colors">
            <ArrowLeft size={20} />
          </button>
          <div>
            <h1 className="text-xl font-bold text-slate-800 flex items-center gap-3">
              {caseId?.substring(0, 8)}...
              <span className={`px-2.5 py-1 text-xs font-semibold rounded-full border ${getRiskBadgeStyle(riskLevel)}`}>
                {riskLevel} RISK
              </span>
            </h1>
            <p className="text-sm text-slate-500 mt-1">
              {caseData.channel || '—'} • {caseData.language || '—'} • {formatDate(caseData.created_at)}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => window.print()} className="flex items-center gap-2 px-4 py-2 text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 font-medium">
            <Printer size={16} /> Print
          </button>
          <button onClick={handleExportJSON} className="flex items-center gap-2 px-4 py-2 text-slate-600 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 font-medium">
            <Download size={16} /> Export JSON
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - SVI & Risk */}
        <div className="lg:col-span-2 space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center h-[350px]">
              <h3 className="w-full text-left font-semibold text-slate-800 mb-4">Overall Stress Vulnerability</h3>
              <SVIGauge score={score} />
            </div>
            <div className="h-[350px]">
              <RiskCard score={score} components={components} />
            </div>
          </div>

          <RecommendationPanel recommendations={recommendations} />

          {/* Detailed Analysis Section */}
          {(textAnalysis || voiceAnalysis) && (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
              <div className="p-4 bg-slate-50 border-b border-slate-200">
                <h3 className="font-semibold text-slate-800">Detailed AI Analysis</h3>
              </div>
              <div className="p-6 space-y-4">
                {/* Voice transcript */}
                {voiceAnalysis?.transcript && (
                  <div>
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-600 rounded text-xs font-medium mb-2">
                      Voice Transcript ({voiceAnalysis.detected_language || 'auto'})
                    </span>
                    <p className="text-slate-800 bg-slate-50 p-4 border-l-4 border-nhaa-blue italic">
                      "{voiceAnalysis.transcript}"
                    </p>
                  </div>
                )}

                {/* Original text */}
                {textAnalysis?.original_text && (
                  <div>
                    <span className="inline-block px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-medium mb-2">
                      Original Text ({textAnalysis.detected_language || 'auto'})
                    </span>
                    <p className="text-slate-800 italic bg-slate-50 p-4 border-l-4 border-slate-300">
                      "{textAnalysis.original_text}"
                    </p>
                  </div>
                )}

                {/* Translated text */}
                {textAnalysis?.translated_text && textAnalysis.translated_text !== textAnalysis.original_text && (
                  <div>
                    <span className="inline-block px-2 py-1 bg-slate-100 text-slate-600 rounded text-xs font-medium mb-2">
                      Translated (English)
                    </span>
                    <p className="text-slate-800 bg-slate-50 p-4 border-l-4 border-nhaa-blue">
                      "{textAnalysis.translated_text}"
                    </p>
                  </div>
                )}

                {/* Sentiment score */}
                {textAnalysis?.sentiment_score != null && (
                  <div className="flex items-center gap-3">
                    <span className="text-sm font-medium text-slate-600">Sentiment:</span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${textAnalysis.sentiment_score < -0.3 ? 'bg-red-100 text-red-700' : textAnalysis.sentiment_score > 0.3 ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                      {textAnalysis.sentiment_score.toFixed(2)} ({textAnalysis.sentiment_score < -0.3 ? 'Negative' : textAnalysis.sentiment_score > 0.3 ? 'Positive' : 'Neutral'})
                    </span>
                  </div>
                )}

                {/* Suicidal ideation flag */}
                {textAnalysis?.suicidal_ideation_flag && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-red-600 flex-shrink-0" />
                    <span className="text-sm font-medium text-red-800">
                      Suicidal Ideation Detected (Confidence: {((textAnalysis.suicidal_ideation_confidence || 0) * 100).toFixed(0)}%)
                    </span>
                  </div>
                )}

                {/* Trauma keywords */}
                {textAnalysis?.trauma_keywords && textAnalysis.trauma_keywords.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-slate-600 mb-2 block">Trauma Keywords Detected:</span>
                    <div className="flex flex-wrap gap-2">
                      {textAnalysis.trauma_keywords.map((kw, i) => (
                        <span key={i} className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">
                          "{kw.keyword}" ({kw.category})
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Right Column - Timeline */}
        <div className="lg:col-span-1">
          <CaseTimeline events={timelineEvents} />
        </div>
      </div>
    </div>
  );
}
