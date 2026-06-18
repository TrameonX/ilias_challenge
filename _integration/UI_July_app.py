"""UI Gradio corrigée pour se brancher sur l'API.

Corrections vs la version initiale :
  1. lit le résultat dans `result` (et pas `insights`)
  2. plus de mélange yield/return (le résultat s'affiche enfin)
  3. API_URL configurable (local / Docker / ngrok)
  + sélecteur de tâche IA + mise en forme du résultat

>>> Destination : UI_July/app.py
"""
import os
import time
import gradio as gr
import requests

# Configurable : localhost en local, http://api:8000 en Docker, URL ngrok à distance.
API_URL = os.getenv("API_URL", "http://localhost:8000")

TASKS = ["sentiment", "summarize", "keywords", "qa"]


def _format_result(result: dict) -> str:
    """Met en forme le dict renvoyé par l'API selon la tâche."""
    if not result:
        return "Rien n'a été renvoyé par l'IA."
    if "label" in result:  # sentiment
        score = result.get("score")
        line = f"Sentiment : {result['label']}"
        if score is not None:
            line += f"  (confiance {score})"
        if result.get("rationale"):
            line += f"\n{result['rationale']}"
        return line
    if "keywords" in result:
        return "Mots-clés : " + ", ".join(result["keywords"])
    if "summary" in result:
        return result["summary"]
    if "answer" in result:
        return result["answer"]
    return "\n".join(f"{k}: {v}" for k, v in result.items())


def traiter_le_fichier(file, task, progress=gr.Progress()):
    if file is None:
        return "En attente", "Donne-moi un fichier d'abord 🙂"

    progress(0.1, desc="Envoi du fichier à l'API…")
    try:
        with open(file.name, "rb") as f:
            resp = requests.post(
                f"{API_URL}/upload",
                files={"file": f},
                data={"task": task},
            )
    except Exception as e:
        return "Erreur", f"Impossible de joindre l'API : {e}"

    if resp.status_code not in (200, 202):
        return "Erreur", f"Upload refusé ({resp.status_code}) : {resp.text}"

    job_id = resp.json().get("job_id")
    progress(0.3, desc="Fichier reçu, traitement en cours…")

    status = "PENDING"
    while status in ("PENDING", "RUNNING"):
        time.sleep(2)
        try:
            res = requests.get(f"{API_URL}/result/{job_id}")
        except Exception as e:
            return "Erreur", f"Connexion perdue : {e}"
        if res.status_code != 200:
            return "Erreur", f"Problème API : {res.status_code}"
        data = res.json()
        status = data.get("status")
        if status == "RUNNING":
            progress(0.6, desc="L'IA analyse ton fichier…")
        elif status == "COMPLETED":
            progress(1.0, desc="Terminé ✅")
            return "COMPLETED", _format_result(data.get("result"))
        elif status == "FAILED":
            return "FAILED", f"Échec : {data.get('error')}"

    return status, "Fin inattendue du traitement."


with gr.Blocks(theme=gr.Theme.from_hub("hmb/vaporwave")) as demo:
    gr.Markdown("# Analyse avec l'IA")
    gr.Markdown("Upload un fichier .txt ou .pdf (max 5 MB). L'IA s'occupe du reste ;)")

    with gr.Row():
        file_input = gr.File(label="Glisse ton fichier ici")
        task_input = gr.Dropdown(TASKS, value="sentiment", label="Tâche IA")

    run_btn = gr.Button("Analyser", variant="primary")
    status_output = gr.Textbox(label="Statut", interactive=False)
    result_output = gr.Textbox(label="Résultat de l'analyse", interactive=False, lines=10)

    run_btn.click(
        fn=traiter_le_fichier,
        inputs=[file_input, task_input],
        outputs=[status_output, result_output],
    )

if __name__ == "__main__":
    demo.launch(
        server_name=os.getenv("UI_HOST", "0.0.0.0"),
        server_port=int(os.getenv("UI_PORT", "7860")),
    )
