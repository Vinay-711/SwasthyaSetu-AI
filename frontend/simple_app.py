"""
SwasthyaSetu AI — Unified Simple Streamlit App
Provides a clean, single-page interface with tabs for all core features.
"""
import streamlit as st  # type: ignore[import-untyped]
import requests  # type: ignore[import-untyped]
import base64

API = "http://localhost:8000"

st.set_page_config(page_title="SwasthyaSetu AI", page_icon="🏥", layout="centered")

st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px;
        color: #e0e0ff;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏥 SwasthyaSetu AI")
st.caption("Simplified Healthcare Intelligence Dashboard")

# Check backend status silently
try:
    API_ONLINE = requests.get(f"{API}/health", timeout=2).status_code == 200
except:
    API_ONLINE = False

if not API_ONLINE:
    st.error("⚠️ Backend API is offline. Please start the backend server.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🪪 Health ID", "🩺 Symptoms", "📄 OCR", "⚠️ Risk Prediction"])

# --- TAB 1: HEALTH ID ---
with tab1:
    st.subheader("Generate QR Health ID")
    with st.form("health_id_form"):
        name = st.text_input("Patient Name")
        age = st.number_input("Age", min_value=1, max_value=120, value=30)
        gender = st.selectbox("Gender", ["M", "F", "Other"])
        blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        submit_id = st.form_submit_button("Create Health ID")
        
    if submit_id:
        with st.spinner("Generating..."):
            res = requests.post(f"{API}/health-id/create", json={
                "name": name, "age": age, "gender": gender, "blood_group": blood_group
            })
            if res.status_code == 200:
                data = res.json()
                st.success(f"Created! Your ID is **{data['patient_id']}**")
                qr_bytes = base64.b64decode(data['qr_code_base64'])
                st.image(qr_bytes, caption=f"Scan to view {name}'s records", width=250)
            else:
                st.error("Failed to create ID.")

# --- TAB 2: SYMPTOMS ---
with tab2:
    st.subheader("Symptom Input")
    st.info("Describe how you are feeling. The AI will parse your symptoms and suggest a department.")
    text_input = st.text_area("How are you feeling today?", placeholder="e.g. I have a severe headache and fever since yesterday.")
    
    if st.button("Analyze Symptoms", type="primary"):
        if text_input.strip():
            with st.spinner("Analyzing..."):
                res = requests.post(f"{API}/symptoms/text", json={"symptoms": text_input})
                if res.status_code == 200:
                    data = res.json()
                    c1, c2 = st.columns(2)
                    c1.metric("Recommended Dept.", data.get("recommended_department", "General"))
                    c2.metric("Severity Score", f"{data.get('severity_score', 0)}/10")
                    st.write("**Identified Symptoms:**")
                    st.write(", ".join(data.get("parsed_symptoms", [])))
                else:
                    st.error("Error analyzing symptoms.")
        else:
            st.warning("Please enter some symptoms first.")

# --- TAB 3: OCR PRESCRIPTION ---
with tab3:
    st.subheader("Prescription OCR")
    upload = st.file_uploader("Upload an image of a prescription", type=["png", "jpg", "jpeg"])
    
    if upload is not None:
        st.image(upload, width=300)
        if st.button("Extract Data"):
            with st.spinner("Extracting text via Tesseract OCR..."):
                files = {"image": (upload.name, upload.getvalue(), upload.type)}
                res = requests.post(f"{API}/ocr/prescription", files=files)
                if res.status_code == 200:
                    data = res.json()
                    st.success("Extraction Complete!")
                    st.write("### 💊 Medicines Found:")
                    for idx, med in enumerate(data.get("medicines", [])):
                        dosage = data.get("dosages", [])[idx] if idx < len(data.get("dosages", [])) else "Unknown dosage"
                        st.info(f"**{med}** — {dosage}")
                    
                    with st.expander("View Raw Output"):
                        st.json(data)
                else:
                    st.error("Failed to extract data.")

# --- TAB 4: RISK PREDICTION ---
with tab4:
    st.subheader("Occupational Risk Prediction")
    with st.form("risk_form"):
        r_age = st.number_input("Age", min_value=16, max_value=100, value=35)
        r_job = st.selectbox("Occupation", ["Office Worker", "Teacher", "Miner", "Construction Worker", "Healthcare", "Other"])
        r_symp = st.text_input("Current Symptoms (comma separated)", "cough, fatigue")
        submit_risk = st.form_submit_button("Calculate Risk")
        
    if submit_risk:
        with st.spinner("Calculating..."):
            symp_list = [s.strip() for s in r_symp.split(",") if s.strip()]
            res = requests.post(f"{API}/risk/predict", json={
                "age": r_age,
                "occupation": r_job,
                "symptoms": symp_list,
                "region": "Unknown"
            })
            if res.status_code == 200:
                data = res.json()
                risk_lvl = data.get("risk_level", "low").lower()
                
                if risk_lvl == "high":
                    st.error("🚨 HIGH OCCUPATIONAL RISK DETECTED")
                elif risk_lvl == "medium":
                    st.warning("⚠️ MEDIUM OCCUPATIONAL RISK DETECTED")
                else:
                    st.success("✅ LOW RISK")
                    
                st.write("**Next Steps:**")
                for rec in data.get("recommendations", []):
                    st.write(f"- {rec}")
            else:
                st.error("Prediction failed.")
