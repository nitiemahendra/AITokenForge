
import numpy as np

from ..models.responses import SemanticResult
from ..utils.logger import get_logger

logger = get_logger(__name__)

# Risk thresholds for semantic similarity
_RISK_THRESHOLDS = {
    "low": 0.88,
    "medium": 0.75,
}


class SemanticEngine:
    """
    Computes semantic similarity between original and optimized prompts
    using sentence-transformers embeddings.

    Falls back to a TF-IDF Jaccard approximation if sentence-transformers
    is unavailable (e.g., minimal install / CI).
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._available = False
        self._init_model()

    def _init_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self._model_name, device=self._device)
            self._available = True
            logger.info("embedding_model_loaded", model=self._model_name, device=self._device)
        except Exception as exc:
            logger.warning(
                "embedding_model_unavailable",
                model=self._model_name,
                error=str(exc),
                fallback="jaccard",
            )
            self._available = False

    @property
    def is_available(self) -> bool:
        return self._available

    @property
    def embedding_model_name(self) -> str:
        return self._model_name if self._available else "jaccard-fallback"

    def compute_similarity(self, text_a: str, text_b: str) -> SemanticResult:
        if self._available and self._model is not None:
            return self._cosine_similarity(text_a, text_b)
        return self._jaccard_similarity(text_a, text_b)

    def _cosine_similarity(self, text_a: str, text_b: str) -> SemanticResult:
        try:
            embeddings = self._model.encode([text_a, text_b], convert_to_numpy=True, normalize_embeddings=True)
            score = float(np.dot(embeddings[0], embeddings[1]))
            score = max(0.0, min(1.0, score))
            return SemanticResult(
                similarity_score=round(score, 4),
                risk_level=self._risk_level(score),
                embedding_model=self._model_name,
                confidence=0.95,
            )
        except Exception as exc:
            logger.error("cosine_similarity_error", error=str(exc))
            return self._jaccard_similarity(text_a, text_b)

    def _jaccard_similarity(self, text_a: str, text_b: str) -> SemanticResult:
        tokens_a = set(text_a.lower().split())
        tokens_b = set(text_b.lower().split())
        union = tokens_a | tokens_b
        score = 1.0 if not union else len(tokens_a & tokens_b) / len(union)
        score = max(0.0, min(1.0, score))
        return SemanticResult(
            similarity_score=round(score, 4),
            risk_level=self._risk_level(score),
            embedding_model="jaccard-fallback",
            confidence=0.6,  # Lower confidence for fallback
        )

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= _RISK_THRESHOLDS["low"]:
            return "low"
        if score >= _RISK_THRESHOLDS["medium"]:
            return "medium"
        return "high"
