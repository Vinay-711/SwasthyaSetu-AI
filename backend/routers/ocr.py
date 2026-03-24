"""
Router: OCR for prescription images.
POST /ocr/prescription

All business logic is in services/ocr_service.py.
This router is a thin HTTP adapter only.
"""
from fastapi import APIRouter, UploadFile, File, HTTPException

from models.schemas import PrescriptionOCRResponse
from services.ocr_service import extract_prescription

router = APIRouter(prefix="/ocr", tags=["OCR"])


@router.post(
    "/prescription",
    response_model=PrescriptionOCRResponse,
    summary="Extract prescription data via OCR",
)
async def ocr_prescription(
    image: UploadFile = File(..., description="Prescription image (JPG, PNG, TIFF)"),
):
    """
    Upload a prescription image and extract structured data.
    All OCR and parsing logic is delegated to ocr_service.extract_prescription().
    """
    try:
        content = await image.read()
        result = extract_prescription(
            image_bytes=content,
            filename=image.filename or "prescription.jpg",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    return PrescriptionOCRResponse(**result)
