"""Utility to create a placeholder classifier so the API can start even
without real training data.
"""
from sklearn.dummy import DummyClassifier
import joblib

if __name__ == "__main__":
    clf = DummyClassifier(strategy="uniform")
    # train on trivial data so predict_proba works
    X = [[0], [1]]
    y = [0, 1]
    clf.fit(X, y)
    joblib.dump(clf, "app/models/saved_model.pkl")
    print("Dummy model saved to app/models/saved_model.pkl")
