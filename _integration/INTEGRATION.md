# Intégration — un seul démo qui marche

**Décision tech lead :** l'API officielle = celle de Mathieu (`api_matthieu/`).
On y branche ta vraie IA, on connecte l'UI de Julie dessus, on laisse tomber le
scaffold `app/` redondant (le « trop » signalé par le prof). On garde juste ta
couche IA (`app/core/` + `app/processing/inference/`).

✅ Déjà testé end-to-end de mon côté : UI → API Mathieu → ta IA renvoie bien le
résultat dans `result`.

## Les 3 fichiers livrés (dossier `_integration/`)

| Fichier livré | À copier vers |
|---|---|
| `ai_adapter.py` | `api_matthieu/ai_adapter.py` (nouveau) |
| `controllers.py` | `api_matthieu/controllers.py` (remplace — 1 ligne change : `DummyAIModel()` → `RealAIModel()`) |
| `UI_July_app.py` | `UI_July/app.py` (remplace — corrige les 3 bugs) |

## Étapes (PowerShell, dans le dossier du projet)

```powershell
cd "C:\Users\pc salon\Documents\Claude\Projects\Challenge Ilias"
git fetch origin
git checkout main
git checkout -b integration

# 1) Apporter les 3 parties dans la branche d'intégration
git checkout origin/feature/api -- api_matthieu
git checkout origin/feature/ui  -- UI_July
git checkout origin/feature/ia  -- app

# 2) Déposer les fichiers d'intégration
Copy-Item _integration/ai_adapter.py   api_matthieu/ai_adapter.py
Copy-Item _integration/controllers.py  api_matthieu/controllers.py -Force
Copy-Item _integration/UI_July_app.py  UI_July/app.py -Force
```

## Lancer la démo (2 terminaux)

**Terminal 1 — API (mode démo, sans clé) :**
```powershell
cd api_matthieu
pip install -r requirements.txt
$env:MODEL_PROVIDER="mock"
uvicorn main:app --host 0.0.0.0 --port 8000
```
Avec la vraie IA : `pip install anthropic`, puis
`$env:MODEL_PROVIDER="anthropic"; $env:ANTHROPIC_API_KEY="sk-ant-..."`.

**Terminal 2 — UI Julie :**
```powershell
cd UI_July
pip install gradio requests
python app.py        # http://localhost:7860
```

Upload un .txt, choisis « sentiment », clique Analyser → le résultat s'affiche.

## Réduire (le « trop » du prof) — après que la démo tourne

Le scaffold backend en double ne sert plus (Mathieu l'a remplacé). À supprimer :
```powershell
Remove-Item -Recurse -Force app/api, app/services, app/storage, app/main.py, app/processing/preprocessing.py, app/processing/validation.py
```
On garde `app/core/` et `app/processing/inference/` (ta IA, utilisée par l'adapter).

## Pousser
```powershell
git add -A
git commit -m "Integration: API Mathieu + IA Steph + UI Julie connectees"
git push origin integration
```
Puis PR `integration → main`.

> Note Docker : le `docker-compose.yml` actuel pointe sur l'ancien `app/`. On le
> repointe sur `api_matthieu/` une fois la démo validée (étape suivante).
