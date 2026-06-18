"""Couche API : endpoints HTTP uniquement.

Cette couche ne fait QUE :
  - valider la requête (taille / type),
  - déléguer au service,
  - renvoyer le contrat.
Aucune logique métier ni appel modèle ici.
"""
from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from app.api.schemas import ResultResponse, UploadResponse
from app.core.config import settings
from app.processing.validation import ValidationError, validate_upload
from app.services.job_service import job_service

router = APIRouter()


@router.post("/upload", response_model=UploadResponse, status_code=202)
async def upload(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """Accepte un fichier, renvoie immédiatement un job_id.

    Le traitement lourd (preprocessing + inference) part en tâche de fond :
    l'endpoint n'est jamais bloquant.
    """
    content = await file.read()
    try:
        validate_upload(file.filename, content)
    except ValidationError as exc:
        # 422 : le fichier est refusé proprement, l'API ne plante pas.
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    job = job_service.create_job(filename=file.filename, task=settings.ai_task)
    # Lancement asynchrone du pipeline après la réponse HTTP.
    background_tasks.add_task(job_service.run_pipeline, job.job_id, content)

    return UploadResponse(job_id=job.job_id, status=job.status)


@router.get("/result/{job_id}", response_model=ResultResponse)
async def get_result(job_id: str):
    """Renvoie le statut du job, et les insights IA s'il est terminé."""
    job = job_service.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="job_id not found")

    return ResultResponse(
        job_id=job.job_id,
        status=job.status,
        filename=job.filename,
        task=job.task,
        result=job.result,
        error=job.error,
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
