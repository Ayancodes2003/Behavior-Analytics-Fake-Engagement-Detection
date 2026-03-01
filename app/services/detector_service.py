"""
High‑level detection service for production API and UI.

Orchestrates feature extraction, model prediction, and score aggregation.
Purely inference-based; no training code.
"""
from typing import Dict, Any
import pandas as pd
import numpy as np

from core import features, detector

# global model cache (loaded once at startup)
_model = None


def load_detector(model_path: str) -> None:
    """Load pre-trained classifier into memory."""
    global _model
    _model = detector.load_model(model_path)


def detect_from_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """Run complete detection pipeline on raw engagement data.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input time series with timestamp and engagement metrics
        
    Returns
    -------
    dict
        Results including anomaly_score, authenticity_score, bot_probability,
        top_behavioral_triggers, and per_row_scores
    """
    # validate and prepare input
    df = features.validate_and_prepare_df(df)

    # extract temporal features
    feat_df = features.generate_features(df)

    if _model is None:
        raise RuntimeError("Detector model not loaded. Call load_detector(path) first.")

    # get per-sample anomaly scores
    anomaly_scores = detector.predict_anomaly(_model, feat_df)

    # compute aggregate anomaly score
    mean_anomaly = detector.compute_anomaly_score(anomaly_scores)
    
    # derive authenticity and bot probability
    authenticity = compute_authenticity_score(mean_anomaly)
    bot_probability = mean_anomaly

    # extract behavioral triggers (feature importance)
    top_features = _extract_top_features(_model, feat_df, top_k=5)

    # attach scores back to original data for visualization
    result_df = df.copy()
    result_df["anomaly_score"] = anomaly_scores

    return {
        "anomaly_score": mean_anomaly,
        "authenticity_score": authenticity,
        "bot_probability": bot_probability,
        "top_behavioral_triggers": top_features,
        "per_row_scores": result_df.to_dict(orient="records"),
    }


def compute_authenticity_score(anomaly_score: float) -> float:
    """Map anomaly score [0, 1] to authenticity [0, 100]."""
    return max(0.0, min(100.0, (1.0 - anomaly_score) * 100.0))


def _extract_top_features(model: Any, feat_df: pd.DataFrame, top_k: int = 5) -> list:
    """Extract most important features from model if available."""
    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
        top_indices = np.argsort(importances)[::-1][:top_k]
        return [feat_df.columns[i] for i in top_indices]
    else:
        return []
