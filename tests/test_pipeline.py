"""Tests de bout en bout avec le provider 'mock' (aucune clé requise).

Lancement : MODEL_PROVIDER=mock pytest -q
"""
from __future__ import annotations

import os
import time

os.environ.setdefault("MODEL_PROVIDER", "mock")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def _wait_result(job_id: str, timeout: float = 5.0) -> dict:
    deadline = time.time() + timeout
    while time.time() < deadline:
        data = client.get(f"/result/{job_id}").json()
        if data["status"] in ("COMPLETED", "FAILED"):
            return data
        time.sleep(0.1)
    raise AssertionError("Timeout waiting for job")


def test_upload_txt_completes():
    files = {"file": ("note.txt", b"This product is great, I love it. Excellent work!")}
    r = client.post("/upload", files=files)
    assert r.status_code == 202
    job_id = r.json()["job_id"]

    data = _wait_result(job_id)
    assert data["status"] == "COMPLETED"
    assert data["result"]["label"] == "positive"


def test_reject_bad_extension():
    r = client.post("/upload", files={"file": ("evil.exe", b"x")})
    assert r.status_code == 422


def test_reject_too_large():
    big = b"a" * (6 * 1024 * 1024)
    r = client.post("/upload", files={"file": ("big.txt", big)})
    assert r.status_code == 422


def test_corrupted_pdf_fails_gracefully():
    r = client.post("/upload", files={"file": ("broken.pdf", b"%PDF-1.4 not really")})
    assert r.status_code == 202  # accepté...
    data = _wait_result(r.json()["job_id"])
    assert data["status"] == "FAILED"  # ...mais échoue proprement, pas de crash


def test_unknown_job_404():
    assert client.get("/result/does-not-exist").status_code == 404
