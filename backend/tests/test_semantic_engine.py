import pytest

from ..services.semantic_engine import SemanticEngine


@pytest.fixture
def engine():
    # Uses Jaccard fallback if sentence-transformers not installed
    return SemanticEngine()


def test_identical_texts_score_one(engine):
    text = "Summarize the document in three bullet points focusing on key insights."
    result = engine.compute_similarity(text, text)
    assert result.similarity_score >= 0.99


def test_similar_texts_high_score(engine):
    a = "Summarize the document in three bullet points."
    b = "Provide a three-point summary of the document."
    result = engine.compute_similarity(a, b)
    assert result.similarity_score > 0.3  # Jaccard is conservative


def test_dissimilar_texts_low_score(engine):
    a = "Summarize the quarterly financial report."
    b = "Write a poem about autumn leaves falling."
    result = engine.compute_similarity(a, b)
    assert result.similarity_score < 0.7


def test_risk_level_low_for_high_similarity(engine):
    text = "Analyze customer feedback for sentiment."
    result = engine.compute_similarity(text, text)
    # Identical → always low risk
    assert result.risk_level == "low"


def test_result_schema(engine):
    result = engine.compute_similarity("Hello world", "Hi there")
    assert 0.0 <= result.similarity_score <= 1.0
    assert result.risk_level in ("low", "medium", "high")
    assert result.embedding_model  # Not empty
    assert 0.0 <= result.confidence <= 1.0
