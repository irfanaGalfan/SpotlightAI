import streamlit as st
import os
import firebase_admin
from firebase_admin import credentials, firestore
import pandas as pd
import plotly.express as px

# -----------------------------
# FIREBASE INITIALIZATION
# -----------------------------
if "firebase_initialized" not in st.session_state:
    try:
        firebase_admin.get_app()
    except ValueError:
        cred = credentials.Certificate(r"C:/Users/Administrator/OneDrive/Desktop/AI_Project/aiproject-4094d-firebase-adminsdk-fbsvc-c46223dc00.json")  # Replace with your Firebase key
        firebase_admin.initialize_app(cred)
    st.session_state.firebase_initialized = True

db = firestore.client()

# -----------------------------
# LOAD STUDENTS DATA
# -----------------------------
def load_class_students(class_name):
    students = []

    students_ref = (
        db.collection("classes")
          .document(class_name)
          .collection("students")
    )

    for doc in students_ref.stream():
        data = doc.to_dict()
        students.append({
            "name": doc.id,
            "score": data.get("score", 0),
            "turns": data.get("turns", 0),
            "answered_questions": data.get("answered_questions", []),
            "difficulty_history": data.get("difficulty_history", []),
            "recent_scores": data.get("recent_scores", [])
        })

    return students


# -----------------------------
# RL TABLE SETUP
# -----------------------------
ACTIONS = ["Easy", "Medium", "Hard"]
REWARD_RULES = {
    "LOW": {"Easy": (10, -5), "Medium": (5, -5), "Hard": (0, -5)},
    "MEDIUM": {"Easy": (5, -2), "Medium": (10, -5), "Hard": (7, -5)},
    "HIGH": {"Easy": (2, -1), "Medium": (5, -2), "Hard": (10, -5)},
}

def get_rl_table(q_table):
    data = []
    for state in ["LOW", "MEDIUM", "HIGH"]:
        for action in ACTIONS:
            q_value = q_table.get(state, {}).get(action, 0.0)
            reward, penalty = REWARD_RULES[state][action]
            data.append({
                "State": state,
                "Action": action,
                "Q-Value": round(q_value, 2),
                "Reward": reward,
                "Penalty": penalty,
                "Notes": f"Policy for {state} students"
            })
    return pd.DataFrame(data)

# -----------------------------
# SHOW FUNCTION FOR DASHBOARD
# -----------------------------
def show():
    st.title("📊 Adaptive Classroom Analytics")

    # -----------------------------
    # Select Class
    # -----------------------------
    class_docs = db.collection("classes").stream()
    class_list = [doc.id for doc in class_docs]

    if not class_list:
        st.warning("No classes found.")
        return
    if not class_list:
        st.warning("No classes found.")
        return

    class_name = st.selectbox("Select Class", class_list, key="analytics_class_select")

    students = load_class_students(class_name)
    if not students:
        st.warning("No students found in this class.")
        return

    # -----------------------------
    # STUDENT OVERVIEW TABLE
    # -----------------------------
    st.subheader("👥 Student Overview")
    overview_data = []
    for s in students:
        overview_data.append({
            "Name": s["name"],
            "Score": s["score"],
            "Turns": s["turns"],
            "Questions Answered": len(s.get("answered_questions", []))
        })
    df_overview = pd.DataFrame(overview_data)
    st.dataframe(df_overview)

    # -----------------------------
    # SCORE PROGRESSION CHART
    # -----------------------------
    st.subheader("📈 Score Progression")
    score_data = []
    for s in students:
        cumulative = 0
        for i, r in enumerate(s.get("recent_scores", [])):
            cumulative += r
            score_data.append({
                "Student": s["name"],
                "Question": i + 1,
                "Cumulative Score": cumulative
            })

    if score_data:
        df_score = pd.DataFrame(score_data)
        fig_score = px.line(df_score, x="Question", y="Cumulative Score", color="Student",
                            markers=True, title="Score Progression per Student")
        st.plotly_chart(fig_score)

    # -----------------------------
    # DIFFICULTY HISTORY
    # -----------------------------
    st.subheader("📊 Difficulty History")
    difficulty_data = []
    for s in students:
        for i, level in enumerate(s.get("difficulty_history", [])):
            state = "LOW" if s["score"] <= 1 else "MEDIUM" if s["score"] <= 3 else "HIGH"
            reward, penalty = REWARD_RULES[state].get(level, (0, 0))
            difficulty_data.append({
                "Student": s["name"],
                "Question": i + 1,
                "Difficulty": level,
                "State": state,
                "Reward": reward,
                "Penalty": penalty
            })

    if difficulty_data:
        df_diff = pd.DataFrame(difficulty_data)
        st.dataframe(df_diff)
        fig_diff = px.histogram(df_diff, x="Student", color="Difficulty", barmode="stack",
                                title="Questions Answered by Difficulty Level")
        st.plotly_chart(fig_diff)

    # -----------------------------
    # RL TABLE
    # -----------------------------
    st.subheader("🤖 Reinforcement Learning Q-Table")
    q_table = st.session_state.get("Q_table", {})
    df_rl = get_rl_table(q_table)
    st.dataframe(df_rl)

    # -----------------------------
    # LEADERBOARD
    # -----------------------------
    st.subheader("🏆 Leaderboard")
    leaderboard = df_overview.sort_values(by="Score", ascending=False)
    st.table(leaderboard[["Name", "Score", "Turns"]])
