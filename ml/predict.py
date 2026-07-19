# Compute headache/cramp risk + contributing factors.
# Headache uses a logistic regression model trained on data.csv (SFR-008~010).
# Cramps uses a TensorFlow Decision Forests random forest (ml/models/cramps_rf).
import joblib
import numpy as np
import pandas as pd
import ydf

FEATURE_LABELS = {
    "lh": "LH level",
    "estrogen": "Estrogen level",
    "phase_order": "Cycle phase",
    "appetite_ord": "Appetite change",
    "exerciselevel_ord": "Exercise level",
    "sorebreasts_ord": "Sore breasts",
    "fatigue_ord": "Fatigue",
    "sleepissue_ord": "Sleep issues",
    "moodswing_ord": "Mood swings",
    "stress_ord": "Stress",
    "foodcravings_ord": "Food cravings",
    "indigestion_ord": "Indigestion",
    "bloating_ord": "Bloating",
    "cramps_ord": "Cramp severity",
    "headaches_ord": "Headache severity",
}

_RISK_THRESHOLDS = [(0.35, "Low"), (0.55, "Moderate"), (0.75, "High")]

_bundles: dict[str, dict] = {}
_cramps_rf_model = None

_CRAMPS_RF_FEATURES = [
    "appetite_ord", "bloating_ord", "estrogen", "exerciselevel_ord", "fatigue_ord",
    "foodcravings_ord", "headaches_ord", "indigestion_ord", "lh", "moodswing_ord",
    "phase", "phase_cos", "sleepissue_ord", "sorebreasts_ord", "stress_ord",
]


def _load(name: str) -> dict:
    if name not in _bundles:
        _bundles[name] = joblib.load(f"ml/models/{name}.joblib")
    return _bundles[name]


def _load_cramps_rf():
    global _cramps_rf_model
    if _cramps_rf_model is None:
        _cramps_rf_model = ydf.from_tensorflow_decision_forests("ml/models/cramps_rf")
    return _cramps_rf_model


def _score_cramps_rf(features: dict) -> float:
    model = _load_cramps_rf()
    row = pd.DataFrame([{col: features.get(col, 0) for col in _CRAMPS_RF_FEATURES}])
    return float(model.predict(row)[0])


def _risk_label(prob: float) -> str:
    for threshold, label in _RISK_THRESHOLDS:
        if prob < threshold:
            return label
    return "Very High"


def _score(name: str, features: dict) -> tuple[float, list[tuple[str, float]]]:
    bundle = _load(name)
    model, scaler, columns = bundle["model"], bundle["scaler"], bundle["features"]

    x = np.array([[features.get(c, 0) for c in columns]], dtype=float)
    x_scaled = scaler.transform(x)
    prob = float(model.predict_proba(x_scaled)[0, 1])

    contributions = model.coef_[0] * x_scaled[0]
    factors = list(zip(columns, contributions))
    return prob, factors


def predict_risk(features: dict) -> dict:
    headache_prob, headache_factors = _score("headache", features)
    cramps_prob = _score_cramps_rf(features)

    top = sorted(headache_factors, key=lambda kv: -abs(kv[1]))[:3]

    confidence = (abs(headache_prob - 0.5) * 2 + abs(cramps_prob - 0.5) * 2) / 2

    return {
        "headache_risk": _risk_label(headache_prob),
        "stomachache_risk": _risk_label(cramps_prob),
        "confidence": round(confidence, 3),
        "factors": [
            {"label": FEATURE_LABELS.get(col, col), "value": round(float(value), 3)} for col, value in top
        ],
    }
