# app.py

import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

DB_PATH = "db/attendance.db"

st.set_page_config(page_title="📊 Attendance Dashboard", layout="wide")
st.title("📊 Smart Face Attendance - Dashboard")

# Function to load attendance with JOIN
def load_attendance(selected_date):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT a.student_id, s.name, s.class, a.timestamp
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        WHERE DATE(a.timestamp) = DATE(?)
    """
    df = pd.read_sql_query(query, conn, params=(selected_date,))
    conn.close()
    return df

# Date input
selected_date = st.date_input("📅 Select Date", date.today())

# Load data
present_df = load_attendance(selected_date)

# Show data
if not present_df.empty:
    st.success(f"✅ {len(present_df)} student(s) were marked present on {selected_date}")
    st.dataframe(present_df, use_container_width=True)
else:
    st.warning("❌ No attendance data found for this date.")

# Optional: Export option
with st.expander("⬇️ Export Attendance Data"):
    if not present_df.empty:
        csv = present_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download as CSV", csv, f"attendance_{selected_date}.csv", "text/csv")
    else:
        st.info("Nothing to export.")