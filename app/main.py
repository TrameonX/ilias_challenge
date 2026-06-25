"""Point d'entrée FastAPI.

Lancement : uvicorn app.main:app --reload
"""
from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings

app = FastAPI(
    title="AI File Processing Pipeline",
    description="Upload -> Validation -> Preprocessing -> Inference -> Storage -> Result",
    version="1.0.0",
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "AI File Processing Pipeline",
        "task": settings.ai_task,
        "model_provider": settings.model_provider,
        "endpoints": ["POST /upload", "GET /result/{job_id}", "GET /health"],
    }
