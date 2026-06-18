"""Prompts par tâche IA, partagés par tous les clients LLM.

Centraliser ici permet d'ajouter une tâche (summarize, keywords, qa...) sans
toucher aux clients de modèle.
"""
from __future__ import annotations

# Limite de contexte envoyée au modèle (caractères). Évite de dépasser la
# fenêtre de contexte et maîtrise le coût.
MAX_CHARS = 12_000

SYSTEM_PROMPTS: dict[str, str] = {
    "sentiment": (
        "You are a precise sentiment analysis engine. Analyse the overall "
        "sentiment of the document. Respond with STRICT JSON only, no prose, "
        'using this schema: {"label": "positive|neutral|negative", '
        '"score": <float 0..1 confidence>, "rationale": "<one short sentence>"}'
    ),
    "summarize": (
        "You are a summarisation engine. Summarise the document in 3-4 "
        'sentences. Respond with STRICT JSON only: {"summary": "<text>"}'
    ),
    "keywords": (
        "You extract keywords. Return the 5-10 most important keywords. "
        'Respond with STRICT JSON only: {"keywords": ["...", "..."]}'
    ),
    "qa": (
        "You answer questions about the document. If no question is embedded, "
        "answer: what is this document about? Respond with STRICT JSON only: "
        '{"answer": "<text>"}'
    ),
}


def build_user_prompt(text: str, task: str) -> str:
    snippet = text[:MAX_CHARS]
    return f"Document:\n\n{snippet}"


def system_prompt(task: str) -> str:
    return SYSTEM_PROMPTS.get(task, SYSTEM_PROMPTS["sentiment"])
