# 🏥 SwasthyaSetu AI

> **AI-Powered Healthcare Intelligence Platform**  
> QR Health ID · Voice Symptom Triage · Prescription OCR · Occupational Risk Prediction · Notifications

---

## 🌟 Features

| Feature | Tech | Description |
|---|---|---|
| 🪪 **QR Health ID** | qrcode + FastAPI | Unique patient IDs with scannable QR codes |
| 🎤 **Voice Symptoms** | SpeechRecognition | Audio → transcription → structured symptom analysis |
| 📄 **Prescription OCR** | pytesseract | Extract medicines, dosages, and doctor info from images |
| ⚠️ **Risk Prediction** | MLflow + scikit-learn | Occupational health risk scoring with ML model |
| 🔔 **Notifications** | Stub (FCM/Twilio ready) | Send & track SMS/push/email patient notifications |
| 📊 **Databricks** | Delta Lake + Spark + MLflow | Scalable data layer and model registry |

---

## 🏗 Project Structure

```
Swastya_Setu_DB/
├── backend/                 # FastAPI backend
│   ├── main.py              # Application entry point
│   ├── requirements.txt
│   ├── models/schemas.py    # Pydantic models
│   ├── routers/
│   │   ├── health_id.py     # QR health ID endpoints
│   │   ├── symptoms.py      # Voice + text symptom analysis
│   │   ├── ocr.py           # Prescription OCR
│   │   ├── risk.py          # Risk prediction
│   │   └── notifications.py # Notification system
│   └── services/
│       ├── databricks_client.py  # Delta Lake integration
│       └── mlflow_client.py      # MLflow model serving
│
├── frontend/                # Streamlit frontend
│   ├── app.py               # Main dashboard
│   ├── requirements.txt
│   └── pages/
│       ├── 1_health_id.py
│       ├── 2_voice_symptoms.py
│       ├── 3_ocr_prescription.py
│       ├── 4_risk_prediction.py
│       └── 5_notifications.py
│
├── databricks/              # Databricks artifacts
│   ├── schemas/
│   │   ├── patients.sql
│   │   └── notifications.sql
│   ├── notebooks/
│   │   └── etl_pipeline.py
│   └── mlflow/
│       └── train_risk_model.py
│
├── .env.example             # Environment variable template
├── .gitignore
└── run.sh                   # One-click startup script
```

---

## 🚀 Quick Start

### 1. Clone and configure

```bash
git clone https://github.com/Vinay-711/SwasthyaSetu-AI.git
cd SwasthyaSetu-AI
cp .env.example .env
# Edit .env with your Databricks/MLflow credentials (optional for local demo)
```

### 2. Run the application

```bash
chmod +x run.sh
./run.sh --install   # First run: installs dependencies
./run.sh             # Subsequent runs
```

This starts:
- **Backend** → http://localhost:8000
- **Frontend** → http://localhost:8501
- **API Docs** → http://localhost:8000/docs

### 3. Manual setup (alternative)

```bash
# Create venv and install
python3 -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt -r frontend/requirements.txt

# Backend
cd backend && uvicorn main:app --reload --port 8000 &

# Frontend
cd ../frontend && streamlit run app.py --server.port 8501
```

---

## ⚙️ Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
|---|---|
| `DATABRICKS_HOST` | Databricks workspace URL |
| `DATABRICKS_TOKEN` | Personal access token |
| `MLFLOW_TRACKING_URI` | MLflow tracking server URI |
| `MLFLOW_MODEL_NAME` | Registered model name |
| `TWILIO_ACCOUNT_SID` | Twilio SID (for SMS) |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Firebase FCM (for push) |

> **Note:** All features work without Databricks credentials — in-memory storage and heuristic models are used as fallback.

---

## 🧠 MLflow Model Training

Train and register the occupational risk model:

```bash
cd databricks/mlflow
python train_risk_model.py
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Backend health check |
| `POST` | `/health-id/create` | Create patient health ID + QR |
| `GET` | `/health-id/{id}` | Get patient record |
| `GET` | `/health-id/{id}/qr` | Download QR code PNG |
| `POST` | `/symptoms/text` | Parse symptoms from text |
| `POST` | `/symptoms/voice` | Transcribe audio + parse symptoms |
| `POST` | `/ocr/prescription` | OCR a prescription image |
| `POST` | `/risk/predict` | Predict occupational health risk |
| `POST` | `/notifications/send` | Send notification to patient |
| `GET` | `/notifications/{id}` | Get notification history |

Full interactive docs at → http://localhost:8000/docs

---

## 🛠 Tech Stack

- **Backend**: Python · FastAPI · Uvicorn · Pydantic
- **Frontend**: Streamlit · Plotly
- **ML/AI**: scikit-learn · MLflow · SpeechRecognition · pytesseract
- **Data**: Databricks · Delta Lake · Apache Spark
- **QR**: qrcode · Pillow

---

*Built for SwasthyaSetu AI · March 2026*

## Reproducible setup notes

Use the cloned repository directory instead of the author-specific absolute path shown in older examples. For a manual setup, start the API and Streamlit in separate terminals so a failed backend is visible:

```sh
# Terminal 1, from the repository root after installing dependencies
cd backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

```sh
# Terminal 2, from the repository root with the same environment active
cd frontend
python -m streamlit run app.py --server.port 8501
```

Fallback heuristics, OCR output and occupational risk estimates are research demonstrations, not validated diagnoses. Provider notification stubs do not prove that a message was delivered. Use synthetic patient records and check the model/provider configuration in [backend/services](backend/services) before evaluating results.

### Audio-file cleanup regression tests

Run `python -m unittest discover -s tests -p test_transcription_cleanup.py`.
The standard-library suite uses synthetic bytes and mocked conversion/recognition,
with no microphone, network, or patient data. It checks removal of both the uploaded
temporary file and converted WAV on success, recognition failure, and partial export
failure. The tests establish cleanup behavior, not transcription or medical accuracy.
