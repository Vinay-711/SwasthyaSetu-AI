"""
services/prediction_service.py
================================
All business logic for occupational health risk prediction.
API routers must call predict_risk() — no ML logic should exist in routers.
"""
import os
from typing import List, Dict, Any

# ── Config ─────────────────────────────────────────────────────────────────
_MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")
_MODEL_NAME          = os.getenv("MLFLOW_MODEL_NAME", "swasthya_risk_model")
_MODEL_VERSION       = os.getenv("MLFLOW_MODEL_VERSION", "1")

# ── Domain knowledge ───────────────────────────────────────────────────────
HIGH_RISK_OCCUPATIONS: set[str] = {
    "miner", "construction worker", "farmer", "factory worker",
    "welder", "painter", "truck driver", "textile worker",
}

RESPIRATORY_SYMPTOMS: set[str] = {"cough", "breathlessness", "chest pain", "wheezing"}

RISK_THRESHOLDS = {"low": 0.3, "medium": 0.55, "high": 0.75}

RECOMMENDATIONS: Dict[str, List[str]] = {
    "low": [
        "Maintain a healthy lifestyle and regular exercise.",
        "Schedule an annual health check-up.",
    ],
    "medium": [
        "Use protective equipment at work.",
        "Monitor symptoms weekly and consult a doctor if they worsen.",
        "Reduce exposure to dust and chemicals.",
    ],
    "high": [
        "Seek immediate medical consultation.",
        "Consider temporary leave from high-exposure environments.",
        "Use full PPE — mask, gloves, goggles.",
    ],
    "critical": [
        "URGENT: Visit an emergency or specialist clinic immediately.",
        "Stop exposure to environmental hazards at once.",
        "Notify your employer for occupational health review.",
    ],
}


def _score_to_level(score: float) -> str:
    """Convert a 0–1 risk score to a categorical risk level."""
    if score < RISK_THRESHOLDS["low"]:
        return "low"
    elif score < RISK_THRESHOLDS["medium"]:
        return "medium"
    elif score < RISK_THRESHOLDS["high"]:
        return "high"
    return "critical"


def _heuristic_predict(occupation: str, age: int, symptoms: List[str]) -> Dict[str, Any]:
    """
    Rule-based risk scoring — used when MLflow is not configured.
    This is the primary logic path for local/demo deployments.
    """
    score = 0.1
    top_risks: List[str] = []

    if occupation.lower() in HIGH_RISK_OCCUPATIONS:
        score += 0.3
        top_risks.append(f"High-risk occupation: {occupation}")

    symptom_set = {s.lower().strip() for s in symptoms}
    respiratory_overlap = RESPIRATORY_SYMPTOMS & symptom_set
    if respiratory_overlap:
        score += 0.2 * len(respiratory_overlap)
        top_risks.append("Respiratory symptoms detected")

    if age > 50:
        score += 0.1
        top_risks.append("Age-related risk factor (>50)")

    score = min(round(float(score), 3), 1.0)  # type: ignore[call-overload]
    level = _score_to_level(score)

    return {
        "risk_score": score,
        "risk_level": level,
        "top_risks": top_risks or ["No specific risk factors identified"],
        "recommendations": RECOMMENDATIONS[level],
        "model_version": "heuristic-v1",
    }


def _mlflow_predict(occupation: str, age: int, symptoms: List[str], region: str) -> Dict[str, Any]:
    """
    MLflow model-based prediction — used when MLFLOW_TRACKING_URI is set.
    Raises an exception if the model cannot be loaded (caller handles fallback).
    """
    import mlflow  # type: ignore[import-untyped]
    import pandas as pd  # type: ignore[import-untyped]

    mlflow.set_tracking_uri(_MLFLOW_TRACKING_URI)
    model_uri = f"models:/{_MODEL_NAME}/{_MODEL_VERSION}"
    model = mlflow.pyfunc.load_model(model_uri)

    input_df = pd.DataFrame([{
        "occupation": occupation,
        "age": age,
        "symptom_count": len(symptoms),
        "region": region,
    }])
    score: float = round(float(model.predict(input_df)[0]), 3)  # type: ignore[call-overload]
    level = _score_to_level(score)

    return {
        "risk_score": score,
        "risk_level": level,
        "top_risks": [f"MLflow model: {_MODEL_NAME}@{_MODEL_VERSION}"],
        "recommendations": RECOMMENDATIONS[level],
        "model_version": f"{_MODEL_NAME}@{_MODEL_VERSION}",
    }


# ── Public interface ───────────────────────────────────────────────────────

def predict_risk(
    occupation: str,
    age: int,
    symptoms: List[str],
    region: str = "",
) -> Dict[str, Any]:
    """
    Predict occupational health risk score.

    Strategy:
      1. If MLFLOW_TRACKING_URI is set → use the registered MLflow model.
      2. Otherwise (or on MLflow failure) → use the heuristic scoring engine.

    Args:
        occupation: Patient's job title.
        age:        Patient's age in years.
        symptoms:   List of symptom strings.
        region:     Geographic region (used by MLflow model; ignored by heuristic).

    Returns:
        Dict with keys: risk_score, risk_level, top_risks, recommendations, model_version.
    """
    if _MLFLOW_TRACKING_URI:
        try:
            return _mlflow_predict(occupation, age, symptoms, region)
        except Exception:
            pass  # Fall through to heuristic

    return _heuristic_predict(occupation, age, symptoms)


def get_risk_prediction(data: Dict[str, Any]) -> str:
    """
    Takes symptoms, age, job and returns risk level (low, medium, high)
    using simple heuristic logic.
    """
    symptoms = [s.lower() for s in data.get("symptoms", [])]
    occupation = data.get("occupation", "").lower()
    age = data.get("age", 0)

    score = 0
    if "fever" in symptoms:
        score += 2
    if "cough" in symptoms:
        score += 1

    if occupation in ["worker", "miner", "construction"]:
        score += 3
    elif occupation in ["teacher", "office worker"]:
        score += 1
        
    if age > 60:
        score += 2

    if score >= 5:
        return "high"
    elif score >= 3:
        return "medium"
    else:
        return "low"
