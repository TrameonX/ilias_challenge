from enum import Enum
from pydantic import BaseModel
from typing import Optional
import requests as http
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
    

class HuggingFaceModel(AbstractAIModel):
    def __init__(self, api_key: str, model_id: str):
        self.api_key = api_key
        self.model_id = model_id
        self.base_url = f"https://api-inference.huggingface.co/models/{model_id}"
        self.headers = {"Authorization": f"Bearer {api_key}"}

    def run_inference(self, task: PITask, content: str, question: Optional[str] = None) -> dict:
        if task == PITask.SUMMARIZE:
            payload = {"inputs": content[:1024]}  # HF a une limite de tokens
            response = http.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return {"summary": response.json()[0]["summary_text"]}

        elif task == PITask.SENTIMENT:
            payload = {"inputs": content[:512]}
            response = http.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            result = response.json()[0][0]
            return {"sentiment": result["label"], "score": round(result["score"], 2)}

        elif task == PITask.QA:
            payload = {"inputs": {"question": question, "context": content[:2048]}}
            response = http.post(self.base_url, headers=self.headers, json=payload)
            response.raise_for_status()
            return {"question": question, "answer": response.json()["answer"]}

        raise ValueError(f"Tâche non supportée : {task}")