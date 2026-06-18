"""Client d'inférence OpenAI — montre que le modèle est swappable.

Même interface que AnthropicClient : on change de provider via MODEL_PROVIDER.
"""
from __future__ import annotations

from typing import Any

from app.core.config import settings
from app.processing.inference.anthropic_client import _parse_json
from app.processing.inference.base import InferenceError, ModelClient
from app.processing.inference.prompts import build_user_prompt, system_prompt


class OpenAIClient(ModelClient):
    name = "openai"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or "gpt-4o-mini"
        self._api_key = api_key or settings.openai_api_key
        if not self._api_key:
            raise InferenceError("OPENAI_API_KEY is not set")
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover
            raise InferenceError(
                "openai package not installed (pip install openai)"
            ) from exc
        self._client = OpenAI(api_key=self._api_key)

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
            raise InferenceError(f"OpenAI inference failed: {exc}") from exc

        return _parse_json(raw, self.model)
