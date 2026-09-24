"""RSTAM - Real-Time Stress and Trauma Assessment Module.

FastAPI application entry point for India's National Helpline Against Atrocities (NHAA 14566).
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .models.database import init_db
from .api.assess import router as assess_router
from .api.consent import router as consent_router
from .api.cases import router as cases_router
from .api.dashboard import router as dashboard_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting RSTAM application...")
    init_db(settings.DATABASE_URL)
    logger.info("Database initialized.")
    yield
    logger.info("Shutting down RSTAM application.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description=(
        "Real-Time Stress and Trauma Assessment Module (RSTAM) "
        "for India's National Helpline Against Atrocities (NHAA 14566). "
        "Analyzes voice and text interactions to assess psychological distress "
        "and recommend interventions."
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(assess_router, prefix="/api/v1")
app.include_router(consent_router, prefix="/api/v1")
app.include_router(cases_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint returning application info."""
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "operational",
        "description": "NHAA 14566 Real-Time Stress and Trauma Assessment Module",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "version": settings.VERSION}
