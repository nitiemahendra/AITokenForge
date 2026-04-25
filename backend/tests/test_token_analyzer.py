import pytest
from ..services.token_analyzer import TokenAnalyzer
from ..models.requests import TargetModel


@pytest.fixture
def analyzer():
    return TokenAnalyzer()


def test_count_tokens_gpt4o(analyzer):
    text = "Hello, world! This is a test prompt."
    count = analyzer.count_tokens(text, TargetModel.GPT_4O)
    assert count > 0
    assert isinstance(count, int)


def test_count_tokens_claude(analyzer):
    text = "Analyze the following customer feedback and identify key themes."
    count = analyzer.count_tokens(text, TargetModel.CLAUDE_SONNET_46)
    assert count > 0


def test_analyze_returns_valid_structure(analyzer):
    prompt = "You are a helpful assistant. Summarize the following text in 3 bullet points."
    result = analyzer.analyze(prompt, TargetModel.GPT_4O)
    assert result.token_count > 0
    assert result.estimated_output_tokens > 0
    assert result.total_estimated_tokens == result.token_count + result.estimated_output_tokens
    assert result.tokenizer_used in ("cl100k_base", "o200k_base")


def test_analyze_with_breakdown(analyzer):
    prompt = "System: You are a helpful assistant.\nConstraint: Always respond in JSON.\nUser: Summarize this."
    result = analyzer.analyze(prompt, TargetModel.GPT_4O, include_breakdown=True)
    assert result.breakdown is not None
    assert len(result.breakdown) > 0
    for item in result.breakdown:
        assert item.token_count >= 0
        assert item.type in ("instruction", "example", "constraint", "content")


def test_empty_ish_prompt(analyzer):
    prompt = "  hi  "
    count = analyzer.count_tokens(prompt.strip(), TargetModel.GPT_4O)
    assert count >= 1


def test_long_prompt_token_count(analyzer):
    prompt = "word " * 1000
    count = analyzer.count_tokens(prompt, TargetModel.GPT_4O)
    # 1000 common words should be roughly 1000–1300 tokens
    assert 800 < count < 1500
