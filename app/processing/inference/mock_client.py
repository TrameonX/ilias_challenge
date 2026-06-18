"""Client mock : aucune dépendance réseau.

Sert de fallback (si pas de clé API) et pour les tests/démo. Implémente une
heuristique de sentiment basée sur des lexiques — suffisant pour démontrer que
le pipeline tourne de bout en bout sans clé.
"""
from __future__ import annotations

from typing import Any

from app.processing.inference.base import ModelClient

_POSITIVE = {
    "good", "great", "excellent", "happy", "love", "wonderful", "best",
    "amazing", "positive", "success", "bon", "super", "génial", "heureux",
    "aime", "excellent", "réussite",
}
_NEGATIVE = {
    "bad", "terrible", "awful", "sad", "hate", "worst", "poor", "negative",
    "fail", "problem", "mauvais", "horrible", "triste", "déteste", "échec",
    "problème", "nul",
}


class MockClient(ModelClient):
    name = "mock"
    model = "mock-lexicon-v1"

    def infer(self, text: str, task: str) -> dict[str, Any]:
        if task == "sentiment":
            return self._sentiment(text)
        # Fallback générique pour les autres tâches.
        return {"output": text[:200], "model": self.model}

    def _sentiment(self, text: str) -> dict[str, Any]:
        words = [w.strip(".,!?;:()\"'").lower() for w in text.split()]
        pos = sum(w in _POSITIVE for w in words)
        neg = sum(w in _NEGATIVE for w in words)
        total = pos + neg

        if total == 0:
            label, score = "neutral", 0.5
        elif pos > neg:
            label, score = "positive", round(pos / total, 2)
        elif neg > pos:
            label, score = "negative", round(neg / total, 2)
        else:
            label, score = "neutral", 0.5

        return {
            "label": label,
            "score": score,
            "rationale": f"Lexicon heuristic: {pos} positive / {neg} negative cues.",
            "model": self.model,
        }
