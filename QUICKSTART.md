# Quick Start Checklist

## Pre-Flight

- [ ] Python 3.10+ installed
- [ ] `requirements.txt` dependencies installed
- [ ] Git repo cloned / codebase ready

## Model Setup

- [ ] Train or obtain a scikit-learn binary classifier
- [ ] Save model as `joblib` to `app/models/saved_model.pkl`
  
  ```python
  import joblib
  joblib.dump(trained_clf, "app/models/saved_model.pkl")
  ```

## Local Testing

```bash
# Test inference pipeline without API
python test_inference_pipeline.py
```

Expected output:
```
✓ All tests passed
```

## Start Services

**Terminal 1 - FastAPI Backend:**
```bash
uvicorn app.api.main:app --reload
```

Expected output:
```
Uvicorn running on http://127.0.0.1:8000
```

**Terminal 2 - Streamlit Dashboard:**
```bash
streamlit run app/ui/dashboard.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

## Verify System

1. Navigate to `http://localhost:8501` in browser
2. **Upload page**: Upload sample CSV (or generate synthetic)
3. **Detection page**: Click "Run Detection" → should show scores & timeline
4. **Simulation page**: Generate synthetic normal/fake data

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: core` | Ensure running from project root |
| `FileNotFoundError: saved_model.pkl` | Train model and save to `app/models/` |
| `ConnectionError: localhost:8000` | Ensure FastAPI is running in another terminal |
| `ValueError: Timestamp column not found` | CSV must have `timestamp` and `views` columns |

## Production Deployment

- Copy `app/`, `core/` directories only
- Exclude: `src/training/`, `tests/`, notebooks
- Include: `app/models/saved_model.pkl` (pre-trained)
- Update `requirements.txt` for production (no dev dependencies)

## API Examples

**Detect fake engagement:**
```bash
curl -X POST http://localhost:8000/detect \
  -F "file=@engagement.csv"
```

**Generate synthetic data:**
```bash
curl -X POST "http://localhost:8000/simulate?start_date=2021-01-01&fake=true"
```

**Health check:**
```bash
curl http://localhost:8000/health
```

## Files & Structure

```
✓ app/                  (production application)
✓ core/                 (inference logic)
✓ DEPLOYMENT.md         (detailed guide)
✓ PRODUCTION_SUMMARY.md (architecture)
✓ requirements.txt      (dependencies)
✓ README.md             (project overview)
```

---

**System Ready for Deployment** ✓
