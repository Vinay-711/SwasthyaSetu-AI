"""
Router: Voice & text-based symptom input.
POST /symptoms/text   — structured text symptom parsing
POST /symptoms/voice  — audio file → transcription → symptom parsing

All business logic is in services/symptom_service.py.
This router is a thin HTTP adapter only.
"""
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form

from models.schemas import TextSymptomsRequest, SymptomsResponse
from services.symptom_service import parse_symptoms, transcribe_audio

router = APIRouter(prefix="/symptoms", tags=["Symptoms"])


@router.post("/text", response_model=SymptomsResponse, summary="Parse symptoms from text")
async def analyze_text_symptoms(request: TextSymptomsRequest):
    """
    Accept a free-text symptom description and return structured analysis.
    Delegates entirely to symptom_service.parse_symptoms().
    """
    result = parse_symptoms(request.symptoms)
    return SymptomsResponse(**result)


@router.post("/voice", response_model=SymptomsResponse, summary="Transcribe voice and parse symptoms")
async def analyze_voice_symptoms(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, OGG)"),
    patient_id: Optional[str] = Form(None),
):
    """
    Accept an audio file, transcribe it, then parse the symptoms.
    Delegates to symptom_service.transcribe_audio() + symptom_service.parse_symptoms().
    """
    audio_bytes = await audio.read()

    transcription = transcribe_audio(
        audio_bytes=audio_bytes,
        filename=audio.filename or "audio.wav",
    )

    result = parse_symptoms(transcription)
    return SymptomsResponse(transcription=transcription, **result)
