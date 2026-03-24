"""
Page 3: OCR for Prescription Images
"""
import streamlit as st
import requests

API = "http://localhost:8000"

st.set_page_config(page_title="Prescription OCR · SwasthyaSetu", page_icon="📄", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0a1a;color:#e0e0ff;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#302b63,#24243e);}
[data-testid="stSidebar"] *{color:#e0e0ff!important;}
h1,h2,h3{color:#7c7cff!important;}
.stButton>button{background:linear-gradient(90deg,#4040ff,#7070ff);color:white;border:none;border-radius:8px;font-weight:600;}
.result-box{background:#1a1a3a;border:1px solid #3535a0;border-radius:12px;padding:20px;margin-top:10px;}
code{background:#2a2a5a!important;color:#a0a0ff!important;border-radius:4px;padding:2px 6px;}
</style>
""", unsafe_allow_html=True)

st.title("📄 Prescription OCR")
st.markdown("Upload a prescription image to extract medicines, dosages, and doctor information.")

uploaded_img = st.file_uploader(
    "Upload Prescription Image",
    type=["jpg", "jpeg", "png", "bmp", "tiff", "pdf"],
    help="Supports JPG, PNG, BMP, TIFF formats",
)

col_img, col_result = st.columns([1, 1])

with col_img:
    if uploaded_img:
        st.image(uploaded_img, caption="Uploaded Prescription", use_column_width=True)

if st.button("🔍 Extract Prescription Data", use_container_width=True):
    if not uploaded_img:
        st.warning("Please upload a prescription image first.")
    else:
        with st.spinner("Running OCR…"):
            try:
                files = {"image": (uploaded_img.name, uploaded_img.getvalue(), uploaded_img.type)}
                r = requests.post(f"{API}/ocr/prescription", files=files, timeout=30)
                r.raise_for_status()
                data = r.json()

                with col_result:
                    st.subheader("📋 Extracted Information")

                    st.markdown("**👨‍⚕️ Doctor / Hospital**")
                    st.markdown(f"- Doctor: `{data.get('doctor_name') or 'Not detected'}`")
                    st.markdown(f"- Hospital: `{data.get('hospital') or 'Not detected'}`")
                    st.markdown(f"- Date: `{data.get('date') or 'Not detected'}`")

                    st.markdown("**💊 Medicines Detected**")
                    if data["medicines"]:
                        for m in data["medicines"]:
                            st.markdown(f"- `{m}`")
                    else:
                        st.info("No medicines detected — ensure image is clear.")

                    st.markdown("**📏 Dosages**")
                    if data["dosages"]:
                        for d in data["dosages"]:
                            st.markdown(f"- `{d}`")
                    else:
                        st.info("No dosage instructions detected.")

                    with st.expander("📝 Raw OCR Text"):
                        st.text(data["raw_text"])

            except Exception as e:
                st.error(f"OCR failed: {e}")

st.divider()
st.caption("💡 Tip: For best results, use a high-resolution image with good lighting. Minimum 300 DPI recommended.")
