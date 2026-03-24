"""
Page 1: QR-based Health ID System
"""
import base64
import streamlit as st
import requests
from PIL import Image
import io

API = "http://localhost:8000"

st.set_page_config(page_title="Health ID · SwasthyaSetu", page_icon="🪪", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0a1a;color:#e0e0ff;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#302b63,#24243e);}
[data-testid="stSidebar"] *{color:#e0e0ff!important;}
h1,h2,h3{color:#7c7cff!important;}
.stButton>button{background:linear-gradient(90deg,#4040ff,#7070ff);color:white;border:none;border-radius:8px;font-weight:600;}
.stTextInput>div>input,.stNumberInput>div>input,.stSelectbox>div{background:#1a1a3a!important;color:#e0e0ff!important;border:1px solid #3535a0!important;}
</style>
""", unsafe_allow_html=True)

st.title("🪪 QR Health ID System")
st.markdown("Create patient health IDs and generate scannable QR codes.")

tab_create, tab_lookup = st.tabs(["➕ Create Health ID", "🔍 Lookup Patient"])

# ── Create ─────────────────────────────────────────────────────────────────
with tab_create:
    with st.form("create_form"):
        st.subheader("Patient Information")
        col1, col2 = st.columns(2)
        name       = col1.text_input("Full Name *", placeholder="Ravi Kumar")
        age        = col2.number_input("Age *", min_value=0, max_value=150, value=30)
        gender     = col1.selectbox("Gender *", ["M", "F", "Other"])
        blood_group = col2.selectbox("Blood Group", ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        phone      = col1.text_input("Phone", placeholder="+91-9876543210")
        occupation = col2.text_input("Occupation", placeholder="Construction Worker")
        region     = col1.text_input("Region / District", placeholder="Rajasthan")
        submitted  = st.form_submit_button("🪪 Generate Health ID", use_container_width=True)

    if submitted:
        if not name:
            st.error("Please enter the patient's name.")
        else:
            with st.spinner("Creating Health ID…"):
                payload = {
                    "name": name, "age": int(age), "gender": gender,
                    "blood_group": blood_group or None,
                    "phone": phone or None,
                    "occupation": occupation or None,
                    "region": region or None,
                }
                try:
                    r = requests.post(f"{API}/health-id/create", json=payload, timeout=10)
                    r.raise_for_status()
                    data = r.json()

                    st.success(f"✅ Health ID Created: **{data['patient_id']}**")
                    col_info, col_qr = st.columns([2, 1])
                    with col_info:
                        st.markdown(f"**Name:** {data['name']}")
                        st.markdown(f"**Age / Gender:** {data['age']} / {data['gender']}")
                        st.markdown(f"**Blood Group:** {data.get('blood_group') or '—'}")
                        st.markdown(f"**Occupation:** {data.get('occupation') or '—'}")
                        st.markdown(f"**Region:** {data.get('region') or '—'}")
                    with col_qr:
                        if data.get("qr_code_base64"):
                            img_bytes = base64.b64decode(data["qr_code_base64"])
                            st.image(img_bytes, caption="Scan to identify patient", width=200)
                            st.download_button(
                                "⬇️ Download QR",
                                data=img_bytes,
                                file_name=f"health_id_{data['patient_id']}.png",
                                mime="image/png",
                            )
                except Exception as e:
                    st.error(f"Error: {e}")

# ── Lookup ─────────────────────────────────────────────────────────────────
with tab_lookup:
    patient_id_input = st.text_input("Enter Health ID", placeholder="A1B2C3")
    if st.button("🔍 Lookup", use_container_width=True):
        if not patient_id_input.strip():
            st.warning("Please enter a Health ID.")
        else:
            with st.spinner("Looking up patient…"):
                try:
                    r = requests.get(f"{API}/health-id/{patient_id_input.strip()}", timeout=10)
                    if r.status_code == 404:
                        st.error(f"No patient found with ID: **{patient_id_input}**")
                    else:
                        r.raise_for_status()
                        data = r.json()
                        st.success(f"Patient Found: **{data['name']}**")
                        st.json(data)
                        # Show QR
                        qr_r = requests.get(f"{API}/health-id/{patient_id_input}/qr", timeout=10)
                        if qr_r.status_code == 200:
                            st.image(qr_r.content, caption="Patient QR Code", width=180)
                except Exception as e:
                    st.error(f"Error: {e}")
