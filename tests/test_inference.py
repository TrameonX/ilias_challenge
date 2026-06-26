"""Tests de la couche modèle avec DummyAIModel (sans Ollama, sans clé API)."""
from API.models import DummyAIModel, PITask


def test_dummy_sentiment():
    result = DummyAIModel().run_inference(PITask.SENTIMENT, "Texte de test positif")
    assert "sentiment" in result
    assert "score" in result
    assert 0.0 <= result["score"] <= 1.0


def test_dummy_summarize():
    result = DummyAIModel().run_inference(PITask.SUMMARIZE, "Texte à résumer pour le test")
    assert "summary" in result
    assert isinstance(result["summary"], str)


def test_dummy_keywords():
    result = DummyAIModel().run_inference(PITask.KEYWORDS, "pipeline inference model storage")
    assert "keywords" in result
    assert isinstance(result["keywords"], list)
    assert len(result["keywords"]) > 0


def test_dummy_qa():
    result = DummyAIModel().run_inference(
        PITask.QA,
        "Le projet traite des fichiers texte et PDF.",
        question="Quel est le sujet ?"
    )
    assert "question" in result
    assert "answer" in result
