"""
Router: QR-based Health ID system.
POST /health-id/create   — create patient + generate QR code
GET  /health-id/{id}     — retrieve patient record
GET  /health-id/{id}/qr  — regenerate QR code image
"""
import io
import base64
import qrcode
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from datetime import datetime

from models.schemas import PatientCreate, PatientResponse
from services import databricks_client as db

router = APIRouter(prefix="/health-id", tags=["Health ID"])


def _generate_qr_base64(patient_id: str) -> str:
    """Generate a QR code PNG and return it as a base64 string."""
    qr = qrcode.QRCode(version=1, box_size=8, border=4)
    qr.add_data(f"swasthyasetu://patient/{patient_id}")
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a2e", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


@router.post("/create", response_model=PatientResponse, summary="Create patient health ID")
async def create_health_id(patient: PatientCreate):
    """
    Create a new patient record and generate a unique QR-coded Health ID.
    Returns patient details along with a base64-encoded QR code PNG.
    """
    record = db.create_patient(patient.model_dump())
    record["qr_code_base64"] = _generate_qr_base64(record["patient_id"])
    record["created_at"] = datetime.fromisoformat(record["created_at"])
    return PatientResponse(**record)


@router.get("/{patient_id}", response_model=PatientResponse, summary="Get patient by Health ID")
async def get_health_id(patient_id: str):
    """Retrieve a patient record by their Health ID."""
    record = db.get_patient(patient_id.upper())
    if not record:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")
    record["created_at"] = datetime.fromisoformat(record["created_at"])
    return PatientResponse(**record)


@router.get("/{patient_id}/qr", response_class=Response, summary="Download QR code PNG")
async def get_qr_image(patient_id: str):
    """Return a raw PNG QR code image for the given Health ID."""
    record = db.get_patient(patient_id.upper())
    if not record:
        raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")

    qr_b64 = _generate_qr_base64(patient_id.upper())
    img_bytes = base64.b64decode(qr_b64)
    return Response(
        content=img_bytes,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=health_id_{patient_id}.png"},
    )
