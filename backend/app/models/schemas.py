from datetime import datetime
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from uuid import UUID
from .enums import (
    RiskLevel, InputChannel, Language, CaseStatus, 
    EmotionLabel, InterventionType, ConsentStatus
)

class ConsentRecord(BaseModel):
    case_id: UUID
    granted_at: datetime
    method: str
    language: str
    ip_hash: Optional[str] = None

class TextAssessmentRequest(BaseModel):
    text: str
    language: Optional[str] = None
    channel: InputChannel
    context_data: Optional[Dict[str, Any]] = None

class VoiceAssessmentRequest(BaseModel):
    channel: InputChannel
    language: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class CombinedAssessmentRequest(BaseModel):
    text: Optional[str] = None
    channel: InputChannel
    language: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None

class AcousticFeatures(BaseModel):
    mean_pitch: float
    pitch_std: float
    pitch_range: float
    speech_rate: float
    pause_count: int
    mean_pause_duration: float
    total_pause_duration: float
    jitter: float
    shimmer: float
    hnr: float
    acoustic_distress_score: float

class EmotionScore(BaseModel):
    label: EmotionLabel
    confidence: float

class VoiceAnalysisResult(BaseModel):
    transcript: str
    detected_language: str
    acoustic_features: AcousticFeatures
    emotions: List[EmotionScore]
    dominant_emotion: EmotionLabel

class TraumaKeywordMatch(BaseModel):
    keyword: str
    category: str
    severity: int = Field(ge=1, le=5)
    context_snippet: str

class TextAnalysisResult(BaseModel):
    original_text: str
    translated_text: str
    detected_language: str
    sentiment_score: float = Field(ge=-1.0, le=1.0)
    emotion_scores: List[EmotionScore]
    trauma_keywords: List[TraumaKeywordMatch]
    keyword_density_score: float = Field(ge=0.0, le=100.0)
    suicidal_ideation_flag: bool
    suicidal_ideation_confidence: float
    suicidal_ideation_matched_phrases: List[str]

class SVIComponent(BaseModel):
    name: str
    raw_score: float
    weight: float
    weighted_score: float

class SVIResult(BaseModel):
    total_score: float = Field(ge=0.0, le=100.0)
    components: List[SVIComponent]
    risk_level: RiskLevel
    auto_escalated: bool
    escalation_reason: Optional[str] = None
    timestamp: datetime

class Recommendation(BaseModel):
    intervention_type: InterventionType
    priority: int
    description: str
    action_details: str
    response_sla: str

class AssessmentResponse(BaseModel):
    case_id: UUID
    svi: SVIResult
    recommendations: List[Recommendation]
    voice_analysis: Optional[VoiceAnalysisResult] = None
    text_analysis: Optional[TextAnalysisResult] = None
    created_at: datetime

class CaseListItem(BaseModel):
    case_id: UUID
    channel: InputChannel
    risk_level: RiskLevel
    svi_score: float
    status: CaseStatus
    language: str
    created_at: datetime

class DashboardStats(BaseModel):
    total_cases_today: int
    risk_distribution: Dict[RiskLevel, int]
    pending_actions: int
    critical_alerts: int
