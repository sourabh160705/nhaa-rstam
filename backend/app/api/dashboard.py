"""Dashboard API endpoints."""
from datetime import datetime, timedelta, timezone
from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..models.database import get_db, Case, Assessment, InterventionRecord
from ..models.enums import RiskLevel

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """Dashboard summary statistics."""
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    total_today = db.query(Case).filter(Case.created_at >= today_start).count()

    assessments_today = db.query(Assessment).filter(Assessment.created_at >= today_start).all()
    risk_dist = Counter(a.risk_level for a in assessments_today)

    pending = db.query(InterventionRecord).filter(InterventionRecord.status == "PENDING").count()
    critical = db.query(Assessment).filter(
        Assessment.risk_level == RiskLevel.CRITICAL.value,
        Assessment.created_at >= today_start,
    ).count()

    return {
        "total_cases_today": total_today,
        "risk_distribution": {
            "CRITICAL": risk_dist.get(RiskLevel.CRITICAL.value, 0),
            "HIGH": risk_dist.get(RiskLevel.HIGH.value, 0),
            "MODERATE": risk_dist.get(RiskLevel.MODERATE.value, 0),
            "LOW": risk_dist.get(RiskLevel.LOW.value, 0),
        },
        "pending_actions": pending,
        "critical_alerts": critical,
    }


@router.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    """Critical and high-risk cases from the last 24 hours."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)

    alerts = (
        db.query(Assessment)
        .filter(
            Assessment.risk_level.in_([RiskLevel.CRITICAL.value, RiskLevel.HIGH.value]),
            Assessment.created_at >= since,
        )
        .order_by(Assessment.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "case_id": a.case_id,
            "svi_score": a.svi_score,
            "risk_level": a.risk_level,
            "auto_escalated": a.auto_escalated,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]


@router.get("/trends")
async def get_trends(db: Session = Depends(get_db)):
    """Daily risk distribution for the last 30 days."""
    since = datetime.now(timezone.utc) - timedelta(days=30)
    assessments = db.query(Assessment).filter(Assessment.created_at >= since).all()

    daily = {}
    for a in assessments:
        day = a.created_at.strftime("%Y-%m-%d") if a.created_at else "unknown"
        if day not in daily:
            daily[day] = {"date": day, "LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0, "total": 0}
        daily[day][a.risk_level] = daily[day].get(a.risk_level, 0) + 1
        daily[day]["total"] += 1

    return sorted(daily.values(), key=lambda x: x["date"])
