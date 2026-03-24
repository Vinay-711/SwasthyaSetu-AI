"""
MLflow model service for occupational risk prediction.
Falls back to a rule-based heuristic when no MLflow server is configured.
"""
import os
from typing import List, Dict, Any

_MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "")
_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "swasthya_risk_model")
_MODEL_VERSION = os.getenv("MLFLOW_MODEL_VERSION", "1")

# High-risk occupations
HIGH_RISK_OCCUPATIONS = {
    "miner", "construction worker", "farmer", "factory worker",
    "welder", "painter", "truck driver", "textile worker",
}

_RECOMMENDATIONS = {
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


def _rule_based_predict(occupation: str, age: int, symptoms: List[str]) -> Dict[str, Any]:
    """Simple heuristic when MLflow is unavailable."""
    score = 0.1
    top_risks = []

    if occupation.lower() in HIGH_RISK_OCCUPATIONS:
        score += 0.3
        top_risks.append(f"High-risk occupation: {occupation}")

    respiratory = {"cough", "breathlessness", "chest pain", "wheezing"}
    symptom_set = {s.lower().strip() for s in symptoms}
    overlap = respiratory & symptom_set
    if overlap:
        score += 0.2 * len(overlap)
        top_risks.append("Respiratory symptoms detected")

    if age > 50:
        score += 0.1
        top_risks.append("Age-related risk factor (>50)")

    score = min(score, 1.0)

    if score < 0.3:
        level = "low"
    elif score < 0.55:
        level = "medium"
    elif score < 0.75:
        level = "high"
    else:
        level = "critical"

    return {
        "risk_score": round(score, 3),
        "risk_level": level,
        "top_risks": top_risks or ["No specific risk factors identified"],
        "recommendations": _RECOMMENDATIONS[level],
        "model_version": "heuristic-v1",
    }


def predict_risk(occupation: str, age: int, symptoms: List[str], region: str = "") -> Dict[str, Any]:
    """Predict occupational health risk. Uses MLflow if configured, else heuristic."""
    if _MLFLOW_TRACKING_URI:
        try:
            import mlflow
            mlflow.set_tracking_uri(_MLFLOW_TRACKING_URI)
            model_uri = f"models:/{_MODEL_NAME}/{_MODEL_VERSION}"
            model = mlflow.pyfunc.load_model(model_uri)

            import pandas as pd
            input_df = pd.DataFrame([{
                "occupation": occupation,
                "age": age,
                "symptom_count": len(symptoms),
                "region": region,
            }])
            prediction = model.predict(input_df)
            score = float(prediction[0])
            level = (
                "critical" if score >= 0.75
                else "high" if score >= 0.55
                else "medium" if score >= 0.3
                else "low"
            )
            return {
                "risk_score": round(score, 3),
                "risk_level": level,
                "top_risks": ["MLflow model prediction"],
                "recommendations": _RECOMMENDATIONS[level],
                "model_version": f"{_MODEL_NAME}@{_MODEL_VERSION}",
            }
        except Exception:
            pass  # fall through to heuristic

    return _rule_based_predict(occupation, age, symptoms)
