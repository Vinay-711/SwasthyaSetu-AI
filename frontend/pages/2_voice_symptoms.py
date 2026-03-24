"""
Page 2: Voice-based Symptom Input
"""
import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(page_title="Voice Symptoms · SwasthyaSetu", page_icon="🎤", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0a1a;color:#e0e0ff;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#302b63,#24243e);}
[data-testid="stSidebar"] *{color:#e0e0ff!important;}
h1,h2,h3{color:#7c7cff!important;}
.stButton>button{background:linear-gradient(90deg,#4040ff,#7070ff);color:white;border:none;border-radius:8px;font-weight:600;}
.stTextArea textarea{background:#1a1a3a!important;color:#e0e0ff!important;border:1px solid #3535a0!important;}
.risk-badge{display:inline-block;padding:6px 16px;border-radius:20px;font-weight:700;font-size:1rem;}
</style>
""", unsafe_allow_html=True)

st.title("🎤 Voice Symptom Input")
st.markdown("Describe symptoms via voice (upload WAV/MP3) or type them directly.")

SEVERITY_COLORS = {"low": "#22c55e", "medium": "#f59e0b", "high": "#ef4444"}

tab_voice, tab_text = st.tabs(["🎙️ Voice Upload", "⌨️ Text Input"])

# ── Voice Tab ──────────────────────────────────────────────────────────────
with tab_voice:
    st.info("📌 Upload a WAV or MP3 audio file where the patient describes their symptoms.")
    uploaded_audio = st.file_uploader("Upload Audio File", type=["wav", "mp3", "ogg", "m4a"])
    patient_id_v = st.text_input("Patient ID (optional)", key="v_pid")

    if st.button("🎤 Transcribe & Analyse", use_container_width=True, key="v_btn"):
        if not uploaded_audio:
            st.warning("Please upload an audio file.")
        else:
            with st.spinner("Transcribing audio…"):
                try:
                    files = {"audio": (uploaded_audio.name, uploaded_audio.getvalue(), uploaded_audio.type)}
                    data = {"patient_id": patient_id_v} if patient_id_v else {}
                    r = requests.post(f"{API}/symptoms/voice", files=files, data=data, timeout=30)
                    r.raise_for_status()
                    result = r.json()

                    st.subheader("📋 Analysis Result")
                    if result.get("transcription"):
                        st.markdown(f"**Transcription:** _{result['transcription']}_")

                    c1, c2 = st.columns(2)
                    color = SEVERITY_COLORS.get(result["severity"], "#888")
                    c1.markdown(f"**Severity:** <span class='risk-badge' style='background:{color};color:white;'>{result['severity'].upper()}</span>", unsafe_allow_html=True)
                    c2.markdown(f"**Suggested Dept:** 🏥 {result['suggested_department']}")

                    st.markdown("**Detected Symptoms:**")
                    for s in result["symptoms"]:
                        st.markdown(f"- {s}")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Text Tab ───────────────────────────────────────────────────────────────
with tab_text:
    symptoms_text = st.text_area(
        "Describe symptoms",
        placeholder="e.g. fever for 3 days, severe cough, chest pain, fatigue",
        height=120,
    )
    patient_id_t = st.text_input("Patient ID (optional)", key="t_pid")

    if st.button("🔍 Analyse Symptoms", use_container_width=True, key="t_btn"):
        if not symptoms_text.strip():
            st.warning("Please enter some symptoms.")
        else:
            with st.spinner("Analysing…"):
                try:
                    payload = {"symptoms": symptoms_text, "patient_id": patient_id_t or None}
                    r = requests.post(f"{API}/symptoms/text", json=payload, timeout=10)
                    r.raise_for_status()
                    result = r.json()

                    st.subheader("📋 Analysis Result")
                    c1, c2 = st.columns(2)
                    color = SEVERITY_COLORS.get(result["severity"], "#888")
                    c1.markdown(f"**Severity:** <span class='risk-badge' style='background:{color};color:white;'>{result['severity'].upper()}</span>", unsafe_allow_html=True)
                    c2.markdown(f"**Suggested Dept:** 🏥 {result['suggested_department']}")

                    st.markdown("**Detected Symptoms:**")
                    for s in result["symptoms"]:
                        st.markdown(f"- {s}")
                except Exception as e:
                    st.error(f"Error: {e}")
