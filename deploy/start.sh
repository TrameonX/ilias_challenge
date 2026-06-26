#!/usr/bin/env bash
set -e

# 1) API en arrière-plan sur :8000
uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# 2) Laisser l'API démarrer
sleep 4

# 3) UI au premier plan sur le port public $PORT (fourni par Render)
export API_URL="http://localhost:8000"
python ui/app.py
