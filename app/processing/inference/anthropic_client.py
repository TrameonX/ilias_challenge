"""Client d'inférence Anthropic (Claude)."""
from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.processing.inference.base import InferenceError, ModelClient
from app.processing.inference.prompts import build_user_prompt, system_prompt


class AnthropicClient(ModelClient):
    name = "anthropic"

    def __init__(self, model: str | None = None, api_key: str | None = None) -> None:
        self.model = model or settings.model_name
        self._api_key = api_key or settings.anthropic_api_key
        if not self._api_key:
            raise InferenceError("ANTHROPIC_API_KEY is not set")
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise InferenceError(
                "anthropic package not installed (pip install anthropic)"
            ) from exc
        self._client = anthropic.Anthropic(api_key=self._api_key)

    def infer(self, text: str, task: str) -> dict[str, Any]:
        try:
            message = self._client.messages.create(
                model=self.model,
                max_tokens=512,
                system=system_prompt(task),
                messages=[{"role": "user", "content": build_user_prompt(text, task)}],
            )
            raw = message.content[0].text
        except Exception as exc:  # erreurs réseau / API
            raise InferenceError(f"Anthropic inference failed: {exc}") from exc

        return _parse_json(raw, self.model)


def _parse_json(raw: str, model: str) -> dict[str, Any]:
    """Parse la réponse JSON du modèle de façon tolérante."""
    raw = raw.strip()
    # Retire d'éventuels fences ```json ... ```
    if raw.startswith("```"):
        raw = raw.split("```", 2)[1].lstrip("json").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InferenceError(f"Model returned non-JSON output: {raw[:200]}") from exc
    data["model"] = model
    return data
