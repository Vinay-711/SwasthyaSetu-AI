"""
SwasthyaSetu AI — FastAPI Backend Entry Point

Registers all routers and configures the application.
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from routers import health_id, symptoms, ocr, risk, notifications

app = FastAPI(
    title="SwasthyaSetu AI",
    description=(
        "AI-powered healthcare platform with QR Health ID, Voice Symptom Input, "
        "Prescription OCR, Occupational Risk Prediction, and Notifications."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS — allow Streamlit frontend ───────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────
app.include_router(health_id.router)
app.include_router(symptoms.router)
app.include_router(ocr.router)
app.include_router(risk.router)
app.include_router(notifications.router)


# ── Health check ──────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "SwasthyaSetu AI Backend"}


@app.get("/", tags=["System"])
async def root():
    return {
        "service": "SwasthyaSetu AI",
        "version": "1.0.0",
        "docs": "/docs",
    }
