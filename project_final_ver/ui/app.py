import gradio as gr
import requests
import time
import os
import mimetypes

API_URL = os.getenv("API_URL", "http://localhost:8000")

def formater_resultat(result: dict) -> str:
    if not result:
        return "Analyse terminée mais l'IA n'a rien renvoyé."
    return "\n".join(f"• {cle} : {valeur}" for cle, valeur in result.items())

def traiter_le_fichier(file, progress=gr.Progress()):
    if file is None:
        return "J'attends un fichier, un truc, je sais pas, donne le moi, fais pas le radin", ""

    progress(0.1, desc="J'envoie ton fichier à l'API, attends 2 secondes")
    
    try:
        nom_propre = os.path.basename(file.name)
        mime_type = mimetypes.guess_type(nom_propre)[0] or "application/octet-stream"
        with open(file.name, "rb") as f:
            response = requests.post(f"{API_URL}/upload", files={"file": (nom_propre, f, mime_type)})
        
        if response.status_code != 200:
            return "Refusé par l'API", f"Erreur : {response.text}"
            
        job_id = response.json().get("job_id")
        
    except Exception as e:
        return "API injoingnable", f"Impossible de converser avec l'API, elle est partie en pause clope ! Erreur: {e}"
    
    progress(0.3, desc="J'ai bien reçu le fichier, je le traite dans les plus brefs délais")
    status = "PENDING"
    
    while status in ["PENDING", "RUNNING"]:
        time.sleep(2) 
        
        try:
            res = requests.get(f"{API_URL}/result/{job_id}")
            
            if res.status_code != 200:
                return "Erreur de communication", f"Statut http: {res.status_code}"
            data = res.json()
            status = data.get("status")

            if status == "RUNNING":
                progress(0.6, desc="L'IA analyse ton fichier")
                
            elif status == "COMPLETED":
                    progress(1.0, desc="Analyse terminée chef !")
                    return "Analyse terminée boss", formater_resultat(data.get("result"))
                                                                      
            elif status == "FAILED":
                progress(1.0, desc="Erreur")
                erreur = data.get("error", "raison inconnue")
                return "Échec du traitement", f"C'est malheureusement un échec pour le joueur français : {erreur}"
                
        except Exception as e:
            return f"Connexion perdue : {e}", ""


with gr.Blocks(theme=gr.Theme.from_hub("hmb/vaporwave")) as demo:
    gr.Markdown("# Analyse avec l'IA")
    gr.Markdown("Upload un fichier .txt ou .pdf (max 5 MB stp faut pas déconner). L'IA s'occupe du reste ma queen ;)")
    
    with gr.Row():
        file_input = gr.File(label="Glisse ton fichier ici por favor")
        
    with gr.Row():
        status_output = gr.Textbox(label="Statut en direct", interactive=False)
    
    result_output = gr.Textbox(label="Résultat de l'analyse", interactive=False, lines=10)
    
    file_input.upload(
        fn=traiter_le_fichier, 
        inputs=[file_input], 
        outputs=[status_output, result_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, inbrowser=True)
