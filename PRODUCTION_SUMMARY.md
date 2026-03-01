# Production Inference System - Summary

## ✅ Completed Refactor

### Separation of Concerns

**`src/` (Untouched Research Code)**
```
src/data/              ← simulator, time series generation
src/features/         ← feature extraction (used by core)
src/training/         ← model training (NOT used in production)
src/models/           ← base model classes
src/inference/        ← legacy inference examples
```

**`core/` (Production Inference Logic)**
```
core/
├── detector.py       ← load_model, predict_anomaly, compute_anomaly_score
├── features.py       ← validate_and_prepare_df, generate_features
├── simulation.py     ← simulate_engagement, synthetic_dataset (imports src.data)
└── injection.py      ← inject_fake_engagement (imports src.data)
```

**`app/` (Production Application)**
```
app/
├── api/
│   └── main.py       ← FastAPI /detect, /simulate, /health
├── services/
│   └── detector_service.py  ← load_detector, detect_from_dataframe
├── ui/
│   ├── dashboard.py  ← Streamlit entrypoint
│   └── pages/
│       ├── 1_upload.py        ← CSV uploader
│       ├── 2_detection.py      ← Analysis & results
│       └── 3_simulation.py     ← Synthetic data generation
├── models/
│   └── saved_model.pkl        ← Pre-trained classifier
└── utils/
```

### Key Design Properties

✅ **No Training Code in Production Path**
- `src/training/` is never imported by core or app
- No MLflow, experiment runners, or logging
- No PyTorch model classes (only inference)

✅ **No Hidden Dependencies**
- `core/detector.py` imports only: pandas, numpy, joblib
- `app/services.py` imports only: pandas, core modules
- `app/api.py` imports only: fastapi, pandas, core, app.services
- `app/ui/*.py` imports only: streamlit, requests (for API calls)

✅ **Modular & Reusable**
- `core/` can be imported standalone
- `app/` depends only on `core/`
- Easy to swap model implementations or inference backends

### Data Flow

```
CSV Upload
    ↓
[app/ui/pages/1_upload.py]
    ↓
app/ui/pages/2_detection.py
    ↓
requests.post(http://localhost:8000/detect)
    ↓
[app/api/main.py]
    ↓
app/services/detector_service.py
    ↓
core/features.py          → features extraction
core/detector.py          → anomaly scoring
    ↓
{anomaly_score, authenticity_score, bot_probability, triggers}
    ↓
app/ui/pages/2_detection.py → visualize results
```

### Running the System

**Start API:**
```bash
uvicorn app.api.main:app --reload
```

**Start Dashboard:**
```bash
streamlit run app/ui/dashboard.py
```

**Usage:**
1. Upload/generate engagement CSV
2. Click "Run Detection"
3. View authenticity score and anomaly timeline

### Model Requirements

Model at `app/models/saved_model.pkl`:
- Must be scikit-learn classifier
- Must implement `predict_proba(X)` → shape `(n_samples, 2)`
- Optionally: `feature_importances_` for behavioral triggers

Example (train once, then freeze):
```python
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(X_train, y_train)
joblib.dump(clf, "app/models/saved_model.pkl")
```

### Testing

```bash
python test_inference_pipeline.py
```

Verifies:
- Core imports work
- Detector can predict without training code
- Feature validation works
- No hidden dependencies on src.training

### Files NOT Included in Production

- ❌ `src/training/` (use for batch model retraining only)
- ❌ `tests/` (development testing only)
- ❌ `src/models/` (PyTorch architectures)
- ❌ MLflow configs
- ❌ Experiment notebooks (kept for reference)
- ❌ Docker demo files

### Summary

The system is **pure inference**, **modular**, and **deployable**. Training is decoupled and can be run separately to update the saved model. All production code is in `core/` and `app/`, with clean imports and zero dependencies on experimental/training code.
