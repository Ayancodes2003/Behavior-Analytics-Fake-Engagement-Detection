# Production Deployment Guide

This document describes how to run the **inference-only** fake engagement detection system.

## Architecture

The system consists of:

- **`core/`**: Reusable inference logic (no training)
  - `detector.py` - Model loading and anomaly scoring
  - `features.py` - Feature extraction for raw data
  - `simulation.py` - Synthetic data generation (for testing)
  - `injection.py` - Fraud pattern injection (for testing)

- **`app/`**: Production application (API + UI)
  - `api/main.py` - FastAPI backend (`POST /detect`, `POST /simulate`, `GET /health`)
  - `ui/dashboard.py` - Streamlit interactive dashboard
  - `services/detector_service.py` - Orchestration layer
  - `models/saved_model.pkl` - Pre-trained binary classifier (joblib)

- **`src/`**: Legacy research code (untouched)
  - `data/` - Data generators (used by core modules)
  - `features/` - Feature engineering functions (used by core modules)
  - **NOT** used: `training/`, MLflow logging, experiment runners

## Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

## Training a Model (One-time)

If you need to train a new classifier:

```bash
# This uses src/training code (NOTpart of production)
python -m src.training.train_main --config config/config.yaml
```

The trained model will be saved to `app/models/saved_model.pkl`.

## Running the Production System

### 1. Start the FastAPI Backend

```bash
uvicorn app.api.main:app --reload
```

API endpoints:
- `GET /health` - System status
- `POST /detect` - Analyze engagement data
- `POST /simulate` - Generate synthetic data

### 2. Launch the Streamlit Dashboard

In another terminal:

```bash
streamlit run app/ui/dashboard.py
```

Streamlit will open at `http://localhost:8501`.

### 3. Use the Dashboard

**Upload page:**
- Upload a CSV with `timestamp` and `views` (minimum)
- Optionally include: `likes`, `comments`, `shares`
- Preview the data

**Detection page:**
- Click "Run Detection"
- View authenticity score (0-100), bot probability, and anomaly timeline
- Inspect top behavioral triggers (features indicating fraud)

**Simulation page:**
- Generate synthetic normal or fake engagement
- Configure duration, fraud pattern, etc.
- Automatically loads into detector for analysis

## API Usage (Direct)

### Detect Endpoint

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "csv_text=$(cat engagement.csv)"
```

Response:
```json
{
  "anomaly_score": 0.34,
  "authenticity_score": 66.0,
  "bot_probability": 0.34,
  "top_behavioral_triggers": [
    "views_n_peaks",
    "likes_trend_slope",
    "comments_autocorr_lag_1"
  ],
  "per_row_scores": [
    { "timestamp": "...", "views": 100, "anomaly_score": 0.2 },
    ...
  ]
}
```

### Simulate Endpoint

```bash
curl -X POST "http://localhost:8000/simulate" \
  -G \
  -d "start_date=2021-01-01" \
  -d "length_days=30" \
  -d "fake=true" \
  -d "fake_pattern=burst"
```

Response: Array of time series records with `timestamp`, `views`, `likes`, `comments`, `shares`, `label`.

## Testing

Run the inference pipeline smoke test:

```bash
python test_inference_pipeline.py
```

This verifies that:
- Core modules import cleanly
- Detector can make predictions without training code
- Feature validation works

## Model Requirements

The model at `app/models/saved_model.pkl` must be:
- A scikit-learn binary classifier
- Implements `predict_proba(X)` returning shape `(n_samples, 2)`
- Optionally has `feature_importances_` for trigger extraction

Example training code (for reference only):

```python
from sklearn.ensemble import RandomForestClassifier
from core import detector

X_train, y_train = ...  # feature matrix, binary labels
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

detector.save_model(clf, "app/models/saved_model.pkl")
```

## Troubleshooting

**"Detector model is not loaded"**
- Ensure `app/models/saved_model.pkl` exists
- FastAPI loads it at startup; check logs for errors

**"Cannot connect to API"**
- FastAPI must be running at `localhost:8000`
- Streamlit connects via HTTP requests

**Feature extraction errors**
-Ensure input CSV has a `timestamp` column
- Views/engagement column can be named `views` or `engagement_count`
- Dates will be auto-parsed

## Performance Notes

- Feature extraction on 336-point time series (~14 days hourly) takes <100ms
- Model prediction is near-instantaneous (<10ms)
- Streamlit dashboard is responsive for typical engagement datasets

## Data Format

Expected CSV structure:

```csv
timestamp,views,likes,comments,shares
2021-01-01T00:00:00,100,10,5,2
2021-01-01T01:00:00,120,12,6,2
...
```

Minimum: `timestamp`, `views` (or `engagement_count`)
