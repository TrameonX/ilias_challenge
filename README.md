# AI File Processing Pipeline

Plateforme de traitement de fichiers par IA. L'utilisateur uploade un fichier,
le système le valide, le prétraite, lance une inférence IA, et renvoie les
insights de façon **asynchrone**.

> Challenge Ilias — équipe : interface (Gradio), API (Mathieu), partie IA + archi (Steph, tech lead).

## Pipeline

```
Upload -> Validation -> Preprocessing -> Inference -> Storage -> Result Retrieval
```

## Architecture en 4 couches (separation of concerns)

| Couche | Dossier | Rôle |
|---|---|---|
| **API** | `app/api/` | Endpoints HTTP uniquement (validation requête + délégation) |
| **Service** | `app/services/` | Orchestration du pipeline, gestion des erreurs |
| **Processing** | `app/processing/` | Validation, preprocessing TXT/PDF, **inference swappable** |
| **Storage** | `app/storage/` | Persistance des jobs (in-memory, remplaçable par Redis/SQL) |

Diagramme complet : `architecture.mermaid`.

### Swappabilité du modèle
Tous les clients implémentent l'interface `ModelClient` (`app/processing/inference/base.py`).
Changer de modèle = **une ligne** dans `factory.py` + une variable `MODEL_PROVIDER`.
Providers fournis : `anthropic`, `openai`, `mock`.

### Robustesse
Un fichier corrompu ou un échec d'inférence fait passer le job en `FAILED`
(capté dans `JobService.run_pipeline`) — **l'API ne plante jamais**. Si la clé
API est absente, la factory bascule automatiquement sur le `mock`.

## Contrat API

| Endpoint | Description |
|---|---|
| `POST /upload` | Accepte TXT/PDF ≤ 5 MB, renvoie un `job_id` immédiatement (202) |
| `GET /result/{job_id}` | Renvoie `PENDING / RUNNING / COMPLETED / FAILED` + insights |

## Installation

```bash
pip install -r requirements.txt
cp .env.example .env   # puis renseigner ANTHROPIC_API_KEY
```

## Lancement

```bash
# 1) Backend (terminal 1)
uvicorn app.main:app --reload      # http://localhost:8000  (docs: /docs)

# 2) Frontend Gradio (terminal 2)
python -m ui.gradio_app            # http://localhost:7860
```

Sans clé API, lancer en mode démo :

```bash
MODEL_PROVIDER=mock uvicorn app.main:app --reload
```

## Mode équipe — API partagée (distanciel)

Décision tech lead : on travaille tous contre **une seule API de référence**, pas
chacun sur son `localhost`. L'intégration UI ↔ API se fait en continu.

**Hébergeur de l'API (par défaut : Mathieu)** lance le backend comme d'habitude,
puis l'expose avec un tunnel :

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000   # backend
ngrok http 8000                                    # -> https://xxxx.ngrok.io
# (alternative sans URL changeante : cloudflared tunnel --url http://localhost:8000)
```

Il partage l'URL `https://xxxx.ngrok.io` sur le chat de l'équipe.

**Les autres (UI, IA)** pointent simplement dessus, sans rien changer au code :

```bash
export API_URL=https://xxxx.ngrok.io   # Windows PowerShell : $env:API_URL="https://xxxx.ngrok.io"
python -m ui.gradio_app
```

> ⚠️ En ngrok gratuit, l'URL change à chaque redémarrage du backend : l'hébergeur
> redonne la nouvelle URL quand il relance. Pour développer une couche en isolation,
> chacun peut toujours retomber sur `MODEL_PROVIDER=mock` + `API_URL=http://localhost:8000`.

## Docker (stack complète en une commande)

Containerise le backend + le frontend. Idéal pour le distanciel et le déploiement
gratuit (HF Spaces, Render, Fly.io...).

```bash
# Mode démo (mock, sans clé) :
docker compose up --build

# Avec le vrai modèle :
MODEL_PROVIDER=anthropic ANTHROPIC_API_KEY=sk-ant-... docker compose up --build
```

- API → http://localhost:8000  (docs : /docs)
- UI  → http://localhost:7860

L'UI joint l'API par le réseau interne Docker (`API_URL=http://api:8000`), pas par
localhost. Pour exposer la démo à l'extérieur, ajouter un tunnel sur le port 7860
(`ngrok http 7860`) ou pousser l'image sur Hugging Face Spaces (SDK Docker).

## Tests

```bash
MODEL_PROVIDER=mock pytest -q
```

Couvre : upload OK, rejet mauvais type, rejet > 5 MB, PDF corrompu (FAILED
propre), job inconnu (404).

## Contraintes respectées

- ✅ Separation of concerns (API / Service / Processing / Storage)
- ✅ Model swappability (interface + factory + variable d'env)
- ✅ Failure handling (jamais de crash API)
- ✅ Pas d'appel modèle direct depuis Gradio (HTTP uniquement)
- ✅ Pas d'implémentation mono-fichier
- ✅ `/upload` non bloquant (traitement en background)
