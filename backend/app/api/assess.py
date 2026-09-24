"""Assessment API endpoints.

Handles voice, text, and combined stress/trauma assessments.
"""
import json
import shutil
import tempfile
import uuid
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.database import get_db, Case, Assessment, InterventionRecord
from ..models.enums import CaseStatus, ConsentStatus
from ..services.voice_pipeline import VoicePipeline
from ..services.text_pipeline import TextPipeline
from ..services.svi_engine import SVIEngine
from ..services.recommender import InterventionRecommender
from ..services.risk_categorizer import RiskCategorizer
from ..utils.validators import validate_audio_file, validate_text_input
from ..utils.anonymizer import PIIAnonymizer

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assess", tags=["Assessment"])

# Shared service instances
_voice_pipeline = VoicePipeline()
_text_pipeline = TextPipeline()
_svi_engine = SVIEngine()
_recommender = InterventionRecommender()
_risk_categorizer = RiskCategorizer()
_anonymizer = PIIAnonymizer()


def _persist_assessment(db: Session, case_id: str, channel: str, language: str,
                        svi_res: dict, recs: list, voice_res: dict = None,
                        text_res: dict = None) -> None:
    """Persist case, assessment, and intervention records to the database."""
    try:
        case = Case(
            id=case_id,
            channel=channel,
            language=language,
            status=CaseStatus.ASSESSED.value,
            consent_status=ConsentStatus.GRANTED.value,
        )
        db.add(case)

        assessment = Assessment(
            id=str(uuid.uuid4()),
            case_id=case_id,
            svi_score=svi_res["total_score"],
            risk_level=svi_res["risk_level"].value if hasattr(svi_res["risk_level"], 'value') else str(svi_res["risk_level"]),
            auto_escalated=svi_res.get("auto_escalated", False),
            escalation_reason=svi_res.get("escalation_reason"),
            voice_transcript=voice_res.get("transcript") if voice_res else None,
            original_text=text_res.get("original_text") if text_res else None,
            translated_text=text_res.get("translated_text") if text_res else None,
            sentiment_score=text_res.get("sentiment") if text_res else None,
            suicidal_ideation_flag=text_res.get("suicidal_ideation", {}).get("flag", False) if text_res else False,
            suicidal_ideation_confidence=text_res.get("suicidal_ideation", {}).get("confidence", 0.0) if text_res else 0.0,
            components_json=json.dumps(svi_res.get("components", [])),
        )
        db.add(assessment)

        for rec in recs:
            intervention = InterventionRecord(
                id=str(uuid.uuid4()),
                assessment_id=assessment.id,
                intervention_type=rec.get("intervention_type", "INFORMATION"),
                priority=rec.get("priority", 99),
                description=rec.get("description", ""),
                action_details=rec.get("action_details", ""),
                response_sla=rec.get("response_sla", ""),
                status="PENDING",
            )
            db.add(intervention)

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error("Failed to persist assessment: %s", e)


@router.post("/voice")
async def assess_voice(
    audio: UploadFile = File(...),
    channel: str = Form("VOICE_CALL"),
    language: str = Form(None),
    context_data: str = Form(None),
    db: Session = Depends(get_db),
):
    """Assess a voice recording for stress and trauma indicators."""
    ctx = json.loads(context_data) if context_data else None

    # Save uploaded audio to temp file
    suffix = "." + (audio.filename.rsplit(".", 1)[-1] if "." in audio.filename else "wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(audio.file, tmp)
        tmp_path = tmp.name

    val = validate_audio_file(tmp_path)
    if not val["valid"]:
        raise HTTPException(status_code=400, detail=val["error"])

    voice_res = await _voice_pipeline.process(tmp_path, language)
    text_res = await _text_pipeline.process(voice_res["transcript"], voice_res["detected_language"])

    svi_res = _svi_engine.compute(voice_result=voice_res, text_result=text_res, context_data=ctx)
    cat = _risk_categorizer.categorize(svi_res)
    recs = _recommender.recommend(cat["risk_level"], svi_res, text_res)

    case_id = str(uuid.uuid4())
    _persist_assessment(db, case_id, channel, voice_res.get("detected_language", "en"), svi_res, recs, voice_res, text_res)

    return {
        "case_id": case_id,
        "svi": svi_res,
        "category": cat,
        "recommendations": recs,
        "voice_analysis": {k: v for k, v in voice_res.items() if k != "durations"},
        "text_analysis": {k: v for k, v in text_res.items() if k != "durations"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/text")
async def assess_text(
    request_body: dict,
    db: Session = Depends(get_db),
):
    """Assess a text narrative for stress and trauma indicators."""
    text = request_body.get("text", "")
    language = request_body.get("language")
    channel = request_body.get("channel", "PORTAL")
    ctx = request_body.get("context_data")

    val = validate_text_input(text)
    if not val["valid"]:
        raise HTTPException(status_code=400, detail=val["error"])

    # Anonymize PII before processing
    anon_result = _anonymizer.anonymize(text)
    anonymized_text = anon_result["anonymized_text"]

    text_res = await _text_pipeline.process(anonymized_text, language)

    svi_res = _svi_engine.compute(voice_result=None, text_result=text_res, context_data=ctx)
    cat = _risk_categorizer.categorize(svi_res)
    recs = _recommender.recommend(cat["risk_level"], svi_res, text_res)

    case_id = str(uuid.uuid4())
    _persist_assessment(db, case_id, channel, text_res.get("detected_language", "en"), svi_res, recs, None, text_res)

    return {
        "case_id": case_id,
        "svi": svi_res,
        "category": cat,
        "recommendations": recs,
        "text_analysis": {k: v for k, v in text_res.items() if k != "durations"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.post("/combined")
async def assess_combined(
    audio: UploadFile = File(...),
    text: str = Form(""),
    channel: str = Form("VOICE_CALL"),
    language: str = Form(None),
    context_data: str = Form(None),
    db: Session = Depends(get_db),
):
    """Combined voice + text assessment for comprehensive analysis."""
    ctx = json.loads(context_data) if context_data else None

    suffix = "." + (audio.filename.rsplit(".", 1)[-1] if "." in audio.filename else "wav")
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(audio.file, tmp)
        tmp_path = tmp.name

    voice_res = await _voice_pipeline.process(tmp_path, language)

    # Use supplementary text if provided, otherwise use transcript
    analysis_text = text if text.strip() else voice_res.get("transcript", "")
    text_res = await _text_pipeline.process(analysis_text, language or voice_res.get("detected_language"))

    svi_res = _svi_engine.compute(voice_result=voice_res, text_result=text_res, context_data=ctx)
    cat = _risk_categorizer.categorize(svi_res)
    recs = _recommender.recommend(cat["risk_level"], svi_res, text_res)

    case_id = str(uuid.uuid4())
    _persist_assessment(db, case_id, channel, voice_res.get("detected_language", "en"), svi_res, recs, voice_res, text_res)

    return {
        "case_id": case_id,
        "svi": svi_res,
        "category": cat,
        "recommendations": recs,
        "voice_analysis": {k: v for k, v in voice_res.items() if k != "durations"},
        "text_analysis": {k: v for k, v in text_res.items() if k != "durations"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{case_id}")
async def get_assessment(case_id: str, db: Session = Depends(get_db)):
    """Retrieve a completed assessment by case ID."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    assessment = db.query(Assessment).filter(Assessment.case_id == case_id).first()
    interventions = []
    if assessment:
        records = db.query(InterventionRecord).filter(InterventionRecord.assessment_id == assessment.id).all()
        interventions = [
            {
                "intervention_type": r.intervention_type,
                "priority": r.priority,
                "description": r.description,
                "action_details": r.action_details,
                "response_sla": r.response_sla,
                "status": r.status,
            }
            for r in records
        ]

    return {
        "case_id": case_id,
        "channel": case.channel,
        "language": case.language,
        "status": case.status,
        "svi_score": assessment.svi_score if assessment else None,
        "risk_level": assessment.risk_level if assessment else None,
        "auto_escalated": assessment.auto_escalated if assessment else False,
        "recommendations": interventions,
        "created_at": case.created_at.isoformat() if case.created_at else None,
    }


@router.get("/{case_id}/recommendations")
async def get_recommendations(case_id: str, db: Session = Depends(get_db)):
    """Retrieve intervention recommendations for a case."""
    assessment = db.query(Assessment).filter(Assessment.case_id == case_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    records = db.query(InterventionRecord).filter(
        InterventionRecord.assessment_id == assessment.id
    ).order_by(InterventionRecord.priority).all()

    return {
        "case_id": case_id,
        "recommendations": [
            {
                "id": r.id,
                "intervention_type": r.intervention_type,
                "priority": r.priority,
                "description": r.description,
                "action_details": r.action_details,
                "response_sla": r.response_sla,
                "status": r.status,
            }
            for r in records
        ],
    }
