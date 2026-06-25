"""Configuration centrale de l'application.

Toute la configuration passe par des variables d'environnement, ce qui rend
le modèle / les limites swappables sans toucher au code.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # --- Validation des fichiers ---
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    allowed_extensions: tuple[str, ...] = ("txt", "pdf")

    # --- Choix du modèle (swappabilité) ---
    # Valeurs possibles : "anthropic", "openai", "mock"
    model_provider: str = os.getenv("MODEL_PROVIDER", "anthropic")
    model_name: str = os.getenv("MODEL_NAME", "claude-haiku-4-5-20251001")

    # --- Tâche IA par défaut ---
    # "sentiment" | "summarize" | "keywords" | "qa"
    ai_task: str = os.getenv("AI_TASK", "sentiment")

    # --- Clés API ---
    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    groq_api_key: str | None = os.getenv("GROQ_API_KEY")

    @property
    def max_file_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024


settings = Settings()
