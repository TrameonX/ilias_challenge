"""Factory : sélectionne le client de modèle selon la config.

C'est le SEUL endroit à modifier pour ajouter/changer un provider.
Si le provider configuré échoue à s'initialiser (ex. clé manquante), on
bascule sur le mock pour que la démo ne soit jamais bloquée.
"""
from __future__ import annotations

from app.core.config import settings
from app.processing.inference.base import InferenceError, ModelClient
from app.processing.inference.mock_client import MockClient

_REGISTRY = {
    "anthropic": "app.processing.inference.anthropic_client.AnthropicClient",
    "openai": "app.processing.inference.openai_client.OpenAIClient",
    "mock": "app.processing.inference.mock_client.MockClient",
}


def _import(path: str):
    module_path, cls_name = path.rsplit(".", 1)
    module = __import__(module_path, fromlist=[cls_name])
    return getattr(module, cls_name)


def get_model_client(provider: str | None = None) -> ModelClient:
    provider = (provider or settings.model_provider).lower()
    target = _REGISTRY.get(provider)
    if target is None:
        raise InferenceError(f"Unknown MODEL_PROVIDER '{provider}'")

    try:
        return _import(target)()
    except InferenceError as exc:
        # Fallback robuste : on ne bloque jamais le pipeline.
        if provider != "mock":
            print(f"[factory] {provider} unavailable ({exc}); falling back to mock.")
            return MockClient()
        raise
