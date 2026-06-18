"""Branche la vraie IA (couche app/processing/inference de Steph) dans l'API.

Implémente l'interface AbstractAIModel de Mathieu -> la swappabilité qu'il a
prévue est respectée : on remplace juste DummyAIModel par RealAIModel.

>>> Destination : api_matthieu/ai_adapter.py
"""
import os
import sys
from typing import Optional

# Rendre le package app/ importable quel que soit le dossier de lancement.
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from models import AbstractAIModel, PITask
from app.processing.inference.factory import get_model_client


class RealAIModel(AbstractAIModel):
    def run_inference(self, task: PITask, content: str, question: Optional[str] = None) -> dict:
        client = get_model_client()            # provider via MODEL_PROVIDER (mock/anthropic/openai)
        result = client.infer(content, task.value)
        result.setdefault("provider", client.name)
        return result
