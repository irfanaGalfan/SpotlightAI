import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import firebase_admin
from firebase_admin import credentials, auth, firestore
import requests
import json

# --- 1. Initialize Firebase ---
if not firebase_admin._apps:
    # Attempt to load from Streamlit Secrets (Cloud Deployment)
    if "firebase" in st.secrets:
        firebase_secrets = dict(st.secrets["firebase"])
        cred = credentials.Certificate(firebase_secrets)
    else:
        # Local Fallback
        local_path = r"C:\Users\Administrator\OneDrive\Desktop\AI_Project\aiproject-4094d-firebase-adminsdk-fbsvc-c46223dc00.json"
        cred = credentials.Certificate(local_path)
    
    firebase_admin.initialize_app(cred)

db = firestore.client()
FIREBASE_API_KEY = "AIzaSyDCkAotVeSnzYwuv60HXws_C9oBcX0St6s"

# --- 2. Session State Initialization ---
states = {
    "page": "dashboard",
    "logged_in": False,
    "current_user": None,
    "role": None,
    "active_tab": "Home"
}
for key, value in states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. Firebase Helper Functions ---
def register_user(email, password, role, extra_detail):
    try:
        user = auth.create_user(email=email, password=password)
        user_data = {
            "uid": user.uid,
            "email": email,
            "role": role,
            "created_at": firestore.SERVER_TIMESTAMP
        }
        user_data["grade" if role == "Student" else "subject"] = extra_detail
        
        db.collection("users").document(user.uid).set(user_data)
        st.success(f"Welcome to Spotlight AI, {email}! Please login now.")
        st.session_state["page"] = "login"
        st.rerun() 
    except Exception as e:
        st.error(f"Registration failed: {e}")

def login_user(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    
    if resp.status_code == 200:
        st.session_state["logged_in"] = True
        st.session_state["current_user"] = email
        
        user_docs = db.collection("users").where("email", "==", email).get()
        if user_docs:
            data = user_docs[0].to_dict()
            role = data.get("role")
            st.session_state["role"] = role
            st.session_state["active_tab"] = "Student Management" if role == "Teacher" else "Home"
            
        st.session_state["page"] = "dashboard"
        st.rerun()
    else:
        st.error("Login failed. Check your credentials.")

# --- 4. Styling ---
st.set_page_config(page_title="Spotlight AI", layout="wide", page_icon="🎓")

st.markdown("""
<style>
    [data-testid="stAppViewContainer"] { background: linear-gradient(to right, #f5f7fa, #c3cfe2); font-family: 'Poppins', sans-serif; }
    [data-testid="stSidebar"] { background: linear-gradient(to bottom, #4a90e2, #0072ff) !important; }
    [data-testid="stSidebar"] * { color: white !important; }
    .metric-card {
        border-radius: 20px; padding: 20px; text-align: center; color: white;
        background: linear-gradient(135deg, #667eea, #764ba2);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    .feature-box {border-radius: 15px; padding: 18px; margin-bottom: 15px; font-weight: bold; color: white !important;}
    .feature-success {background: linear-gradient(135deg,#28a745,#218838);}
    .feature-warning {background: linear-gradient(135deg,#ffc107,#e0a800); color:black !important;}
    .feature-info {background: linear-gradient(135deg,#17a2b8,#138496);}
    div.stButton > button {
        background: linear-gradient(135deg, #4a90e2, #0072ff);
        color: white !important; border: none; padding: 10px 24px;
        border-radius: 12px; font-weight: 600; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s ease; width: 100%;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #0072ff, #4a90e2);
        transform: translateY(-2px); color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. Header ---
col1, space, col_lgn, col_reg = st.columns([3, 0.5, 0.5, 0.6])
with col1:
    st.title("🎓 Spotlight.Ai")

if not st.session_state["logged_in"]:
    with col_lgn:
        if st.button("Login", key="btn_lgn"): st.session_state["page"] = "login"; st.rerun()
    with col_reg:
        if st.button("Register", key="btn_reg"): st.session_state["page"] = "register"; st.rerun()
else:
    with col_reg:
        if st.button("Logout", key="btn_out"): 
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()

st.divider()

# --- 6. Page Routing ---

if st.session_state["page"] == "login":
    st.subheader("🔐 Sign In")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.form_submit_button("Sign In"):
            login_user(email, password)
    if st.button("← Back to Dashboard"): st.session_state["page"] = "dashboard"; st.rerun()

elif st.session_state["page"] == "register":
    st.subheader("📝 Join the Spotlight")
    role = st.radio("I am joining as a:", ["Student", "Teacher"], horizontal=True, index=None)
    with st.form("reg_form"):
        email = st.text_input("Email Address")
        password = st.text_input("Create Password", type="password")
        additional_info = None
        if role == "Student":
            additional_info = st.selectbox("Select your Grade Level", ["Year 9", "Year 10", "Year 11", "Year 12", "Year 13"])
        elif role == "Teacher":
            additional_info = st.selectbox("Select your Department", ["Computer Science", "English", "Mathematics", "Science", "History"])
        
        if st.form_submit_button("Complete Registration"):
            if not role: st.error("Select a role first!")
            elif email and password and additional_info:
                register_user(email, password, role, additional_info)
            else: st.error("Fill in all details.")
    if st.button("← Back to Dashboard"): st.session_state["page"] = "dashboard"; st.rerun()

else:
    if st.session_state["logged_in"]:
        role = st.session_state.get("role")
        options = ["Home", "Student Management", "Adaptive Classroom", "Analytics"] if role == "Teacher" else ["Home", "My Progress"]
        with st.sidebar:
            st.title("Menu")
            st.session_state["active_tab"] = st.radio("Navigate:", options, index=options.index(st.session_state["active_tab"]))

    # --- Content Logic ---
    current_tab = st.session_state.get("active_tab")

    if current_tab == "Home":
        m1, m2, m3 = st.columns(3)
        m1.markdown('<div class="metric-card"><h2>25</h2><p>Active Students</p></div>', unsafe_allow_html=True)
        m2.markdown('<div class="metric-card"><h2>82%</h2><p>Average Score</p></div>', unsafe_allow_html=True)
        m3.markdown('<div class="metric-card"><h2>Medium</h2><p>Difficulty</p></div>', unsafe_allow_html=True)

        st.write("### Adaptive Highlights")
        # Slideshow logic
        count = st_autorefresh(interval=3000, key="slide_refresh")
        imgs = ["images/level_easy.png", "images/level_medium.png", "images/level_hard.png"]
        idx = count % len(imgs)
        try:
            st.image(imgs[idx], width="stretch"))
        except:
            st.info("Ensure the 'images' folder exists in your GitHub repository.")

        st.subheader("System Capabilities")
        st.markdown('<div class="feature-box feature-success">✅ AI-generated Questions adapt to skill levels</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box feature-warning">⚠️ Monitor participation fairness in real-time</div>', unsafe_allow_html=True)
        st.markdown('<div class="feature-box feature-info">ℹ️ Reinforcement Learning adjusts quiz difficulty</div>', unsafe_allow_html=True)

    elif current_tab == "Student Management":
        try:
            import Pages.Students as Students
            Students.show()
        except Exception as e:
            st.error(f"Error loading Students: {e}")

    elif current_tab == "Adaptive Classroom":
        try:
            import Pages.Adaptive_Classroom as ac
            ac.show()
        except Exception as e:
            st.error(f"Error loading Adaptive Classroom: {e}")

    elif current_tab == "Analytics":
        try:
            import Pages.analytics as an
            an.show()
        except Exception as e:
            st.error(f"Error loading Analytics: {e}")
