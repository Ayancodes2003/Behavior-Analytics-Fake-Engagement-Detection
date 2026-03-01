"""
FastAPI backend for fake engagement detection.

Provides endpoints for:
- /detect: Analyze uploaded engagement data
- /simulate: Generate synthetic engagement (normal or fake)
- /health: System health check

All endpoints use inference-only code from core/ and app/services.
"""
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
from io import StringIO
from typing import Optional
from datetime import datetime

from app.services.detector_service import load_detector, detect_from_dataframe
from core import simulation, injection

app = FastAPI(
    title="Fake Engagement Detection API",
    description="Detect and analyze inauthentic engagement patterns",
    version="1.0.0",
)

# Load default model at startup if available
try:
    load_detector("app/models/saved_model.pkl")
except FileNotFoundError:
    print("Warning: saved_model.pkl not found. /detect will fail until model is loaded.")
except Exception as e:
    print(f"Warning: Could not load model: {e}")


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "fake-engagement-detector"}


@app.post("/detect")
def detect(
    file: Optional[UploadFile] = File(None),
    csv_text: Optional[str] = None,
    json_data: Optional[list] = None,
):
    """Detect fake engagement in time series data.
    
    Accepts input in three formats:
    - Uploaded CSV file
    - Raw CSV text
    - JSON list of records
    
    Expected columns: timestamp (required), views or engagement_count (required)
    Optional: likes, comments, shares
    
    Returns:
    - anomaly_score: [0, 1] where 1 = definitely fake
    - authenticity_score: [0, 100] where 100 = definitely authentic
    - bot_probability: [0, 1] probability of bot engagement
    - top_behavioral_triggers: features most indicative of fraud
    - per_row_scores: per-timestamp anomaly scores for visualization
    """
    if file is None and csv_text is None and json_data is None:
        raise HTTPException(status_code=400, detail="No data provided")

    # Parse input
    if json_data is not None:
        try:
            df = pd.DataFrame(json_data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
    else:
        if file is not None:
            content = file.file.read().decode("utf-8")
        else:
            content = csv_text or ""

        try:
            df = pd.read_csv(StringIO(content))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Cannot parse CSV: {e}")

    # Run detection
    try:
        result = detect_from_dataframe(df)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Model not loaded: {e}",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return JSONResponse(content=result)


@app.post("/simulate")
def simulate(
    start_date: str,
    length_days: int = 30,
    frequency: str = "H",
    video_id: str = "sim_001",
    fake: bool = False,
    fake_pattern: str = "burst",
):
    """Generate synthetic engagement data (simulation helper).
    
    Parameters:
    - start_date: ISO format date (YYYY-MM-DD)
    - length_days: Duration in days (1-100)
    - frequency: 'H' for hourly, 'D' for daily
    - video_id: Identifier for the sequence
    - fake: If true, inject fraud patterns
    - fake_pattern: 'burst', 'synchronized', 'off_peak', 'perfect_correlation'
    
    Returns: JSON list of records with timestamp, views, likes, comments, shares, label
    """
    # Parse date
    try:
        dt = datetime.fromisoformat(start_date)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date: {e}")

    # Generate data
    try:
        if fake:
            df = injection.inject_fake_engagement(
                start_date=dt,
                length_days=length_days,
                frequency=frequency,
                video_id=video_id,
                fake_pattern=fake_pattern,
            )
        else:
            df = simulation.simulate_engagement(
                start_date=dt,
                length_days=length_days,
                frequency=frequency,
                video_id=video_id,
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {e}")

    # Convert to JSON-serializable format
    df["timestamp"] = df["timestamp"].astype(str)
    return JSONResponse(content=df.to_dict(orient="records"))
