import gradio as gr
import requests
import time

API_URL = "http://localhost:8000"

def traiter_le_fichier(file, progress=gr.Progress()):
    if file is None:
        return "J'attends un fichier, un truc, je sais pas, donne le moi, fais pas le radin", ""

    progress(0.1, desc="J'envoie ton fichier à l'API, attends 2 secondes")
    
    try:
        with open(file.name, "rb") as f:
            response = requests.post(f"{API_URL}/upload", files={"file": f})
        
        if response.status_code != 200:
            yield f"Erreur : {response.text}", ""
            return
            
        job_id = response.json().get("job_id")
        
    except Exception as e:
        return f"Impossible de converser avec l'API, elle est partie en pause clope ! Erreur: {e}", ""
    
    progress(0.3, desc="J'ai bien reçu le fichier, je le traite dans les plus brefs délais")
    status = "PENDING"
    
    while status in ["PENDING", "RUNNING"]:
        time.sleep(2) 
        
        try:
            res = requests.get(f"{API_URL}/result/{job_id}")
            
            if res.status_code == 200:
                data = res.json()
                status = data.get("status")

                if status == "RUNNING":
                    progress(0.6, desc="L'IA analyse ton fichier")
                
                if status == "COMPLETED":
                    progress(1.0, desc="Analyse terminée chef !")
                    insights = data.get("insights", "Rien n'a été renvoyé par l'IA.")
                    return str(insights)
                    
                elif status == "FAILED":
                    progress(1.0, desc="Erreur")
                    return "C'est malheureusement un échec pour le joueur français"
            else:
                return f"Problème de communication avec l'API : {res.status_code}", ""
                
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
        outputs=[result_output]
    )

if __name__ == "__main__":
    demo.launch(share=True)