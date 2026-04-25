import re
from typing import Optional


_PII_PATTERNS = [
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL]"),
    (re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[PHONE]"),
    (re.compile(r"\b(?:\d[ -]?){13,16}\b"), "[CARD]"),
    (re.compile(r"\b(?:sk|pk|api|key|token|secret|password|passwd|pwd)\s*[=:]\s*\S+", re.IGNORECASE), "[REDACTED_CREDENTIAL]"),
]

_LOG_TRUNCATE_LEN = 200


def sanitize_prompt(prompt: str) -> str:
    """Strip control characters that could cause injection or display issues."""
    # Remove null bytes and non-printable control chars (keep newlines/tabs)
    sanitized = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", prompt)
    return sanitized.strip()


def sanitize_for_log(prompt: str, max_length: int = _LOG_TRUNCATE_LEN) -> str:
    """Return a safe, truncated version of prompt for logging — redacts PII."""
    text = prompt[:max_length * 2]  # Work on a slice before regex
    for pattern, replacement in _PII_PATTERNS:
        text = pattern.sub(replacement, text)
    if len(text) > max_length:
        text = text[:max_length] + f"…[{len(prompt)} chars total]"
    return text


def sanitize_response_for_log(response: str, max_length: int = _LOG_TRUNCATE_LEN) -> str:
    return sanitize_for_log(response, max_length)
