"""Consent management API endpoints."""
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.database import get_db, Case
from ..models.enums import ConsentStatus, CaseStatus

router = APIRouter(prefix="/consent", tags=["Consent"])


@router.post("/record")
async def record_consent(request_body: dict, db: Session = Depends(get_db)):
    """Record informed consent for an assessment."""
    case_id = request_body.get("case_id") or str(uuid.uuid4())
    language = request_body.get("language", "en")
    channel = request_body.get("channel", "PORTAL")
    method = request_body.get("method", "verbal")

    # Check if case exists, create if not
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        case = Case(
            id=case_id,
            channel=channel,
            language=language,
            status=CaseStatus.NEW.value,
            consent_status=ConsentStatus.GRANTED.value,
            consent_granted_at=datetime.now(timezone.utc),
        )
        db.add(case)
    else:
        case.consent_status = ConsentStatus.GRANTED.value
        case.consent_granted_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "case_id": case.id,
        "consent_status": ConsentStatus.GRANTED.value,
        "method": method,
        "language": language,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/{case_id}")
async def get_consent(case_id: str, db: Session = Depends(get_db)):
    """Check consent status for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    return {
        "case_id": case_id,
        "consent_status": case.consent_status,
        "consent_granted_at": case.consent_granted_at.isoformat() if case.consent_granted_at else None,
    }
