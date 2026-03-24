"""
Pydantic models for SwasthyaSetu AI request/response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Health ID ──────────────────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str = Field(..., example="Ravi Kumar")
    age: int = Field(..., ge=0, le=150, example=34)
    gender: str = Field(..., example="M")
    blood_group: Optional[str] = Field(None, example="B+")
    phone: Optional[str] = Field(None, example="+91-9876543210")
    occupation: Optional[str] = Field(None, example="Miner")
    region: Optional[str] = Field(None, example="Rajasthan")


class PatientResponse(BaseModel):
    patient_id: str
    name: str
    age: int
    gender: str
    blood_group: Optional[str]
    phone: Optional[str]
    occupation: Optional[str]
    region: Optional[str]
    created_at: datetime
    qr_code_base64: Optional[str] = None   # PNG as base64 string


# ── Symptoms ───────────────────────────────────────────────────────────────

class TextSymptomsRequest(BaseModel):
    symptoms: str = Field(..., example="fever, cough, fatigue for 3 days")
    patient_id: Optional[str] = None


class SymptomsResponse(BaseModel):
    transcription: Optional[str] = None   # filled for voice requests
    symptoms: List[str]
    severity: str  # low | medium | high
    suggested_department: str


# ── OCR ────────────────────────────────────────────────────────────────────

class PrescriptionOCRResponse(BaseModel):
    raw_text: str
    medicines: List[str]
    dosages: List[str]
    doctor_name: Optional[str]
    hospital: Optional[str]
    date: Optional[str]


# ── Risk Prediction ────────────────────────────────────────────────────────

class RiskPredictionRequest(BaseModel):
    occupation: str = Field(..., example="Construction Worker")
    age: int = Field(..., example=42)
    region: str = Field(..., example="Punjab")
    symptoms: List[str] = Field(..., example=["cough", "back pain"])
    gender: Optional[str] = Field("M", example="M")


class RiskPredictionResponse(BaseModel):
    risk_score: float          # 0.0 – 1.0
    risk_level: str            # low | medium | high | critical
    top_risks: List[str]
    recommendations: List[str]
    model_version: str


# ── Notifications ──────────────────────────────────────────────────────────

class NotificationSendRequest(BaseModel):
    patient_id: str
    message: str = Field(..., example="Your next appointment is tomorrow at 10 AM.")
    channel: str = Field("sms", example="sms")   # sms | push | email


class NotificationRecord(BaseModel):
    notification_id: str
    patient_id: str
    message: str
    channel: str
    status: str   # sent | failed | pending
    sent_at: datetime


class NotificationHistoryResponse(BaseModel):
    patient_id: str
    notifications: List[NotificationRecord]
