"""Démo de la couche IA en isolation (sans lancer l'API ni Gradio).

Pratique pour bosser/démontrer ta partie IA indépendamment du reste.

Exemples :
    python -m scripts.try_inference "Ce produit est génial, je l'adore !"
    python -m scripts.try_inference --task keywords --provider mock fichier.txt
    MODEL_PROVIDER=anthropic python -m scripts.try_inference "..."   # vrai modèle
"""
from __future__ import annotations

import argparse
import json
import os
import sys

from app.processing.inference.factory import get_model_client


def main() -> int:
    parser = argparse.ArgumentParser(description="Test de la couche d'inférence IA")
    parser.add_argument("text", help="Texte à analyser, ou chemin d'un fichier .txt")
    parser.add_argument("--task", default=os.getenv("AI_TASK", "sentiment"),
                        choices=["sentiment", "keywords", "summarize", "qa"])
    parser.add_argument("--provider", default=None,
                        help="anthropic | openai | mock (sinon MODEL_PROVIDER)")
    args = parser.parse_args()

    # Si l'argument est un fichier existant, on lit son contenu.
    text = args.text
    if os.path.isfile(text):
        with open(text, encoding="utf-8", errors="ignore") as fh:
            text = fh.read()

    client = get_model_client(args.provider)
    print(f"→ provider={client.name} | task={args.task}\n")
    result = client.infer(text, args.task)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
