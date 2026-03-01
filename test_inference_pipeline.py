#!/usr/bin/env python
"""
Quick smoke test for the production inference pipeline.

Verifies that core modules import cleanly and services can run
without training code.
"""
import sys
from pathlib import Path

def test_imports():
    """Test that core modules import without errors."""
    print("Testing imports...")
    try:
        from core import detector, features, simulation, injection
        print("  ✓ core modules")
    except Exception as e:
        print(f"  ✗ core modules: {e}")
        return False
    
    try:
        from app.services import detector_service
        print("  ✓ detector_service")
    except Exception as e:
        print(f"  ✗ detector_service: {e}")
        return False
    
    return True


def test_detector():
    """Test detector inference without training."""
    print("\nTesting detector inference...")
    try:
        from sklearn.dummy import DummyClassifier
        from core import detector
        import pandas as pd
        import numpy as np
        
        # Create dummy classifier
        clf = DummyClassifier(strategy='uniform')
        clf.fit([[0], [1]], [0, 1])
        
        # Test prediction
        X = pd.DataFrame([[0.5], [0.3]], columns=['feat1'])
        scores = detector.predict_anomaly(clf, X)
        assert isinstance(scores, np.ndarray)
        assert len(scores) == 2
        assert all(0 <= s <= 1 for s in scores)
        
        # Test aggregate
        agg = detector.compute_anomaly_score(scores)
        assert isinstance(agg, float)
        assert 0 <= agg <= 1
        
        print("  ✓ predict_anomaly")
        print("  ✓ compute_anomaly_score")
    except Exception as e:
        print(f"  ✗ detector: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_features():
    """Test feature validation."""
    print("\nTesting feature validation...")
    try:
        from core import features
        import pandas as pd
        
        # Create test data
        df = pd.DataFrame({
            'timestamp': ['2021-01-01', '2021-01-02'],
            'engagement_count': [10, 20],
        })
        
        # Validate
        df_clean = features.validate_and_prepare_df(
            df,
            timestamp_column='timestamp',
            engagement_col='views',
        )
        
        assert 'views' in df_clean.columns
        assert 'timestamp' in df_clean.columns
        
        print("  ✓ validate_and_prepare_df")
    except Exception as e:
        print(f"  ✗ features: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("Production Inference Pipeline Smoke Test")
    print("=" * 60)
    
    all_pass = True
    all_pass &= test_imports()
    all_pass &= test_detector()
    all_pass &= test_features()
    
    print("\n" + "=" * 60)
    if all_pass:
        print("✓ All tests passed")
        print("=" * 60)
        sys.exit(0)
    else:
        print("✗ Some tests failed")
        print("=" * 60)
        sys.exit(1)
