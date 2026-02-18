"""
Main FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.core.config import settings
from app.api.routes import incidents, webhooks, analysis, health

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automatically diagnose and fix data pipeline failures using AI",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Log level: {settings.LOG_LEVEL}")
    
    # TODO: Initialize database connection pool
    # TODO: Initialize Redis connection
    # TODO: Verify external API credentials


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info(f"Shutting down {settings.APP_NAME}")
    # TODO: Close database connections
    # TODO: Close Redis connections


# Include routers
app.include_router(
    health.router,
    prefix=f"{settings.API_V1_PREFIX}/health",
    tags=["health"]
)

app.include_router(
    webhooks.router,
    prefix=f"{settings.API_V1_PREFIX}/webhooks",
    tags=["webhooks"]
)

app.include_router(
    incidents.router,
    prefix=f"{settings.API_V1_PREFIX}/incidents",
    tags=["incidents"]
)

app.include_router(
    analysis.router,
    prefix=f"{settings.API_V1_PREFIX}/analysis",
    tags=["analysis"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
