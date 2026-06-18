"""Preprocessing : extraction du texte brut depuis TXT ou PDF.

Renvoie un texte nettoyé, prêt pour l'inférence. Lève PreprocessingError si le
fichier est corrompu (capté plus haut pour passer le job en FAILED).
"""
from __future__ import annotations

import io


class PreprocessingError(Exception):
    """Fichier illisible / corrompu."""


def _clean(text: str) -> str:
    # Normalisation simple des espaces et lignes vides.
    lines = [ln.strip() for ln in text.splitlines()]
    return "\n".join(ln for ln in lines if ln).strip()


def _extract_txt(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise PreprocessingError("Could not decode TXT file")


def _extract_pdf(content: bytes) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # pragma: no cover
        raise PreprocessingError(
            "pypdf is required to read PDF files (pip install pypdf)"
        ) from exc

    try:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:  # corrupted PDF
        raise PreprocessingError(f"Corrupted or unreadable PDF: {exc}") from exc

    return "\n".join(pages)


def preprocess(filename: str, content: bytes) -> str:
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if ext == "txt":
        text = _extract_txt(content)
    elif ext == "pdf":
        text = _extract_pdf(content)
    else:  # défensif : ne devrait jamais arriver après validation
        raise PreprocessingError(f"Unsupported extension: {ext}")

    cleaned = _clean(text)
    if not cleaned:
        raise PreprocessingError("No extractable text found in file")
    return cleaned
