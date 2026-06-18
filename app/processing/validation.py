"""Validation du fichier uploadé : type et taille."""
from __future__ import annotations

from app.core.config import settings


class ValidationError(Exception):
    """Erreur de validation (fichier refusé), gérée proprement par l'API."""


def _extension(filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def validate_upload(filename: str | None, content: bytes) -> None:
    if not filename:
        raise ValidationError("Missing filename")

    ext = _extension(filename)
    if ext not in settings.allowed_extensions:
        raise ValidationError(
            f"Unsupported file type '.{ext}'. Allowed: "
            f"{', '.join(settings.allowed_extensions)}"
        )

    if len(content) == 0:
        raise ValidationError("Empty file")

    if len(content) > settings.max_file_size_bytes:
        raise ValidationError(
            f"File too large ({len(content) / 1024 / 1024:.1f} MB). "
            f"Max: {settings.max_file_size_mb} MB"
        )
