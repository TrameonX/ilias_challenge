# AI File Processing Pipeline

Plateforme de traitement de fichiers par IA. L'utilisateur uploade un fichier,
le système le valide, le prétraite, lance une inférence via **Llama (Ollama)**,
et renvoie les insights de façon **asynchrone**.

> Challenge Ilias — équipe : interface Julie (Gradio), API Mathieu (FastAPI), archi Steph.

## Pipeline

```
Upload -> Validation -> Preprocessing -> Inference (Ollama/Llama) -> Storage -> Result
```

## Architecture en 4 couches

| Couche | Dossier | Rôle |
|---|---|---|
| **API** | `API/controllers.py` | Endpoints HTTP (validation requête + délégation) |
| **Service** | `API/services.py` | Orchestration du pipeline, gestion des erreurs |
| **Modèle** | `API/models.py` | OllamaAIModel (Llama), DummyAIModel (tests) |
| **Storage** | `API/storage.py` | Persistance des jobs in-memory (remplaçable par Redis/SQL) |

Point d'entrée FastAPI : `app/main.py`  
Interface Gradio : `ui/app.py`

## Prérequis

- [Ollama](https://ollama.com) installé et lancé (`ollama serve`)
- Modèle téléchargé : `ollama pull llama3.2`
- Docker Desktop (pour le mode conteneur)

## Lancement — Docker (recommandé)

```bash
docker compose up --build
```

- API  → http://localhost:8000  (doc Swagger : /docs)
- UI   → http://localhost:7860

> L'API joint Ollama via `host.docker.internal:11434`. Ollama doit tourner sur le poste hôte.

Pour arrêter : `docker compose down`

## Lancement — sans Docker

```bash
pip install -r requirements.txt

# Terminal 1 — API
uvicorn app.main:app --reload

# Terminal 2 — Interface
python ui/app.py
```

## Contrat API

| Endpoint | Description |
|---|---|
| `POST /upload` | Accepte TXT/PDF ≤ 5 MB, renvoie `job_id` immédiatement (200) |
| `GET /result/{job_id}` | Renvoie `PENDING / RUNNING / COMPLETED / FAILED` + insights |

Tâches disponibles (paramètre `task` du formulaire) : `summarize`, `keywords`, `sentiment`, `qa`.

## Tests

Les tests utilisent `DummyAIModel` — **Ollama non requis en CI**.

```bash
pytest tests -q
```

Couvre : upload OK, rejet mauvais format, rejet > 5 MB, PDF corrompu (pas de crash), job inconnu (404), couche modèle (DummyAIModel).

## CI/CD (GitHub Actions)

- **CI** : déclenché sur chaque push/PR → tests + build image Docker (`deploy/Dockerfile`)
- **CD** : sur `main` uniquement → déploiement Render (nécessite le secret `RENDER_DEPLOY_HOOK_URL`)

## Contraintes respectées

- ✅ Séparation des couches (controllers / services / models / storage)
- ✅ Traitement asynchrone (`/upload` non bloquant, background task)
- ✅ Robustesse — un échec d'inférence passe le job en `FAILED`, l'API ne plante jamais
- ✅ Interface découplée — l'UI ne parle à l'IA que via HTTP
