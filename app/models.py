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


class StoredDocument(BaseModel):
    """Métadonnées d'un document persisté en MongoDB."""
    document_id: str
    job_id: str
    filename: str
    content_type: str
    size_bytes: int
    gridfs_id: Optional[str] = None  # ObjectId GridFS stringifié


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


class OllamaAIModel(AbstractAIModel):
    def __init__(self, model: str = "llama3.2:latest", base_url: str = None):
        import os
        base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model
        self.base_url = base_url

    def run_inference(self, task: PITask, content: str, question: Optional[str] = None) -> dict:
        import requests

        prompts = {
            PITask.SUMMARIZE: f"Fais un résumé clair et concis du texte suivant en français :\n\n{content[:4000]}",
            PITask.KEYWORDS: f"Liste les 5 mots-clés principaux du texte suivant, séparés par des virgules, sans explication :\n\n{content[:4000]}",
            PITask.SENTIMENT: f"Analyse le sentiment général du texte suivant (Positif, Négatif ou Neutre) et donne un score de 0 à 1. Réponds uniquement avec le format : SENTIMENT|SCORE\n\n{content[:4000]}",
            PITask.QA: f"Réponds à la question suivante en te basant sur le texte fourni.\nQuestion : {question or 'Quel est le sujet principal ?'}\n\nTexte :\n{content[:4000]}",
        }

        prompt = prompts[task]
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={"model": self.model, "messages": [{"role": "user", "content": prompt}], "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        answer = response.json()["message"]["content"].strip()

        if task == PITask.SUMMARIZE:
            return {"summary": answer}
        elif task == PITask.KEYWORDS:
            keywords = [k.strip() for k in answer.split(",") if k.strip()]
            return {"keywords": keywords}
        elif task == PITask.SENTIMENT:
            parts = answer.split("|")
            sentiment = parts[0].strip() if parts else answer
            score = float(parts[1].strip()) if len(parts) > 1 else 0.5
            return {"sentiment": sentiment, "score": score}
        elif task == PITask.QA:
            return {"question": question or "Quel est le sujet principal ?", "answer": answer}

        raise ValueError("Tâche non supportée.")