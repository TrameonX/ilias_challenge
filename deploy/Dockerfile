# Image de déploiement : API (Mathieu) + UI (Julie) + IA (Steph) dans un conteneur.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Dépendances (le requirements racine couvre fastapi, uvicorn, gradio, pypdf,
# openai pour Groq, requests, python-multipart...)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code complet
COPY . .

RUN chmod +x deploy/start.sh

# Render fournit $PORT (utilisé par l'UI). L'API tourne en interne sur 8000.
CMD ["bash", "deploy/start.sh"]
