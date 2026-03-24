"""
Router: Notification system.
POST /notifications/send         — send a notification to a patient
GET  /notifications/{patient_id} — retrieve notification history
"""
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException

from models.schemas import (
    NotificationSendRequest,
    NotificationRecord,
    NotificationHistoryResponse,
)
from services import databricks_client as db

router = APIRouter(prefix="/notifications", tags=["Notifications"])


def _dispatch_notification(channel: str, patient_id: str, message: str) -> str:
    """
    Stub for actual dispatch logic.
    Replace with Firebase FCM / Twilio / AWS SNS calls as needed.
    """
    # In production, invoke the appropriate SDK here.
    print(f"[NOTIFY] channel={channel} patient={patient_id} msg={message}")
    return "sent"


@router.post(
    "/send",
    response_model=NotificationRecord,
    summary="Send a notification to a patient",
)
async def send_notification(request: NotificationSendRequest):
    """
    Send an SMS, push, or email notification to a patient.
    Persists the notification to Delta Lake (or in-memory fallback).
    """
    status = _dispatch_notification(request.channel, request.patient_id, request.message)

    record = NotificationRecord(
        notification_id=str(uuid.uuid4())[:8].upper(),
        patient_id=request.patient_id,
        message=request.message,
        channel=request.channel,
        status=status,
        sent_at=datetime.utcnow(),
    )

    db.save_notification(record.model_dump())
    return record


@router.get(
    "/{patient_id}",
    response_model=NotificationHistoryResponse,
    summary="Get notification history for a patient",
)
async def get_notification_history(patient_id: str):
    """Retrieve all notifications sent to a patient."""
    records_raw = db.get_notifications(patient_id.upper())
    records = []
    for r in records_raw:
        if isinstance(r.get("sent_at"), str):
            r["sent_at"] = datetime.fromisoformat(r["sent_at"])
        records.append(NotificationRecord(**r))
    return NotificationHistoryResponse(patient_id=patient_id.upper(), notifications=records)
