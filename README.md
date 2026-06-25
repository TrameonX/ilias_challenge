Pour build et lancer :


docker build -t ilias-ui .
docker run -p 7860:7860 -e API_URL=http://<adresse-API>:8000 ilias-ui

L'UI sera dispo sur http://localhost:7860.