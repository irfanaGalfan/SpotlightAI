import streamlit as st
from firebase_admin import firestore
import os
def show():
    st.header("👩‍🎓 Student Management")

    db = firestore.client()

    if "current_user" not in st.session_state:
        st.error("Please log in first.")
        return

    # -----------------------------
    # Fetch ALL classes
    # -----------------------------
    existing_classes = []
    try:
        docs = db.collection("classes").stream()
        for doc in docs:
            class_name = doc.id
            if isinstance(class_name, str) and class_name.strip():
                existing_classes.append(class_name)
    except Exception as e:
        st.error(f"Could not fetch classes: {e}")

    existing_classes = sorted(list(set(existing_classes)))

    # -----------------------------
    # Class selector
    # -----------------------------
    class_choice = st.selectbox(
        "Select Existing Class or Enter New Class Name",
        ["-- Create New Class --"] + existing_classes
    )

    if class_choice == "-- Create New Class --":
        class_name = st.text_input("New Class Name")
    else:
        class_name = class_choice

    uploaded_files = st.file_uploader(
        "Upload student images (names only)",
        type=["jpg", "png", "jpeg"],
        accept_multiple_files=True
    )

    if st.button("Create Class / Add Students"):

        if not isinstance(class_name, str):
            st.error("Invalid class name")
            return

        class_name = class_name.strip()

        if not class_name:
            st.error("Class name cannot be empty")
            return

        if not uploaded_files:
            st.error("Upload at least one image")
            return
         # 👇 SAVE IMAGES HERE
        save_dir = f"classes/{class_name}"
        os.makedirs(save_dir, exist_ok=True)

        for file in uploaded_files:
            file_path = os.path.join(save_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

        # 👇 THEN extract student names
        student_names = []
        for file in uploaded_files:
            name = file.name.split(".")[0].strip()
            if name:
                student_names.append(name)
    

        # -----------------------------
        # Extract student names
        # -----------------------------
        student_names = []
        for file in uploaded_files:
            name = file.name.split(".")[0].strip()
            if name:
                student_names.append(name)

        if not student_names:
            st.error("No valid student names found")
            return

        # -----------------------------
        # Create class document
        # -----------------------------
        class_ref = db.collection("classes").document(class_name)
        class_ref.set({
            "teacher": str(st.session_state["current_user"]),
            "created_at": firestore.SERVER_TIMESTAMP
        }, merge=True)

        # -----------------------------
        # Create students subcollection
        # -----------------------------
        students_ref = class_ref.collection("students")

        for student in student_names:
            students_ref.document(student).set({
                "score": 0,
                "turns": 0,
                "answered_questions": []
            }, merge=True)

        st.success(f"✅ Class '{class_name}' updated with {len(student_names)} students")
