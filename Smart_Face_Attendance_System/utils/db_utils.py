import sqlite3
import os

DB_PATH = "db/attendance.db"

def connect_db():
    conn = sqlite3.connect(DB_PATH)
    return conn, conn.cursor()

def create_student_table():
    os.makedirs("db", exist_ok=True)
    conn, cur = connect_db()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            branch TEXT,
            year TEXT,
            class TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_student(student_id, name, branch_year, student_class):
    year = branch_year[:2]  # e.g., "25"
    branch = branch_year[2:]  # e.g., "CSE"
    
    conn, cur = connect_db()
    cur.execute("""
        INSERT OR REPLACE INTO students (student_id, name, branch, year, class)
        VALUES (?, ?, ?, ?, ?)
    """, (student_id, name, branch, year, student_class))
    conn.commit()
    conn.close()

def get_next_roll_number(year, branch):
    conn, cur = connect_db()
    pattern = f"{year}{branch}%"
    cur.execute("SELECT COUNT(*) FROM students WHERE student_id LIKE ?", (pattern,))
    count = cur.fetchone()[0]
    conn.close()
    return count + 1

def delete_missing_students(dataset_dir):
    """
    Automatically remove student records from DB if their dataset folder is deleted.
    """
    conn, cursor = connect_db()
    cursor.execute("SELECT student_id FROM students")
    students = cursor.fetchall()

    for (student_id,) in students:
        folder_path = os.path.join(dataset_dir, student_id)
        if not os.path.exists(folder_path):
            print(f"[SYNC] Removed missing student from DB: {student_id}")
            cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    conn.close()