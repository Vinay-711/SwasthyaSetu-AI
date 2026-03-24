"""
Page 5: Notification System
"""
import streamlit as st
import requests
from datetime import datetime

API = "http://localhost:8000"

st.set_page_config(page_title="Notifications · SwasthyaSetu", page_icon="🔔", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif;}
.stApp{background:#0a0a1a;color:#e0e0ff;}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#0f0c29,#302b63,#24243e);}
[data-testid="stSidebar"] *{color:#e0e0ff!important;}
h1,h2,h3{color:#7c7cff!important;}
.stButton>button{background:linear-gradient(90deg,#4040ff,#7070ff);color:white;border:none;border-radius:8px;font-weight:600;}
.stTextInput>div>input,.stTextArea textarea,.stSelectbox>div{background:#1a1a3a!important;color:#e0e0ff!important;border:1px solid #3535a0!important;}
.notif-card{background:#1a1a3a;border:1px solid #3535a0;border-radius:12px;padding:16px;margin-bottom:12px;}
.notif-card .meta{color:#6060aa;font-size:0.8rem;margin-top:8px;}
.badge-sent{background:#22c55e;color:white;border-radius:12px;padding:2px 10px;font-size:0.75rem;}
.badge-failed{background:#ef4444;color:white;border-radius:12px;padding:2px 10px;font-size:0.75rem;}
</style>
""", unsafe_allow_html=True)

st.title("🔔 Notification System")
st.markdown("Send appointment reminders, health alerts, or custom messages to patients.")

tab_send, tab_history = st.tabs(["📤 Send Notification", "📋 Notification History"])

# ── Send ───────────────────────────────────────────────────────────────────
with tab_send:
    with st.form("send_notif_form"):
        st.subheader("Compose Notification")
        patient_id = st.text_input("Patient Health ID *", placeholder="A1B2C3")
        channel    = st.selectbox("Channel", ["sms", "push", "email"])

        # Message templates
        template = st.selectbox("Quick Template", [
            "Custom message",
            "Your appointment is scheduled for tomorrow at 10:00 AM.",
            "Your prescription is ready for pickup at the pharmacy.",
            "Reminder: Take your medication as prescribed. Stay healthy!",
            "Your lab results are ready. Please visit the clinic.",
            "Your health check-up is due. Please schedule an appointment.",
        ])
        message = st.text_area(
            "Message *",
            value="" if template == "Custom message" else template,
            height=100,
            placeholder="Type your notification message here…",
        )
        submitted = st.form_submit_button("📤 Send Notification", use_container_width=True)

    if submitted:
        if not patient_id.strip() or not message.strip():
            st.error("Patient ID and message are required.")
        else:
            with st.spinner("Sending notification…"):
                try:
                    payload = {
                        "patient_id": patient_id.strip().upper(),
                        "message": message,
                        "channel": channel,
                    }
                    r = requests.post(f"{API}/notifications/send", json=payload, timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    st.success(f"✅ Notification sent! ID: **{data['notification_id']}** via {data['channel'].upper()}")
                except Exception as e:
                    st.error(f"Failed to send: {e}")

# ── History ────────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Notification History")
    lookup_id = st.text_input("Enter Patient Health ID", placeholder="A1B2C3", key="hist_pid")

    if st.button("🔍 Fetch History", use_container_width=True):
        if not lookup_id.strip():
            st.warning("Please enter a Patient ID.")
        else:
            with st.spinner("Fetching…"):
                try:
                    r = requests.get(f"{API}/notifications/{lookup_id.strip()}", timeout=10)
                    r.raise_for_status()
                    data = r.json()
                    notifs = data.get("notifications", [])

                    if not notifs:
                        st.info(f"No notifications found for patient **{lookup_id.upper()}**.")
                    else:
                        st.markdown(f"**{len(notifs)} notification(s) found for `{data['patient_id']}`**")
                        for n in reversed(notifs):
                            badge = (
                                "<span class='badge-sent'>SENT</span>"
                                if n["status"] == "sent"
                                else "<span class='badge-failed'>FAILED</span>"
                            )
                            channel_icon = {"sms": "📱", "push": "🔔", "email": "✉️"}.get(n["channel"], "📨")
                            ts = n.get("sent_at", "")
                            st.markdown(f"""
<div class="notif-card">
    <strong>{channel_icon} {n['channel'].upper()}</strong> {badge}
    <p style="margin:8px 0;">{n['message']}</p>
    <div class="meta">ID: {n['notification_id']} · {ts}</div>
</div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error: {e}")
