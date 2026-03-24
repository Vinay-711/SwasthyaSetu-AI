"""
Page 4: Occupational Risk Prediction
"""
import streamlit as st
import requests
import plotly.graph_objects as go

API = "http://localhost:8000"

st.set_page_config(page_title="Risk Prediction · SwasthyaSetu", page_icon="⚠️", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0a1a;color:#e0e0ff;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#302b63,#24243e);}
[data-testid="stSidebar"] *{color:#e0e0ff!important;}
h1,h2,h3{color:#7c7cff!important;}
.stButton>button{background:linear-gradient(90deg,#4040ff,#7070ff);color:white;border:none;border-radius:8px;font-weight:600;}
.stTextInput>div>input,.stNumberInput>div>input{background:#1a1a3a!important;color:#e0e0ff!important;border:1px solid #3535a0!important;}
.risk-card{border-radius:16px;padding:24px;text-align:center;margin:16px 0;}
</style>
""", unsafe_allow_html=True)

st.title("⚠️ Occupational Risk Prediction")
st.markdown("Assess health risk based on occupation, demographics, and symptoms using ML model.")

LEVEL_CONFIG = {
    "low":      {"color": "#22c55e", "emoji": "🟢", "bar_color": "green"},
    "medium":   {"color": "#f59e0b", "emoji": "🟡", "bar_color": "yellow"},
    "high":     {"color": "#ef4444", "emoji": "🔴", "bar_color": "red"},
    "critical": {"color": "#7c3aed", "emoji": "🚨", "bar_color": "purple"},
}

COMMON_OCCUPATIONS = [
    "Select…",
    "Construction Worker", "Miner", "Factory Worker", "Farmer",
    "Welder", "Painter", "Textile Worker", "Truck Driver",
    "Healthcare Worker", "Teacher", "Office Worker", "Other",
]

COMMON_SYMPTOMS = [
    "cough", "fever", "fatigue", "breathlessness", "chest pain",
    "back pain", "joint pain", "skin rash", "headache", "dizziness",
    "eye irritation", "hearing loss", "nausea", "vomiting",
]

col_form, col_result = st.columns([1, 1])

with col_form:
    st.subheader("📝 Patient Details")
    occupation = st.selectbox("Occupation *", COMMON_OCCUPATIONS)
    custom_occ = ""
    if occupation == "Other":
        custom_occ = st.text_input("Specify occupation")

    age    = st.number_input("Age *", min_value=1, max_value=120, value=35)
    gender = st.selectbox("Gender", ["M", "F", "Other"])
    region = st.text_input("Region / State", placeholder="e.g. Punjab, Odisha")

    st.markdown("**Symptoms** (select all that apply)")
    selected_symptoms = st.multiselect("Symptoms", COMMON_SYMPTOMS)
    custom_symptom = st.text_input("Add custom symptom", placeholder="e.g. chronic fatigue")
    if custom_symptom:
        selected_symptoms.append(custom_symptom)

    predict_btn = st.button("⚠️ Predict Risk", use_container_width=True)

with col_result:
    if predict_btn:
        occ = custom_occ if occupation == "Other" else occupation
        if not occ or occ == "Select…":
            st.warning("Please select an occupation.")
        elif not selected_symptoms:
            st.warning("Please select at least one symptom.")
        else:
            with st.spinner("Running risk model…"):
                try:
                    payload = {
                        "occupation": occ,
                        "age": int(age),
                        "gender": gender,
                        "region": region,
                        "symptoms": selected_symptoms,
                    }
                    r = requests.post(f"{API}/risk/predict", json=payload, timeout=15)
                    r.raise_for_status()
                    result = r.json()

                    level = result["risk_level"]
                    cfg   = LEVEL_CONFIG.get(level, LEVEL_CONFIG["medium"])
                    score = result["risk_score"]

                    st.subheader("📊 Risk Assessment")

                    # Gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=round(score * 100, 1),
                        domain={"x": [0, 1], "y": [0, 1]},
                        title={"text": f"Risk Score — {cfg['emoji']} {level.upper()}", "font": {"color": "#e0e0ff"}},
                        gauge={
                            "axis": {"range": [0, 100], "tickcolor": "#8080bb"},
                            "bar":  {"color": cfg["color"]},
                            "bgcolor": "#1a1a3a",
                            "steps": [
                                {"range": [0, 30],  "color": "#1a3a1a"},
                                {"range": [30, 55], "color": "#3a3010"},
                                {"range": [55, 75], "color": "#3a1010"},
                                {"range": [75, 100],"color": "#2a0a3a"},
                            ],
                        },
                        number={"suffix": "%", "font": {"color": cfg["color"]}},
                    ))
                    fig.update_layout(
                        paper_bgcolor="#0a0a1a",
                        font_color="#e0e0ff",
                        height=280,
                        margin=dict(t=40, b=20),
                    )
                    st.plotly_chart(fig, use_container_width=True)

                    st.markdown(f"**⚠️ Top Risk Factors:**")
                    for risk in result["top_risks"]:
                        st.markdown(f"- {risk}")

                    st.markdown(f"**✅ Recommendations:**")
                    for rec in result["recommendations"]:
                        st.success(rec)

                    st.caption(f"Model: `{result['model_version']}`")

                except Exception as e:
                    st.error(f"Prediction failed: {e}")
    else:
        st.info("Fill the form and click **Predict Risk** to see the assessment.")
