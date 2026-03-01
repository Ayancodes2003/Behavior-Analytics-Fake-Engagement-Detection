"""
Feature engineering wrapper.
Re-exports temporal feature functions and adds helpers for dynamic input
validation used by the API/UI.
"""
from typing import List, Optional
import pandas as pd

from src.features.temporal_features import extract_temporal_features


def generate_features(
    df: pd.DataFrame,
    id_column: str = "id",
    timestamp_column: str = "timestamp",
    metric_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """Return feature matrix for any engagement dataset.

    If columns are missing, the underlying extractor will simply ignore them.
    """
    return extract_temporal_features(
        df,
        id_column=id_column,
        timestamp_column=timestamp_column,
        metric_columns=metric_columns,
    )


def validate_and_prepare_df(
    df: pd.DataFrame,
    timestamp_column: str = "timestamp",
    engagement_col: str = "views",
) -> pd.DataFrame:
    """Perform minimal schema checks and fill defaults.

    The API allows uploading arbitrary csvs with a timestamp and an
    engagement count; this helper will create the columns expected by
    downstream code using defaults/zeros where necessary.
    """
    if timestamp_column not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_column}' not found")

    if engagement_col not in df.columns:
        # try alternative name
        if "engagement_count" in df.columns and engagement_col == "views":
            df["views"] = df["engagement_count"]
        else:
            # create placeholder column
            df[engagement_col] = 0

    # ensure datetime type
    df[timestamp_column] = pd.to_datetime(df[timestamp_column])
    return df
