"""Tests de la couche IA : swappabilité + tâches (mock, sans clé)."""
from __future__ import annotations

from app.processing.inference.factory import get_model_client
from app.processing.inference.mock_client import MockClient


def test_factory_returns_mock():
    client = get_model_client("mock")
    assert isinstance(client, MockClient)
    assert client.name == "mock"


def test_factory_falls_back_to_mock_without_key():
    # Provider réel demandé mais aucune clé -> fallback robuste sur mock.
    client = get_model_client("anthropic")
    assert client.name == "mock"


def test_sentiment_positive():
    res = MockClient().infer("This is great, I love it. Excellent!", "sentiment")
    assert res["label"] == "positive"
    assert 0.0 <= res["score"] <= 1.0


def test_sentiment_negative():
    res = MockClient().infer("Terrible, awful, the worst. I hate this.", "sentiment")
    assert res["label"] == "negative"


def test_keywords_task():
    text = "Pipeline pipeline inference inference inference model storage storage"
    res = MockClient().infer(text, "keywords")
    assert "keywords" in res
    assert "inference" in res["keywords"]  # mot le plus fréquent
    assert "model" in res["keywords"]
