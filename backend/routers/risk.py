"""
Router: Occupational risk prediction.
POST /risk/predict

All business logic is in services/prediction_service.py.
This router is a thin HTTP adapter only.
"""
from fastapi import APIRouter

from models.schemas import RiskPredictionRequest, RiskPredictionResponse
from services.prediction_service import predict_risk

router = APIRouter(prefix="/risk", tags=["Risk Prediction"])


@router.post("/predict", response_model=RiskPredictionResponse, summary="Predict occupational health risk")
async def predict_occupational_risk(request: RiskPredictionRequest):
    """
    Given occupation, age, region, and symptoms, return a risk assessment.
    Business logic is fully delegated to prediction_service.predict_risk().
    """
    result = predict_risk(
        occupation=request.occupation,
        age=request.age,
        symptoms=request.symptoms,
        region=request.region,
    )
    return RiskPredictionResponse(**result)
