"""Frontend Gradio.

IMPORTANT (contrainte du challenge) : l'UI ne fait AUCUN appel direct au modèle.
Elle parle uniquement au backend FastAPI via HTTP :
  - POST /upload pour envoyer le fichier,
  - GET  /result/{job_id} en polling toutes les 2 secondes.

Lancement : python -m ui.gradio_app   (backend doit tourner en parallèle)
"""
from __future__ import annotations

import json
import os
import time

import gradio as gr
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")
POLL_INTERVAL_S = 2
POLL_TIMEOUT_S = 120


def process_file(file_path: str):
    """Upload puis polling jusqu'au résultat. `yield` met l'UI à jour en direct."""
    if not file_path:
        yield "Aucun fichier sélectionné.", {}
        return

    # 1) Upload -> job_id immédiat
    try:
        with open(file_path, "rb") as fh:
            resp = requests.post(f"{API_URL}/upload", files={"file": (os.path.basename(file_path), fh)})
    except requests.RequestException as exc:
        yield f"❌ Impossible de joindre l'API : {exc}", {}
        return

    if resp.status_code != 202:
        detail = _safe_detail(resp)
        yield f"❌ Upload refusé ({resp.status_code}) : {detail}", {}
        return

    job_id = resp.json()["job_id"]
    yield f"⏳ Job `{job_id}` accepté. Traitement en cours...", {}

    # 2) Polling toutes les 2 s
    deadline = time.time() + POLL_TIMEOUT_S
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL_S)
        try:
            r = requests.get(f"{API_URL}/result/{job_id}")
        except requests.RequestException as exc:
            yield f"❌ Erreur réseau pendant le polling : {exc}", {}
            return

        data = r.json()
        status = data.get("status")

        if status in ("PENDING", "RUNNING"):
            yield f"⏳ Statut : **{status}**...", {}
            continue
        if status == "COMPLETED":
            yield "✅ Statut : **COMPLETED**", data.get("result") or {}
            return
        if status == "FAILED":
            yield f"❌ Statut : **FAILED** — {data.get('error')}", {}
            return

    yield "⌛ Timeout : le traitement a pris trop de temps.", {}


def _safe_detail(resp) -> str:
    try:
        return resp.json().get("detail", resp.text)
    except json.JSONDecodeError:
        return resp.text


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="AI File Processing Pipeline") as demo:
        gr.Markdown(
            "# 🧠 AI File Processing Pipeline\n"
            "Uploade un fichier **TXT ou PDF** (max 5 MB). "
            "Le backend valide, prétraite, lance l'inférence IA, puis renvoie le résultat."
        )
        with gr.Row():
            file_in = gr.File(label="Fichier (TXT / PDF)", type="filepath")
        run_btn = gr.Button("Lancer le traitement", variant="primary")
        status_out = gr.Markdown(label="Statut")
        result_out = gr.JSON(label="Résultat IA")

        run_btn.click(process_file, inputs=file_in, outputs=[status_out, result_out])
    return demo


if __name__ == "__main__":
    build_ui().launch()
