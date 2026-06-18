"""Couche Service : orchestration du pipeline.

C'est le chef d'orchestre entre l'API, le Processing et le Storage :
  Upload -> Validation -> Preprocessing -> Inference -> Storage -> Result

L'API appelle `create_job` (instantané) puis `run_pipeline` en tâche de fond.
Toute exception est capturée ici : un fichier corrompu ou un échec d'inférence
fait passer le job en FAILED, mais ne fait JAMAIS planter l'API.
"""
from __future__ import annotations

from app.core.models import Job, JobStatus
from app.processing.inference.base import InferenceError
from app.processing.inference.factory import get_model_client
from app.processing.preprocessing import PreprocessingError, preprocess
from app.storage.job_store import job_store


class JobService:
    def create_job(self, filename: str, task: str) -> Job:
        job = Job(filename=filename, task=task, status=JobStatus.PENDING)
        job_store.save(job)
        return job

    def get_job(self, job_id: str) -> Job | None:
        return job_store.get(job_id)

    def run_pipeline(self, job_id: str, content: bytes) -> None:
        """Exécute le pipeline complet pour un job (appelé en background)."""
        job = job_store.get(job_id)
        if job is None:
            return

        job.status = JobStatus.RUNNING
        job_store.save(job)

        try:
            # 1) Preprocessing -> texte
            text = preprocess(job.filename, content)

            # 2) Inference (modèle swappable via la factory)
            client = get_model_client()
            result = client.infer(text, job.task)
            result.setdefault("provider", client.name)

            # 3) Storage du résultat
            job.result = result
            job.status = JobStatus.COMPLETED

        except (PreprocessingError, InferenceError) as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
        except Exception as exc:  # filet de sécurité ultime
            job.status = JobStatus.FAILED
            job.error = f"Unexpected error: {exc}"
        finally:
            job_store.save(job)


# Singleton de service.
job_service = JobService()
