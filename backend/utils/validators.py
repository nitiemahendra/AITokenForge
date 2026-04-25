from fastapi import HTTPException, status


def validate_prompt_length(prompt: str, max_length: int) -> None:
    if len(prompt) > max_length:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Prompt exceeds maximum allowed length of {max_length} characters.",
        )


def validate_compression_ratio(original: int, optimized: int, threshold: float = 0.05) -> list[str]:
    """Return warnings if optimization produced unexpected results."""
    warnings = []
    if optimized >= original:
        warnings.append("Optimized prompt is not shorter than the original; the original will be used.")
    ratio = 1 - (optimized / original) if original > 0 else 0
    if ratio > 0.90:
        warnings.append(
            f"Extreme compression detected ({ratio:.0%}). Verify semantic preservation before use."
        )
    return warnings
