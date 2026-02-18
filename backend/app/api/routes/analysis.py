"""
API routes for triggering and managing AI analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.models.incident import Incident

router = APIRouter()


class AnalyzeRequest(BaseModel):
    """Request to analyze an incident."""
    incident_id: str
    force_reanalysis: bool = False  # Re-analyze even if already analyzed


class AnalyzeResponse(BaseModel):
    """Response from analysis trigger."""
    success: bool
    incident_id: str
    message: str
    status: str


@router.post("/analyze", response_model=AnalyzeResponse)
async def trigger_analysis(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Trigger AI analysis for an incident.
    
    This endpoint:
    1. Verifies incident exists and has evidence
    2. Triggers Claude API analysis in background
    3. Updates incident with root cause and fixes
    
    Can be called manually or automatically after evidence collection.
    """
    logger.info(f"Analysis requested for incident {request.incident_id}")
    
    # Get incident
    incident = db.query(Incident).filter(Incident.id == request.incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Check if already analyzed
    if incident.status == "analyzed" and not request.force_reanalysis:
        return AnalyzeResponse(
            success=False,
            incident_id=request.incident_id,
            message="Incident already analyzed. Use force_reanalysis=true to re-analyze.",
            status=incident.status
        )
    
    # Check if evidence exists
    if not incident.evidence:
        raise HTTPException(
            status_code=400,
            detail="No evidence collected yet. Wait for evidence collection to complete."
        )
    
    # Update status
    incident.status = "analyzing"
    db.commit()
    
    # Trigger analysis in background
    background_tasks.add_task(
        run_claude_analysis,
        incident_id=request.incident_id
    )
    
    return AnalyzeResponse(
        success=True,
        incident_id=request.incident_id,
        message="Analysis started",
        status="analyzing"
    )


async def run_claude_analysis(incident_id: str):
    """
    Background task to run Claude API analysis.
    
    This will:
    1. Format all evidence for Claude
    2. Call Claude API with specialized prompts
    3. Parse response for root cause + fixes
    4. Update incident record
    5. Create Fix records
    
    TODO: Implement using ClaudeAnalysisService
    """
    logger.info(f"Starting Claude analysis for incident {incident_id}")
    
    # TODO: Implement actual Claude integration
    # from app.services.claude_analysis import ClaudeAnalysisService
    # service = ClaudeAnalysisService()
    # await service.analyze_incident(incident_id)
    
    logger.info(f"Claude analysis completed for incident {incident_id}")


@router.post("/generate-fix", response_model=dict)
async def generate_fix(
    incident_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Generate a fix for an analyzed incident.
    
    This can be called after analysis to generate additional fix strategies,
    or to regenerate fixes if the first one didn't work.
    """
    logger.info(f"Fix generation requested for incident {incident_id}")
    
    # Get incident
    incident = db.query(Incident).filter(Incident.id == incident_id).first()
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if incident.status not in ["analyzed", "fixing", "fixed"]:
        raise HTTPException(
            status_code=400,
            detail="Incident must be analyzed before generating fixes"
        )
    
    # Update status
    incident.status = "fixing"
    db.commit()
    
    # Trigger fix generation
    background_tasks.add_task(
        generate_fix_for_incident,
        incident_id=incident_id
    )
    
    return {
        "success": True,
        "incident_id": incident_id,
        "message": "Fix generation started"
    }


async def generate_fix_for_incident(incident_id: str):
    """
    Background task to generate fixes using Claude.
    
    TODO: Implement using FixGeneratorService
    """
    logger.info(f"Generating fix for incident {incident_id}")
    
    # TODO: Implement
    # from app.services.fix_generator import FixGeneratorService
    # service = FixGeneratorService()
    # await service.generate_fixes(incident_id)
    
    logger.info(f"Fix generation completed for incident {incident_id}")
