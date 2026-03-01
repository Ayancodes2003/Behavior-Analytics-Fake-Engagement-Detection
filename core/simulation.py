"""
Simplified simulation utilities for the production system.
This module wraps the existing research code and exposes convenient
functions for generating synthetic engagement data.
"""
from datetime import datetime
from typing import Optional
import pandas as pd

# re-exported from legacy module
from src.data.simulate_timeseries import (
    generate_normal_timeseries,
    generate_fake_timeseries,
    generate_dataset,
)


def simulate_engagement(
    start_date: datetime,
    length_days: int,
    frequency: str = "H",
    video_id: str = "normal_001",
    **kwargs,
) -> pd.DataFrame:
    """Produce a normal engagement time series.

    Parameters mirror :func:`generate_normal_timeseries`.
    """
    return generate_normal_timeseries(
        start_date=start_date,
        length_days=length_days,
        frequency=frequency,
        video_id=video_id,
        **kwargs,
    )


def synthetic_dataset(
    n_normal: int = 100,
    n_fake: int = 30,
    length_days: int = 30,
    frequency: str = "H",
    start_date: Optional[datetime] = None,
    output_path: str = "data/raw/engagement.parquet",
    output_format: str = "parquet",
    random_seed: int = 42,
) -> pd.DataFrame:
    """Wrapper for :func:`generate_dataset`.

    Returns combined dataset and saves to disk if a path is provided.
    """
    return generate_dataset(
        n_normal=n_normal,
        n_fake=n_fake,
        length_days=length_days,
        frequency=frequency,
        start_date=start_date,
        output_path=output_path,
        output_format=output_format,
        random_seed=random_seed,
    )
