FROM python:3.11-slim

WORKDIR /code

# Dépendances système minimales (pypdf/gradio n'en ont pas besoin de plus)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Les vraies commandes (uvicorn / gradio) sont définies dans docker-compose.yml
# pour que la même image serve à la fois le conteneur api et le conteneur ui.
EXPOSE 8000 7860
