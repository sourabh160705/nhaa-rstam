"""Enums used across the RSTAM application."""
from enum import Enum


class RiskLevel(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class InputChannel(str, Enum):
    VOICE_CALL = "VOICE_CALL"
    PORTAL = "PORTAL"
    CHATBOT = "CHATBOT"
    IVRS = "IVRS"
    MOBILE_APP = "MOBILE_APP"
    OTHER = "OTHER"


class Language(str, Enum):
    EN = "EN"
    HI = "HI"
    TA = "TA"
    TE = "TE"
    MR = "MR"
    BN = "BN"
    KN = "KN"
    GU = "GU"
    ML = "ML"
    PA = "PA"
    OR = "OR"
    UR = "UR"


class ConsentStatus(str, Enum):
    PENDING = "PENDING"
    GRANTED = "GRANTED"
    WITHDRAWN = "WITHDRAWN"


class CaseStatus(str, Enum):
    NEW = "NEW"
    ASSESSING = "ASSESSING"
    ASSESSED = "ASSESSED"
    REFERRED = "REFERRED"
    CLOSED = "CLOSED"


class EmotionLabel(str, Enum):
    NEUTRAL = "NEUTRAL"
    HAPPY = "HAPPY"
    SAD = "SAD"
    ANGRY = "ANGRY"
    FEARFUL = "FEARFUL"
    DISGUSTED = "DISGUSTED"
    SURPRISED = "SURPRISED"


class InterventionType(str, Enum):
    """Types of interventions that can be recommended."""
    COUNSELLING = "COUNSELLING"
    LEGAL_AID = "LEGAL_AID"
    LEGAL = "LEGAL"
    MEDICAL_ASSISTANCE = "MEDICAL_ASSISTANCE"
    MEDICAL = "MEDICAL"
    POLICE_INTERVENTION = "POLICE_INTERVENTION"
    POLICE = "POLICE"
    WITNESS_PROTECTION = "WITNESS_PROTECTION"
    PROTECTION = "PROTECTION"
    EMERGENCY_SUPPORT = "EMERGENCY_SUPPORT"
    REHABILITATION = "REHABILITATION"
    INFORMATION = "INFORMATION"
    FOLLOW_UP = "FOLLOW_UP"
    FOLLOWUP = "FOLLOWUP"
    ADMINISTRATION = "ADMINISTRATION"
    CRISIS = "CRISIS"
