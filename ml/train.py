# Train headache risk prediction model from data.csv.
# Cramps risk is served by the TF-DF random forest in ml/models/cramps_rf (not trained here).
# Run: python -m ml.train  (from the backend root)
import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import StandardScaler

COMMON_FEATURES = [
    "lh",
    "estrogen",
    "phase_order",
    "appetite_ord",
    "exerciselevel_ord",
    "sorebreasts_ord",
    "fatigue_ord",
    "sleepissue_ord",
    "moodswing_ord",
    "stress_ord",
    "foodcravings_ord",
    "indigestion_ord",
    "bloating_ord",
]

TARGETS = {
    # Excludes its own raw pain scale from the features, and includes the
    # other pain scale as a cross-signal.
    "headache": {
        "features": COMMON_FEATURES + ["cramps_ord"],
        "label_fn": lambda df: (df["headaches_ord"] >= 4).astype(int),
    },
}


def main():
    df = pd.read_csv("data/data.csv")

    for name, cfg in TARGETS.items():
        features = cfg["features"]
        y_all = cfg["label_fn"](df)

        train_mask = df["ml_split"] == "TRAIN"
        test_mask = df["ml_split"] == "TEST"

        X_train, y_train = df.loc[train_mask, features], y_all[train_mask]
        X_test, y_test = df.loc[test_mask, features], y_all[test_mask]

        scaler = StandardScaler().fit(X_train)
        X_train_scaled = scaler.transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        model = LogisticRegression(max_iter=1000, class_weight="balanced")
        model.fit(X_train_scaled, y_train)

        auc = roc_auc_score(y_test, model.predict_proba(X_test_scaled)[:, 1])
        print(f"[{name}] test AUC = {auc:.3f}  (n_train={len(X_train)}, n_test={len(X_test)})")

        joblib.dump(
            {"model": model, "scaler": scaler, "features": features},
            f"ml/models/{name}.joblib",
        )
        print(f"  saved -> ml/models/{name}.joblib")


if __name__ == "__main__":
    main()
