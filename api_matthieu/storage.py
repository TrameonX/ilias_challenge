from typing import Dict
from fastapi import HTTPException
from models import JobStatus, ResultResponse
import time


JOB_TTL_SECONDS = 3600


class JobRepository:
    """
    Couche Storage — requis explicitement par l'énoncé (4 couches séparées).
    En production, remplacer le dict par Redis ou SQLAlchemy ici seulement.

    FIX : Ajout d'un mécanisme de nettoyage (TTL) pour éviter la fuite mémoire.
    Les jobs COMPLETED ou FAILED sont supprimés après JOB_TTL_SECONDS secondes.
    """

    def __init__(self):
        self._store: Dict[str, ResultResponse] = {}
        self._timestamps: Dict[str, float] = {}

    def _cleanup(self):
        """Supprime les jobs terminés dont le TTL est expiré."""
        now = time.time()
        terminal_statuses = {JobStatus.COMPLETED, JobStatus.FAILED}
        expired = [
            job_id for job_id, job in self._store.items()
            if job.status in terminal_statuses
            and (now - self._timestamps.get(job_id, now)) > JOB_TTL_SECONDS
        ]
        for job_id in expired:
            del self._store[job_id]
            self._timestamps.pop(job_id, None)

    def create(self, job_id: str) -> ResultResponse:
        self._cleanup()
        job = ResultResponse(job_id=job_id, status=JobStatus.PENDING)
        self._store[job_id] = job
        self._timestamps[job_id] = time.time()
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
        self._timestamps[job_id] = time.time()

    def set_failed(self, job_id: str, error: str):
        self._store[job_id].status = JobStatus.FAILED
        self._store[job_id].error = error
        self._timestamps[job_id] = time.time()