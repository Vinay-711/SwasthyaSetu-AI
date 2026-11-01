"""
services/symptom_service.py
============================
All business logic for symptom parsing and voice transcription.
API routers must call parse_symptoms() and transcribe_audio() — no NLP logic in routers.
"""
import re
import os
import tempfile
from typing import List, Dict, Any

# ── Domain knowledge ───────────────────────────────────────────────────────

DEPARTMENT_MAP: Dict[str, str] = {
    "fever":       "General Medicine",
    "cough":       "Pulmonology",
    "chest pain":  "Cardiology",
    "heart":       "Cardiology",
    "breathless":  "Pulmonology",
    "wheezing":    "Pulmonology",
    "back pain":   "Orthopedics",
    "joint pain":  "Orthopedics",
    "skin rash":   "Dermatology",
    "itching":     "Dermatology",
    "headache":    "Neurology",
    "dizziness":   "Neurology",
    "stomach":     "Gastroenterology",
    "vomiting":    "Gastroenterology",
    "diarrhea":    "Gastroenterology",
    "eye":         "Ophthalmology",
    "teeth":       "Dentistry",
}

SEVERE_WORDS   = {"severe", "unbearable", "critical", "chest pain", "breathless", "unconscious"}
MODERATE_WORDS = {"moderate", "persistent", "chronic", "frequent"}


# ── Public interface ───────────────────────────────────────────────────────

def parse_symptoms(text: str) -> Dict[str, Any]:
    """
    Parse a free-text symptom description into structured output.

    Returns:
        Dict with keys: symptoms (list[str]), severity (str), suggested_department (str).
    """
    text_lower = text.lower()

    # Tokenise on common delimiters
    raw = re.split(r"[,;.\n]| and | with ", text_lower)
    symptoms: List[str] = [s.strip() for s in raw if s.strip()]

    # Department routing
    department = "General Medicine"
    for keyword, dept in DEPARTMENT_MAP.items():
        if keyword in text_lower:
            department = dept
            break

    # Severity scoring
    if any(w in text_lower for w in SEVERE_WORDS):
        severity = "high"
    elif any(w in text_lower for w in MODERATE_WORDS) or len(symptoms) >= 3:
        severity = "medium"
    else:
        severity = "low"

    return {
        "symptoms":             symptoms,
        "severity":             severity,
        "suggested_department": department,
    }


def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> str:
    """
    Transcribe an audio file to text using Google SpeechRecognition.

    Returns the transcribed string, or an error message on failure.
    Never raises — returns a human-readable fallback string instead.
    """
    suffix = os.path.splitext(filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    transcription = ""
    wav_path = tmp_path
    try:
        import speech_recognition as sr  # type: ignore[import-untyped]

        if suffix.lower() != ".wav":
            from pydub import AudioSegment  # type: ignore[import-untyped]
            seg = AudioSegment.from_file(tmp_path)
            wav_path = os.path.splitext(tmp_path)[0] + ".wav"
            seg.export(wav_path, format="wav")

        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            transcription = recognizer.recognize_google(audio_data)

    except Exception as exc:
        transcription = (
            f"[Transcription unavailable: {exc}] "
            "— Upload a valid WAV file and ensure internet access."
        )
    finally:
        for path in {tmp_path, wav_path}:
            try:
                os.unlink(path)
            except OSError:
                pass

    return transcription
