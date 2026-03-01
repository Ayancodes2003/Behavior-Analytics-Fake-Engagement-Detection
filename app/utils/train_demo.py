"""Utility script to train a simple model and persist it for the API/UI."""
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from core import simulation, features, detector


def main():
    # generate a small synthetic dataset
    df = simulation.synthetic_dataset(n_normal=50, n_fake=20, length_days=14, frequency="H")

    # compute features
    feat_df = features.generate_features(df)

    # prepare labels
    if "label" in df.columns:
        labels = (df.groupby("id")["label"].first() == "fake").astype(int).values
    else:
        labels = pd.Series(0, index=feat_df.index)

    # train a random forest baseline
    X = feat_df.values
    y = labels
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf = detector.train_model(X, y, clf)

    # save
    output_path = "app/models/saved_model.pkl"
    detector.save_model(clf, output_path)
    print(f"Model trained and saved to {output_path}")


if __name__ == "__main__":
    main()
