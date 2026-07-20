import streamlit as st
import requests

# إعدادات الواجهة
st.set_page_config(
    page_title="CogniVerse AI Discovery Agent",
    page_icon="💼",
    layout="wide"
)

API_URL = "http://localhost:8000"

st.title("💼 CogniVerse AI Discovery Agent")
st.caption("Intelligent Business Discovery & AI Opportunity Assessment")

# تهيئة الـ Session State بـ Streamlit
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_topic" not in st.session_state:
    st.session_state.current_topic = "Not Started"
if "completed_topics" not in st.session_state:
    st.session_state.completed_topics = []

# --- الشريط الجانبي (Sidebar) ---
with st.sidebar:
    st.header("📌 Discovery Progress")
    
    if st.button("🚀 Start New Discovery Session", type="primary"):
        try:
            res = requests.post(f"{API_URL}/start").json()
            st.session_state.session_id = res["session_id"]
            st.session_state.current_topic = res["current_topic"]
            st.session_state.completed_topics = []
            st.session_state.messages = [
                {"role": "assistant", "content": res["welcome_message"]}
            ]
            st.rerun()
        except Exception as e:
            st.error("Failed to start session. Make sure FastAPI server is running!")

    st.markdown("---")
    st.subheader("Current Topic")
    st.info(f"👉 **{st.session_state.current_topic}**")

    st.subheader("Completed Topics")
    if st.session_state.completed_topics:
        for topic in st.session_state.completed_topics:
            st.success(f"✓ {topic}")
    else:
        st.write("None yet")

    st.markdown("---")
    # زر تصدير التقرير النهائي
    if st.session_state.session_id:
        if st.button("📥 Export Discovery JSON"):
            try:
                data = requests.get(f"{API_URL}/export/{st.session_state.session_id}").json()
                st.json(data)
            except Exception as e:
                st.error("Error fetching export data.")

# --- منطقة الشات الرئيسية ---
if not st.session_state.session_id:
    st.warning("Please click **'Start New Discovery Session'** in the sidebar to begin.")
else:
    # عرض سجل المحادثة
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # إدخال المستخدم
    if user_input := st.chat_input("Type your response here..."):
        # عرض رسالة المستخدم
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # إرسال للـ Backend واستلام الرد
        with st.spinner("Consultant is thinking..."):
            try:
                payload = {
                    "session_id": st.session_state.session_id,
                    "message": user_input
                }
                response = requests.post(f"{API_URL}/chat", json=payload).json()

                agent_msg = response["agent_message"]
                st.session_state.current_topic = response["current_topic"]
                st.session_state.completed_topics = response["completed_topics"]

                st.session_state.messages.append({"role": "assistant", "content": agent_msg})
                with st.chat_message("assistant"):
                    st.write(agent_msg)
                
                st.rerun()
            except Exception as e:
                st.error("Error communicating with Backend API.")