"""Tests de l'API — Ollama non requis en CI (on teste upload/validation/result)."""
import os
import time
os.environ.setdefault("OLLAMA_URL", "http://localhost:11434")

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_upload_txt_returns_job_id():
    files = {"file": ("note.txt", b"Ceci est un texte de test.", "text/plain")}
    r = client.post("/upload", files=files)
    assert r.status_code == 200
    body = r.json()
    assert "job_id" in body
    assert body["status"] == "PENDING"


def test_reject_bad_extension():
    r = client.post("/upload", files={"file": ("evil.exe", b"x", "application/octet-stream")})
    assert r.status_code == 400


def test_reject_too_large():
    big = b"a" * (6 * 1024 * 1024)
    r = client.post("/upload", files={"file": ("big.txt", big, "text/plain")})
    assert r.status_code == 400


def test_unknown_job_404():
    assert client.get("/result/does-not-exist").status_code == 404


def test_corrupted_pdf_accepted_no_crash():
    """Un PDF invalide est accepté à l'upload et finit sans crash serveur."""
    r = client.post("/upload", files={"file": ("broken.pdf", b"%PDF-1.4 not really", "application/pdf")})
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    deadline = time.time() + 10
    while time.time() < deadline:
        data = client.get(f"/result/{job_id}").json()
        if data["status"] in ("COMPLETED", "FAILED"):
            return  # terminé proprement, peu importe le résultat
        time.sleep(0.2)
    raise AssertionError("Timeout waiting for job")
