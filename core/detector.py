"""
Inference-only anomaly detection module.

Loads a pre-trained binary classifier and computes anomaly/authenticity scores
from feature matrices. No training logic.
"""
from typing import Any
import pandas as pd
import numpy as np
import joblib


def load_model(path: str) -> Any:
    """Load serialized classifier from disk.
    
    Expected to be a scikit-learn Binary classifier with predict_proba.
    """
    return joblib.load(path)


def predict_anomaly(model: Any, X: pd.DataFrame) -> np.ndarray:
    """Compute anomaly scores (probability of being fake).
    
    Assumes model is binary classifier with predict_proba returning
    shape (n_samples, 2), where column 1 is probability of fake engagement.
    
    Parameters
    ----------
    model : sklearn classifier
        Fitted classifier with predict_proba method
    X : pd.DataFrame
        Feature matrix (n_samples, n_features)
    
    Returns
    -------
    np.ndarray
        Anomaly scores in [0, 1] where 1 = definitely fake
    """
    probs = model.predict_proba(X)
    if probs.ndim == 2 and probs.shape[1] == 2:
        return probs[:, 1]  # probability of class 1 (fake)
    else:
        # fallback for non-binary or malformed output
        return probs.max(axis=1)


def compute_anomaly_score(series: np.ndarray) -> float:
    """Aggregate per-sample anomaly scores into single metric.
    
    Parameters
    ----------
    series : np.ndarray
        Array of per-sample anomaly scores
    
    Returns
    -------
    float
        Mean anomaly score in [0, 1]
    """
    return float(np.mean(series))
