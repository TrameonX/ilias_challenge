"""Couche Storage : persistance des jobs.

Implémentation in-memory thread-safe pour le challenge. L'interface est isolée
ici : on pourrait la remplacer par Redis / une base SQL sans toucher au reste.
"""
from __future__ import annotations

import threading

from app.core.models import Job


class InMemoryJobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, Job] = {}
        self._lock = threading.Lock()

    def save(self, job: Job) -> None:
        with self._lock:
            job.touch()
            self._jobs[job.job_id] = job

    def get(self, job_id: str) -> Job | None:
        with self._lock:
            return self._jobs.get(job_id)


# Singleton de stockage de l'application.
job_store = InMemoryJobStore()
