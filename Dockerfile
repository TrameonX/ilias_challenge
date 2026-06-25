# Image unique servant au backend ET au frontend (la commande change via compose).
FROM python:3.11-slim

# Évite les .pyc et bufferise pas les logs (pratique en conteneur).
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 1) Dépendances d'abord (cache Docker efficace)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2) Code
COPY . .

# Backend par défaut ; surchargé par docker-compose pour l'UI.
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
