"""
Fraud injection utilities.
This module provides functions to introduce fake engagement patterns into
existing or synthetic time series. Currently it re-uses the legacy
`generate_fake_timeseries` from the research code but exposes a clearer
interface for the production pipeline.
"""
from datetime import datetime
from typing import Optional
import pandas as pd

from src.data.simulate_timeseries import generate_fake_timeseries


def inject_fake_engagement(
    start_date: datetime,
    length_days: int,
    frequency: str = "H",
    video_id: str = "fake_001",
    fake_pattern: str = "burst",
    **kwargs,
) -> pd.DataFrame:
    """Produce a time series containing a fake engagement pattern.

    Parameters mirror :func:`generate_fake_timeseries`.
    """
    return generate_fake_timeseries(
        start_date=start_date,
        length_days=length_days,
        frequency=frequency,
        video_id=video_id,
        fake_pattern=fake_pattern,
        **kwargs,
    )
