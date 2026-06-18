"""Schémas Pydantic = contrat d'entrée/sortie de l'API."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from app.core.models import JobStatus


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str = "File accepted for processing"


class ResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    filename: str
    task: str
    result: dict[str, Any] | None = None
    error: str | None = None


class ErrorResponse(BaseModel):
    detail: str
