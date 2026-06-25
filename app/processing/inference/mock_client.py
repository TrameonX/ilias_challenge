"""Client mock : aucune dépendance réseau.

Sert de fallback (si pas de clé API) et pour les tests/démo. Implémente une
heuristique de sentiment basée sur des lexiques — suffisant pour démontrer que
le pipeline tourne de bout en bout sans clé.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.processing.inference.base import ModelClient

# Mots vides ignorés pour l'extraction de mots-clés (FR + EN, minimal).
_STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "is",
    "are", "was", "were", "be", "with", "as", "at", "by", "it", "this", "that",
    "le", "la", "les", "un", "une", "des", "de", "du", "et", "ou", "à", "au",
    "aux", "en", "dans", "sur", "pour", "est", "sont", "ce", "cette", "ces",
    "qui", "que", "se", "ne", "pas", "plus", "avec", "son", "sa", "ses",
}

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
        if task == "keywords":
            return self._keywords(text)
        # Fallback générique pour les autres tâches.
        return {"output": text[:200], "model": self.model}

    def _keywords(self, text: str) -> dict[str, Any]:
        tokens = re.findall(r"[A-Za-zÀ-ÿ]{4,}", text.lower())
        meaningful = [t for t in tokens if t not in _STOPWORDS]
        top = [w for w, _ in Counter(meaningful).most_common(8)]
        return {"keywords": top, "model": self.model}

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
