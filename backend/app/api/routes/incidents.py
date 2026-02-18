"""
API routes for viewing and managing incidents.
"""

from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.models.incident import Incident, Evidence, Fix

router = APIRouter()


class IncidentResponse(BaseModel):
    """Response model for incident details."""
    id: str
    dag_id: str
    task_id: str
    execution_date: datetime
    orchestrator: str
    error_message: Optional[str]
    status: str
    root_cause: Optional[str]
    root_cause_confidence: Optional[float]
    detected_at: datetime
    analyzed_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class IncidentListResponse(BaseModel):
    """Response model for incident list."""
    total: int
    incidents: List[IncidentResponse]
    page: int
    page_size: int


class EvidenceResponse(BaseModel):
    """Response model for evidence."""
    id: str
    evidence_type: str
    content: Optional[str]
    source: Optional[str]
    relevance_score: Optional[float]
    collected_at: datetime
    
    class Config:
        from_attributes = True


class FixResponse(BaseModel):
    """Response model for fixes."""
    id: str
    fix_type: str
    description: Optional[str]
    code_patch: Optional[str]
    status: str
    confidence_score: Optional[float]
    github_pr_url: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    dag_id: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    List incidents with pagination and filtering.
    
    Query parameters:
    - page: Page number (default: 1)
    - page_size: Items per page (default: 20, max: 100)
    - status: Filter by status (pending, analyzing, analyzed, fixing, fixed, failed)
    - dag_id: Filter by DAG ID
    - days: Show incidents from last N days (default: 7)
    """
    # Build query
    query = db.query(Incident)
    
    # Apply filters
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    query = query.filter(Incident.detected_at >= cutoff_date)
    
    if status:
        query = query.filter(Incident.status == status)
    
    if dag_id:
        query = query.filter(Incident.dag_id == dag_id)
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    incidents = query.order_by(desc(Incident.detected_at)).offset(offset).limit(page_size).all()
    
    return IncidentListResponse(
        total=total,
        incidents=[IncidentResponse.from_orm(i) for i in incidents],
        page=page,
        page_size=page_size
    )


@router.get("/{incident_id}", response_model=IncidentResponse)
async def get_incident(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific incident.
    """
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    return IncidentResponse.from_orm(incident)


@router.get("/{incident_id}/evidence", response_model=List[EvidenceResponse])
async def get_incident_evidence(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all evidence collected for an incident.
    """
    # Verify incident exists
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get evidence
    evidence = db.query(Evidence).filter(
        Evidence.incident_id == incident_id
    ).order_by(desc(Evidence.relevance_score), Evidence.collected_at).all()
    
    return [EvidenceResponse.from_orm(e) for e in evidence]


@router.get("/{incident_id}/fixes", response_model=List[FixResponse])
async def get_incident_fixes(
    incident_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all proposed/applied fixes for an incident.
    """
    # Verify incident exists
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Get fixes
    fixes = db.query(Fix).filter(
        Fix.incident_id == incident_id
    ).order_by(Fix.priority, desc(Fix.confidence_score)).all()
    
    return [FixResponse.from_orm(f) for f in fixes]


@router.get("/stats/summary")
async def get_stats_summary(
    days: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """
    Get summary statistics for incidents.
    
    Returns:
    - Total incidents in period
    - Breakdown by status
    - Average resolution time
    - Most common failure types
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    
    # Total incidents
    total = db.query(Incident).filter(Incident.detected_at >= cutoff_date).count()
    
    # By status
    from sqlalchemy import func
    status_counts = db.query(
        Incident.status,
        func.count(Incident.id)
    ).filter(
        Incident.detected_at >= cutoff_date
    ).group_by(Incident.status).all()
    
    # Average resolution time (for resolved incidents)
    resolved = db.query(Incident).filter(
        Incident.detected_at >= cutoff_date,
        Incident.resolved_at.isnot(None)
    ).all()
    
    if resolved:
        resolution_times = [
            (inc.resolved_at - inc.detected_at).total_seconds() / 60
            for inc in resolved
        ]
        avg_resolution_minutes = sum(resolution_times) / len(resolution_times)
    else:
        avg_resolution_minutes = None
    
    # Top failing DAGs
    top_dags = db.query(
        Incident.dag_id,
        func.count(Incident.id).label('count')
    ).filter(
        Incident.detected_at >= cutoff_date
    ).group_by(Incident.dag_id).order_by(desc('count')).limit(10).all()
    
    return {
        "period_days": days,
        "total_incidents": total,
        "by_status": {status: count for status, count in status_counts},
        "avg_resolution_minutes": avg_resolution_minutes,
        "top_failing_dags": [{"dag_id": dag, "count": count} for dag, count in top_dags]
    }
