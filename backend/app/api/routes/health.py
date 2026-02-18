"""
Health check endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings

router = APIRouter()


@router.get("")
async def health_check(db: Session = Depends(get_db)):
    """
    Basic health check endpoint.
    Verifies API is running and database is accessible.
    """
    try:
        # Try to execute a simple query to check database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check for Kubernetes/container orchestration.
    Verifies all dependencies are available.
    """
    checks = {
        "database": False,
        "claude_api": False,
    }
    
    # Check database
    try:
        db.execute("SELECT 1")
        checks["database"] = True
    except Exception:
        pass
    
    # Check Claude API key is configured
    if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "your_anthropic_api_key_here":
        checks["claude_api"] = True
    
    all_healthy = all(checks.values())
    
    return {
        "ready": all_healthy,
        "checks": checks
    }
