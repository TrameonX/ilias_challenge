from typing import Dict
from fastapi import HTTPException
from API.models import JobStatus, ResultResponse


class JobRepository:
    """
    Couche Storage — requis explicitement par l'énoncé (4 couches séparées).
    En production, remplacer le dict par Redis ou SQLAlchemy ici seulement.
    """

    def __init__(self):
        self._store: Dict[str, ResultResponse] = {}

    def create(self, job_id: str) -> ResultResponse:
        job = ResultResponse(job_id=job_id, status=JobStatus.PENDING)
        self._store[job_id] = job
        return job

    def get(self, job_id: str) -> ResultResponse:
        if job_id not in self._store:
            raise HTTPException(status_code=404, detail="Identifiant de tâche introuvable.")
        return self._store[job_id]

    def set_running(self, job_id: str):
        self._store[job_id].status = JobStatus.RUNNING

    def set_completed(self, job_id: str, result: dict):
        self._store[job_id].status = JobStatus.COMPLETED
        self._store[job_id].result = result

    def set_failed(self, job_id: str, error: str):
        self._store[job_id].status = JobStatus.FAILED
        self._store[job_id].error = error
