#!/usr/bin/env bash
# Démarre l'API (Mathieu) en interne, puis l'UI (Julie) sur le port public de Render.
set -e

# 1) API en arrière-plan sur :8000 (interne au conteneur)
#    cwd = api_matthieu pour ses imports plats ; PYTHONPATH=/app pour importer la IA (app/)
( cd /app/api_matthieu && PYTHONPATH=/app uvicorn main:app --host 0.0.0.0 --port 8000 ) &

# 2) Laisser l'API démarrer
sleep 4

# 3) UI au premier plan, branchée sur l'API interne, sur le port public $PORT (fourni par Render)
export API_URL="http://localhost:8000"
cd /app
python UI_July/app.py
