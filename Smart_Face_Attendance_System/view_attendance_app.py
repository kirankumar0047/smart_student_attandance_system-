# app.py

import streamlit as st
import sqlite3
import pandas as pd
import os
from datetime import date

DB_PATH = "db/attendance.db"

st.set_page_config(page_title="Smart Face Attendance", layout="wide")
st.title("🎓 Smart Face Attendance System")

# Sidebar Navigation
menu = st.sidebar.selectbox("📂 Navigate", ["Home", "View Attendance"])

# ---------------- View Attendance Section ---------------- #
def load_attendance_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.student_id, s.name, s.branch, s.year, s.class, a.timestamp
        FROM students s
        JOIN attendance a ON s.student_id = a.student_id
        ORDER BY a.timestamp DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    columns = ["Student ID", "Name", "Branch", "Year", "Class", "Timestamp"]
    return pd.DataFrame(rows, columns=columns)

# ---------------- Page Logic ---------------- #
if menu == "Home":
    st.markdown("👋 Welcome! Use the sidebar to navigate.")

elif menu == "View Attendance":
    st.subheader("📋 Attendance Dashboard")

    if not os.path.exists(DB_PATH):
        st.error("❌ Attendance database not found.")
    else:
        df = load_attendance_data()
        if df.empty:
            st.warning("⚠️ No attendance data found.")
        else:
            # Filters
            with st.expander("🔍 Filter Records"):
                name_filter = st.text_input("Search by Name")
                branch_filter = st.selectbox("Filter by Branch", ["All"] + sorted(df["Branch"].unique().tolist()))
                class_filter = st.selectbox("Filter by Class", ["All"] + sorted(df["Class"].unique().tolist()))

                if name_filter:
                    df = df[df["Name"].str.contains(name_filter, case=False)]
                if branch_filter != "All":
                    df = df[df["Branch"] == branch_filter]
                if class_filter != "All":
                    df = df[df["Class"] == class_filter]

            st.dataframe(df, use_container_width=True)

            # Download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download as CSV", csv, "attendance_report.csv", "text/csv")

            st.success(f"✅ Total Records Shown: {len(df)}")