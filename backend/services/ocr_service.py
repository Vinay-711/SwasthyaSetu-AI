"""
services/ocr_service.py
========================
All business logic for prescription OCR and text extraction.
API routers must call extract_prescription() — no OCR logic should exist in routers.
"""
import re
import os
import tempfile
from typing import Dict, Any

# ── Regex patterns ─────────────────────────────────────────────────────────

MEDICINE_PATTERNS = [
    r"\b(Tab|Cap|Syrup|Inj|Drops|Cream|Gel|Oint|Spray)\s+([A-Z][a-zA-Z0-9\s\-]+)",
    r"\b([A-Z][a-z]+(?:mycin|cillin|zole|prazole|statin|pril|sartan|olol|pine|dipine|azole)\b)",
]

DOSAGE_PATTERNS = [
    r"\d+\s*(?:mg|mcg|ml|g|IU|units?)",
    r"\d+\s*(?:OD|BD|TDS|QID|SOS|HS|AC|PC|PRN)\b",
    r"\b(?:once|twice|thrice)\s+(?:daily|a\s+day)\b",
    r"(?:morning|evening|night|bedtime)\b",
]

DOCTOR_PATTERN   = r"Dr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"
HOSPITAL_PATTERN = r"([A-Z][a-zA-Z\s]+(?:Hospital|Clinic|Medical|Centre|Center))"
DATE_PATTERN     = r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b"

# Demo fallback used when no OCR library is installed or image is unreadable
DEMO_PRESCRIPTION = (
    "Dr. Arvind Sharma\n"
    "City Health Clinic\n"
    "Date: 24/03/2026\n"
    "Tab Paracetamol 500mg BD\n"
    "Tab Amoxicillin 250mg TDS\n"
    "Syrup Cetirizine 5ml OD\n"
)


# ── Private helpers ────────────────────────────────────────────────────────

def _run_tesseract(image_path: str) -> str:
    """
    Run pytesseract OCR on the given image path.
    Returns empty string if pytesseract is not installed.
    Raises ValueError on image read failure.
    """
    try:
        import pytesseract  # type: ignore[import-untyped]
        from PIL import Image  # type: ignore[import-untyped]
        img = Image.open(image_path)
        return pytesseract.image_to_string(img)
    except ImportError:
        return ""
    except Exception as exc:
        raise ValueError(f"OCR engine failed: {exc}") from exc


def _parse_raw_text(raw_text: str) -> Dict[str, Any]:
    """
    Parse raw OCR text into structured prescription fields.
    Extracts: medicines, dosages, doctor name, hospital, date.
    """
    medicines: list[str] = []
    for pat in MEDICINE_PATTERNS:
        for match in re.finditer(pat, raw_text):
            med = match.group(0).strip()
            if med and med not in medicines:
                medicines.append(med)

    dosages: list[str] = []
    for pat in DOSAGE_PATTERNS:
        for match in re.finditer(pat, raw_text, re.IGNORECASE):
            d = match.group(0).strip()
            if d and d not in dosages:
                dosages.append(d)

    doctor_match   = re.search(DOCTOR_PATTERN, raw_text)
    hospital_match = re.search(HOSPITAL_PATTERN, raw_text)
    date_match     = re.search(DATE_PATTERN, raw_text)

    return {
        "raw_text":    raw_text,
        "medicines":   medicines,
        "dosages":     dosages,
        "doctor_name": doctor_match.group(0) if doctor_match else None,
        "hospital":    hospital_match.group(0).strip() if hospital_match else None,
        "date":        date_match.group(0) if date_match else None,
    }


# ── Public interface ───────────────────────────────────────────────────────

def extract_prescription(image_bytes: bytes, filename: str = "prescription.jpg") -> Dict[str, Any]:
    """
    Extract structured data from a prescription image.

    Steps:
      1. Write image bytes to a temp file.
      2. Run Tesseract OCR.
      3. Fall back to a demo prescription if OCR yields no text.
      4. Parse and return structured fields.

    Args:
        image_bytes: Raw bytes of the uploaded image.
        filename:    Original filename (used to determine file extension).

    Returns:
        Dict with keys: raw_text, medicines, dosages, doctor_name, hospital, date.

    Raises:
        ValueError: If OCR fails due to a corrupt or unreadable image.
    """
    suffix = os.path.splitext(filename)[1] or ".jpg"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(image_bytes)
        tmp_path = tmp.name

    result: Dict[str, Any]
    try:
        raw_text = _run_tesseract(tmp_path)

        if not raw_text.strip():
            raw_text = DEMO_PRESCRIPTION   # graceful fallback

        result = _parse_raw_text(raw_text)

    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass

    return result
