"""
scientific_validation.py - UET Core (v0.9.0)
===========================================
Repository-level validation helpers.

These utilities support internal numerical comparisons. They should not be treated as a
standalone substitute for topic-specific methods, baselines, or external review.
"""

from typing import Dict

import numpy as np


class ScientificValidator:
    """
    Computes internal comparison metrics for UET research topics.
    """

    @staticmethod
    def calculate_supplemental_score(
        real_data_ratio: float, param_source_rigor: float
    ) -> float:
        """
        Supplemental internal metric retained for historical compatibility.

        Score = (Real Data Count / Total Data Count) * (Param Rigor Weight)
        Rigor Weight: 1.0 (physical constant), 0.5 (tuned benchmark), 0.1 (guess)
        """
        return float(real_data_ratio * param_source_rigor)

    @staticmethod
    def calculate_sincerity_score(
        real_data_ratio: float, param_source_rigor: float
    ) -> float:
        """Backward-compatible alias for the legacy internal score."""
        return ScientificValidator.calculate_supplemental_score(
            real_data_ratio, param_source_rigor
        )

    @staticmethod
    def estimate_error_margin(
        prediction: np.ndarray, empirical: np.ndarray
    ) -> Dict[str, float]:
        """
        Standard statistical error estimation.
        """
        if prediction.shape != empirical.shape:
            return {"rmse": np.nan, "mae": np.nan, "correlation": np.nan}

        rmse = np.sqrt(np.mean((prediction - empirical) ** 2))
        mae = np.mean(np.abs(prediction - empirical))
        correlation = np.corrcoef(prediction.flatten(), empirical.flatten())[0, 1]

        return {
            "rmse": float(rmse),
            "mae": float(mae),
            "correlation": float(correlation),
        }

    @staticmethod
    def check_cross_topic_scaling(
        topic_a_params: Dict[str, float], topic_b_params: Dict[str, float]
    ) -> bool:
        """
        Placeholder structural check for cross-topic parameter consistency.

        Topic-level documentation must still explain the scientific rationale for any
        scaling assumptions and should not rely on this helper as proof.
        """
        return bool(topic_a_params is not None and topic_b_params is not None)


def get_rigor_report(
    topic: str, sincerity: float, error_metrics: Dict[str, float]
) -> str:
    """Standardized string output for internal research logs."""
    verdict = "PASSING INTERNAL SIGNAL" if sincerity > 0.8 else "REQUIRES TOPIC REVIEW"
    return f"""
    [INTERNAL VALIDATION REPORT: {topic}]
    ------------------------------------
    Supplemental score: {sincerity:.2f}
    RMSE (vs empirical): {error_metrics.get('rmse', 0):.4f}
    Correlation: {error_metrics.get('correlation', 0):.4f}
    Verdict: {verdict}
    """
