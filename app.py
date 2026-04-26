import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests

# ----------------------------
# 1. Firebase Initialization
# ----------------------------
if not firebase_admin._apps:
    try:
        # Update this path to your actual JSON file location
        cred = credentials.Certificate(r"C:\Users\Administrator\OneDrive\Desktop\AI_Project\aiproject-4094d-firebase-adminsdk-fbsvc-c46223dc00.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Firebase Init Error: {e}")

db = firestore.client()
FIREBASE_API_KEY = "AIzaSyDCkAotVeSnzYwuv60HXws_C9oBcX0St6s"

# ----------------------------
# 2. Page Configuration (Must be first)
# ----------------------------
st.set_page_config(page_title="Spotlight AI", layout="wide")

# ----------------------------
# 3. Session State
# ----------------------------
if "page" not in st.session_state:
    st.session_state.page = "dashboard"
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# ----------------------------
# 4. Helper Functions
# ----------------------------
def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        st.session_state.logged_in = True
        st.session_state.current_user = email
        st.session_state.page = "dashboard"
        st.rerun()
    else:
        st.error("Invalid email or password")

# ----------------------------
# 5. UI & Styling
# ----------------------------
st.markdown("""
<style>
    .metric-card {border-radius:15px; padding:15px; text-align:center; color:white; background:linear-gradient(135deg,#667eea,#764ba2); margin-bottom:10px;}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 6. Navigation Logic
# ----------------------------

# HEADER SECTION
t_col, b_col = st.columns([3, 1])
with t_col:
    st.title("🎓 Spotlight AI")
with b_col:
    if not st.session_state.logged_in:
        c1, c2 = st.columns(2)
        if c1.button("Login", key="main_login_btn"):
            st.session_state.page = "login"
            st.rerun()
        if c2.button("Register", key="main_reg_btn"):
            st.session_state.page = "register"
            st.rerun()
    else:
        if st.button("Logout", key="main_logout_btn"):
            st.session_state.logged_in = False
            st.session_state.page = "dashboard"
            st.rerun()

st.divider()

# PAGE ROUTING
if st.session_state.page == "login":
    st.subheader("🔐 Login")
    l_email = st.text_input("Email", key="l_email")
    l_pass = st.text_input("Password", type="password", key="l_pass")
    if st.button("Sign In", key="do_login"):
        login_user(l_email, l_pass)
    if st.button("← Back", key="back_from_login"):
        st.session_state.page = "dashboard"
        st.rerun()

elif st.session_state.page == "register":
    st.subheader("📝 Register")
    r_email = st.text_input("Email", key="r_email")
    r_pass = st.text_input("Password", type="password", key="r_pass")
    if st.button("← Back", key="back_from_reg"):
        st.session_state.page = "dashboard"
        st.rerun()

else:
    # --- DASHBOARD PAGE ---
    if st.session_state.logged_in:
        st.success(f"Welcome, {st.session_state.current_user}")
    
    # 3-Column Metrics
    m1, m2, m3 = st.columns(3)
    m1.markdown('<div class="metric-card"><h3>25</h3><p>Active Students</p></div>', unsafe_allow_html=True)
    m2.markdown('<div class="metric-card"><h3>82%</h3><p>Avg Score</p></div>', unsafe_allow_html=True)
    m3.markdown('<div class="metric-card"><h3>Med</h3><p>Difficulty</p></div>', unsafe_allow_html=True)

    st.subheader("Classroom Insights")
    
    # ONLY Refresh if we are on the dashboard
    # This prevents the refresh from triggering during Login/Register
    count = st_autorefresh(interval=3000, key="dash_refresh")
    
    images = ["images/level_easy.png", "images/level_medium.png", "images/level_hard.png"]
    idx = count % len(images)
    
    try:
        st.image(images[idx], use_container_width=True)
    except:
        st.info(f"Showing simulation slide {idx + 1}")

    st.subheader("Key Features")
    st.info("✅ AI-based fair student selection")
    st.warning("⚠️ Detect under-participation automatically")
