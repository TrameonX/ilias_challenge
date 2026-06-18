"""Client d'inférence Groq — option GRATUITE (sans carte bancaire).

Groq expose une API compatible OpenAI : on réutilise donc le SDK `openai` avec
une base_url différente. Démontre encore la swappabilité : même interface, juste
un provider en plus.

Clé gratuite : https://console.groq.com  (variable GROQ_API_KEY)
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.processing.inference.anthropic_client import _parse_json
from app.processing.inference.base import InferenceError, ModelClient
from app.processing.inference.prompts import build_user_prompt, system_prompt

GROQ_BASE_URL = "https://api.groq.com/openai/v1"


class GroqClient(ModelClient):
    name = "groq"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        # Modèle open-source rapide, dispo sur le tier gratuit de Groq.
        self.model = model or "llama-3.3-70b-versatile"
        self._api_key = api_key or settings.groq_api_key
        if not self._api_key:
            raise InferenceError("GROQ_API_KEY is not set")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise InferenceError(
                "openai package required for Groq (pip install openai)"
            ) from exc
        self._client = OpenAI(api_key=self._api_key, base_url=GROQ_BASE_URL)

    def infer(self, text: str, task: str) -> dict[str, Any]:
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                max_tokens=512,
                messages=[
                    {"role": "system", "content": system_prompt(task)},
                    {"role": "user", "content": build_user_prompt(text, task)},
                ],
            )
            raw = resp.choices[0].message.content or ""
        except Exception as exc:
            raise InferenceError(f"Groq inference failed: {exc}") from exc

        return _parse_json(raw, self.model)
