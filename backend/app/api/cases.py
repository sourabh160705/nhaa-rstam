"""Case management API endpoints."""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.database import get_db, Case, Assessment
from ..models.enums import RiskLevel, CaseStatus

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.get("/")
async def list_cases(
    risk_level: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    channel: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List cases with optional filters and pagination."""
    query = db.query(Case).order_by(desc(Case.created_at))

    if status:
        query = query.filter(Case.status == status)
    if channel:
        query = query.filter(Case.channel == channel)

    total = query.count()
    cases = query.offset((page - 1) * size).limit(size).all()

    items = []
    for case in cases:
        assessment = db.query(Assessment).filter(Assessment.case_id == case.id).first()
        item = {
            "case_id": case.id,
            "channel": case.channel,
            "language": case.language,
            "status": case.status,
            "risk_level": assessment.risk_level if assessment else None,
            "svi_score": assessment.svi_score if assessment else None,
            "created_at": case.created_at.isoformat() if case.created_at else None,
        }
        # Apply risk_level filter post-join
        if risk_level and assessment and assessment.risk_level != risk_level:
            continue
        items.append(item)

    return {"items": items, "total": total, "page": page, "size": size}


@router.get("/{case_id}")
async def get_case(case_id: str, db: Session = Depends(get_db)):
    """Get full case details including assessment and interventions."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    assessment = db.query(Assessment).filter(Assessment.case_id == case_id).first()

    return {
        "case_id": case.id,
        "channel": case.channel,
        "language": case.language,
        "status": case.status,
        "consent_status": case.consent_status,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "assessment": {
            "svi_score": assessment.svi_score,
            "risk_level": assessment.risk_level,
            "auto_escalated": assessment.auto_escalated,
            "sentiment_score": assessment.sentiment_score,
            "suicidal_ideation_flag": assessment.suicidal_ideation_flag,
        } if assessment else None,
    }


@router.patch("/{case_id}/status")
async def update_case_status(case_id: str, body: dict, db: Session = Depends(get_db)):
    """Update a case's status."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    new_status = body.get("status")
    if new_status:
        case.status = new_status
        db.commit()

    return {"case_id": case_id, "status": case.status, "updated": True}
