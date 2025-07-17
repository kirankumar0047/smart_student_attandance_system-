# register_student.py

import streamlit as st
import os
from datetime import datetime
from PIL import Image
from utils.db_utils import insert_student, create_student_table, get_next_roll_number

# Create DB and table if not exists
create_student_table()

st.title("📸 Student Registration - Smart Face Attendance System")

# Registration form
with st.form("register_form"):
    name = st.text_input("Full Name")

    # Select branch
    branch = st.selectbox("Select Branch", ["CSE", "ECE", "MECH", "CIVIL", "EEE", "IT"])

    # Select year
    current_year = datetime.now().year % 100  # e.g., 25 for 2025
    year = st.selectbox("Admission Year", [current_year - i for i in range(5)])  # last 5 years

    # Auto-generate student ID
    if name and branch:
        roll_number = get_next_roll_number(year, branch)
        student_id = f"{year}{branch}{roll_number:03d}"
    else:
        student_id = "Waiting for Name & Branch..."

    st.text_input("Generated Student ID", value=student_id, disabled=True)

    student_class = st.text_input("Class (e.g., BTech 3rd Year)")

    # Capture 3 face images
    img1 = st.camera_input("Capture Face Image 1")
    img2 = st.camera_input("Capture Face Image 2")
    img3 = st.camera_input("Capture Face Image 3")

    submitted = st.form_submit_button("Register")

if submitted:
    if name and branch and student_class and img1 and img2 and img3 and "Waiting" not in student_id:
        dataset_path = f"dataset/{student_id}"
        os.makedirs(dataset_path, exist_ok=True)

        # Save images
        for idx, img in enumerate([img1, img2, img3], start=1):
            image = Image.open(img)
            image = image.convert("RGB")
            image.save(f"{dataset_path}/img{idx}.jpg")

        # Insert student info to DB
        insert_student(student_id, name, f"{year} {branch}", student_class)

        st.success(f"{name} registered successfully with Student ID: {student_id}")
    else:
        st.warning("Please fill all fields and capture all 3 images.")