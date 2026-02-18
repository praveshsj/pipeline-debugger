"""
Webhook endpoints for receiving pipeline failure notifications.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from loguru import logger

from app.core.database import get_db
from app.models.incident import Incident
from app.services.evidence_collector import EvidenceCollectorService

router = APIRouter()


class AirflowWebhookPayload(BaseModel):
    """
    Payload received from Airflow on task failure.
    
    Example:
    {
        "dag_id": "daily_etl",
        "task_id": "load_customers",
        "execution_date": "2024-02-18T10:00:00Z",
        "log_url": "http://airflow:8080/log?dag_id=daily_etl&task_id=load_customers",
        "error_message": "SQL compilation error: column 'user_id' does not exist",
        "state": "failed"
    }
    """
    dag_id: str
    task_id: str
    execution_date: str
    log_url: str | None = None
    error_message: str | None = None
    state: str = "failed"
    airflow_base_url: str | None = None


class PrefectWebhookPayload(BaseModel):
    """
    Payload received from Prefect on flow run failure.
    """
    flow_run_id: str
    flow_name: str
    task_name: str | None = None
    state: str
    message: str | None = None
    start_time: str
    end_time: str | None = None


@router.post("/airflow/failure")
async def airflow_failure_webhook(
    payload: AirflowWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive pipeline failure notification from Airflow.
    
    This endpoint:
    1. Creates an Incident record
    2. Triggers evidence collection in the background
    3. Returns immediately (async)
    
    The actual analysis happens asynchronously via Celery tasks.
    """
    logger.info(f"Received Airflow failure webhook: {payload.dag_id}.{payload.task_id}")
    
    try:
        # Parse execution date
        execution_date = datetime.fromisoformat(
            payload.execution_date.replace('Z', '+00:00')
        )
        
        # Create incident record
        incident = Incident(
            dag_id=payload.dag_id,
            task_id=payload.task_id,
            execution_date=execution_date,
            orchestrator="airflow",
            orchestrator_url=payload.log_url,
            error_message=payload.error_message,
            status="pending",
            detected_at=datetime.utcnow()
        )
        
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        logger.info(f"Created incident {incident.id} for {payload.dag_id}.{payload.task_id}")
        
        # Trigger evidence collection in background
        # Note: In production, this would be a Celery task
        # For MVP, we'll use FastAPI BackgroundTasks
        background_tasks.add_task(
            collect_evidence_for_incident,
            incident_id=str(incident.id),
            airflow_base_url=payload.airflow_base_url
        )
        
        return {
            "success": True,
            "incident_id": str(incident.id),
            "message": "Incident created, analysis starting"
        }
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/prefect/failure")
async def prefect_failure_webhook(
    payload: PrefectWebhookPayload,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Receive pipeline failure notification from Prefect.
    """
    logger.info(f"Received Prefect failure webhook: {payload.flow_name}")
    
    try:
        # Parse timestamps
        start_time = datetime.fromisoformat(payload.start_time.replace('Z', '+00:00'))
        
        # Create incident record
        incident = Incident(
            dag_id=payload.flow_name,  # Use flow_name as dag_id
            task_id=payload.task_name or "flow_run",
            execution_date=start_time,
            orchestrator="prefect",
            orchestrator_url=f"prefect://flow-run/{payload.flow_run_id}",
            error_message=payload.message,
            status="pending",
            detected_at=datetime.utcnow(),
            metadata_json={"flow_run_id": payload.flow_run_id}
        )
        
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        logger.info(f"Created incident {incident.id} for Prefect flow {payload.flow_name}")
        
        # Trigger evidence collection
        background_tasks.add_task(
            collect_evidence_for_incident,
            incident_id=str(incident.id)
        )
        
        return {
            "success": True,
            "incident_id": str(incident.id),
            "message": "Incident created, analysis starting"
        }
        
    except Exception as e:
        logger.error(f"Error processing Prefect webhook: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def collect_evidence_for_incident(incident_id: str, airflow_base_url: str | None = None):
    """
    Background task to collect evidence for an incident.
    
    This will eventually be a Celery task, but for MVP we use BackgroundTasks.
    
    Steps:
    1. Fetch logs from orchestrator
    2. Get recent git commits
    3. Check schema changes
    4. Query upstream task status
    5. Search for similar past incidents
    """
    logger.info(f"Starting evidence collection for incident {incident_id}")
    
    # TODO: Implement EvidenceCollectorService
    # collector = EvidenceCollectorService()
    # await collector.collect_all_evidence(incident_id, airflow_base_url)
    
    # For now, just log
    logger.info(f"Evidence collection completed for incident {incident_id}")
