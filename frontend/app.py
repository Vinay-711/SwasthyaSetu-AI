"""
SwasthyaSetu AI — Streamlit Multi-Page Application
Main entry point with dashboard overview.
"""
import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(
    page_title="SwasthyaSetu AI",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');

html, body, [class*="css"]  {
    font-family: 'Inter', sans-serif;
}

/* Sidebar gradient */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
}
[data-testid="stSidebar"] * { color: #e0e0ff !important; }

/* Main background */
.stApp { background: #0a0a1a; color: #e0e0ff; }

/* Metric cards */
.metric-card {
    background: linear-gradient(135deg, #1a1a3e 0%, #2d2d6b 100%);
    border: 1px solid #4040a0;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: transform 0.2s;
}
.metric-card:hover { transform: translateY(-4px); }
.metric-card h2 { font-size: 2.4rem; font-weight: 800; color: #7c7cff; margin: 0; }
.metric-card p  { color: #a0a0cc; margin: 4px 0 0; font-size: 0.9rem; }

/* Feature tiles */
.feature-tile {
    background: linear-gradient(135deg, #1e1e4a 0%, #2a2a60 100%);
    border: 1px solid #3535a0;
    border-radius: 12px;
    padding: 20px;
    height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
.feature-tile h3 { font-size: 1.1rem; color: #9090ff; margin-bottom: 6px; }
.feature-tile p  { color: #8080bb; font-size: 0.82rem; margin: 0; }

/* Buttons */
.stButton > button {
    background: linear-gradient(90deg, #4040ff, #7070ff);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 10px 24px;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* Headers */
h1 { color: #7c7cff !important; }
h2 { color: #9090ff !important; }
h3 { color: #a0a0ff !important; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 SwasthyaSetu AI")
    st.markdown("*Bridging healthcare & technology*")
    st.divider()

    # Backend health check
    try:
        r = requests.get(f"{API}/health", timeout=3)
        if r.status_code == 200:
            st.success("✅ Backend Online")
        else:
            st.warning("⚠️ Backend Unreachable")
    except Exception:
        st.error("❌ Backend Offline")

    st.divider()
    st.caption("Navigate using the pages menu above ↑")

# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;padding:40px 0 20px;">
    <h1 style="font-size:3rem;font-weight:800;background:linear-gradient(90deg,#7c7cff,#ff7cff);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        🏥 SwasthyaSetu AI
    </h1>
    <p style="color:#8080bb;font-size:1.1rem;margin-top:8px;">
        AI-Powered Healthcare Intelligence Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ── Metrics ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
metrics = [
    ("🪪", "Health IDs", "QR-based identity"),
    ("🎤", "Voice Triage", "Speech symptom input"),
    ("📄", "OCR Rx", "Prescription reader"),
    ("⚠️", "Risk Engine", "Occupational ML model"),
]
for col, (icon, title, desc) in zip([c1, c2, c3, c4], metrics):
    col.markdown(f"""
    <div class="metric-card">
        <h2>{icon}</h2>
        <p><strong>{title}</strong></p>
        <p>{desc}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Feature grid ───────────────────────────────────────────────────────────
st.markdown("### 🚀 Platform Features")
f1, f2, f3 = st.columns(3)

features = [
    ("🪪 QR Health ID", "Generate unique patient IDs with QR codes. Instant lookup & verification."),
    ("🎤 Voice Symptoms", "Speak symptoms in any language (Google STT). Get instant triage & dept routing."),
    ("📄 Prescription OCR", "Upload a photo of any prescription. Extracts medicines, dosage, doctor details."),
    ("⚠️ Risk Prediction", "Enter occupation + symptoms → ML model (MLflow/heuristic) predicts health risk."),
    ("🔔 Notifications", "Send SMS/push/email reminders. Full notification history per patient."),
    ("📊 Databricks", "Delta Lake for patient data, Spark ETL pipelines, MLflow model registry."),
]
cols = [f1, f2, f3, f1, f2, f3]
for col, (title, desc) in zip(cols, features):
    col.markdown(f"""
    <div class="feature-tile">
        <h3>{title}</h3>
        <p>{desc}</p>
    </div>
    <br>""", unsafe_allow_html=True)

# ── Quick access buttons ───────────────────────────────────────────────────
st.markdown("### ⚡ Quick Actions")
b1, b2, b3, b4, b5 = st.columns(5)
b1.page_link("pages/1_health_id.py",        label="🪪 Health ID",      icon="🪪")
b2.page_link("pages/2_voice_symptoms.py",   label="🎤 Symptoms",       icon="🎤")
b3.page_link("pages/3_ocr_prescription.py", label="📄 OCR",            icon="📄")
b4.page_link("pages/4_risk_prediction.py",  label="⚠️ Risk",           icon="⚠️")
b5.page_link("pages/5_notifications.py",    label="🔔 Notifications",  icon="🔔")

st.markdown("---")
st.caption("SwasthyaSetu AI v1.0 · Built with FastAPI + Streamlit + Databricks")
