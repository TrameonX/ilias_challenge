from enum import Enum
from pydantic import BaseModel
from typing import Optional
from abc import ABC, abstractmethod


class JobStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PITask(str, Enum):
    SUMMARIZE = "summarize"
    KEYWORDS = "keywords"
    SENTIMENT = "sentiment"
    QA = "qa"


class UploadResponse(BaseModel):
    job_id: str
    status: JobStatus


class ResultResponse(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[dict] = None
    error: Optional[str] = None


class AbstractAIModel(ABC):
    @abstractmethod
    def run_inference(self, task: PITask, content: str, question: Optional[str] = None) -> dict:
        pass


class DummyAIModel(AbstractAIModel):
    def run_inference(self, task: PITask, content: str, question: Optional[str] = None) -> dict:
        preview = content[:30].strip().replace('\n', ' ')

        if task == PITask.SUMMARIZE:
            return {"summary": f"Résumé automatique du document (Début : '{preview}...')"}
        elif task == PITask.KEYWORDS:
            return {"keywords": ["analyse", "pipeline", "automation", "text"]}
        elif task == PITask.SENTIMENT:
            return {"sentiment": "Positif", "score": 0.92}
        elif task == PITask.QA:
            q = question or "Question non fournie"
            return {
                "question": q,
                "answer": f"Réponse simulée à '{q}' basée sur un contexte de {len(content)} caractères."
            }

        raise ValueError("Tâche non supportée par le modèle d'inférence.")