"""Contrat d'inférence = clé de la swappabilité du modèle.

Tout client de modèle implémente `ModelClient.infer(text, task)`.
Changer de modèle = écrire une nouvelle classe + une ligne dans la factory.
Le reste du pipeline ne connaît QUE cette interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class InferenceError(Exception):
    """Échec d'inférence (réseau, API, parsing...). Capté pour passer en FAILED."""


class ModelClient(ABC):
    """Interface abstraite pour n'importe quel moteur d'inférence."""

    name: str = "abstract"

    @abstractmethod
    def infer(self, text: str, task: str) -> dict[str, Any]:
        """Exécute la tâche IA sur `text` et renvoie un dict d'insights.

        Pour la tâche 'sentiment', le format attendu est :
            {"label": "positive|neutral|negative",
             "score": 0.0-1.0,
             "rationale": "...",
             "model": "<nom du modèle>"}
        """
        raise NotImplementedError
