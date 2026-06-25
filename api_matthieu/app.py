import gradio as gr
import requests
import time
import os
import mimetypes


API_URL = os.getenv("API_URL", "http://localhost:8000")

def formater_resultat(result: dict) -> str:
    if not result:
        return "Analyse terminée mais l'IA n'a rien renvoyé."
    return "\n".join(f"• {cle.capitalize()} : {valeur}" for cle, valeur in result.items())

def traiter_le_fichier(file, progress=gr.Progress()):
    if file is None:
        return "J'attends un fichier, faites pas le radin !", ""

    progress(0.1, desc="Envoi du fichier à l'API...")
    
    try:
        nom_propre = os.path.basename(file.name)
        mime_type = mimetypes.guess_type(nom_propre)[0] or "application/octet-stream"
        
        with open(file.name, "rb") as f:
            response = requests.post(
                f"{API_URL}/upload", 
                files={"file": (nom_propre, f, mime_type)},
                data={"task": "summarize"}
            )
        
        if response.status_code != 200:
            return "Refusé par l'API", f"Erreur {response.status_code} : {response.text}"
            
        job_id = response.json().get("job_id")
        
    except Exception as e:
        return "API injoignable", f"Impossible de se connecter à l'API. Erreur: {e}"

    compteur = 0
    while True:
        time.sleep(1)
        compteur += 1
        
        try:
            status_response = requests.get(f"{API_URL}/jobs/{job_id}")
            if status_response.status_code != 200:
                return "Erreur Statut", f"Impossible de récupérer le job {job_id}"
                
            data = status_response.json()
            status = data.get("status")
            
            if status == "PENDING":
                progress(0.3, desc="Fichier en attente de traitement...")
            elif status == "RUNNING":
                progress(0.6, desc="L'IA analyse ton fichier...")
            elif status == "COMPLETED":
                progress(1.0, desc="Analyse terminée !")
                return "Analyse terminée avec succès", formater_resultat(data.get("result"))
            elif status == "FAILED":
                progress(1.0, desc="Échec")
                erreur = data.get("error", "Raison inconnue")
                return "Échec du traitement", f"Erreur remontée par le serveur : {erreur}"
                
        except Exception as e:
            return "Connexion perdue", f"La connexion avec l'API a été coupée durant l'analyse : {e}"
            
        if compteur > 30:
            return "Timeout", "Le traitement a pris trop de temps (Max 30s)."


with gr.Blocks(theme=gr.Theme.from_hub("hmb/vaporwave")) as demo:
    gr.Markdown("# 🧠 Plateforme d'Analyse Documentaire - IA")
    gr.Markdown("Déposez un fichier `.txt` ou `.pdf` (max 5 Mo). L'API FastAPI s'occupe du traitement asynchrone.")
    
    with gr.Row():
        file_input = gr.File(label="Glissez votre fichier ici")
        
    with gr.Row():
        status_output = gr.Textbox(label="Statut en direct", interactive=False)
    
    result_output = gr.Textbox(label="Résultat de l'analyse", interactive=False, lines=10)
    
    file_input.upload(
        fn=traiter_le_fichier, 
        inputs=[file_input], \
        outputs=[status_output, result_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)