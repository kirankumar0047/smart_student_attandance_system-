# encode_faces.py

import os
import cv2
import face_recognition
import pickle
import sqlite3
import numpy as np

# Paths
DATASET_DIR = "dataset"
ENCODING_FILE = "encodings/face_encodings.pkl"
DB_PATH = "db/attendance.db"

# Ensure encodings folder exists
os.makedirs("encodings", exist_ok=True)

# Connect to DB to get student name
def get_student_name(student_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name FROM students WHERE student_id=?", (student_id,))
    result = cur.fetchone()
    conn.close()
    return result[0] if result else "Unknown"

# Store all encodings
known_encodings = []
known_ids = []
known_names = []

print("[INFO] Starting face encoding...")

# Loop through dataset
for student_id in os.listdir(DATASET_DIR):
    student_folder = os.path.join(DATASET_DIR, student_id)
    if not os.path.isdir(student_folder):
        continue

    print(f"[INFO] Processing student ID: {student_id}")
    for img_name in os.listdir(student_folder):
        img_path = os.path.join(student_folder, img_name)
        image = cv2.imread(img_path)

        if image is None:
            print(f"[WARNING] Could not read image: {img_path}")
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.face_locations(rgb)
        if len(boxes) == 0:
            print(f"[WARNING] No face found in: {img_path}")
            continue

        encodings = face_recognition.face_encodings(rgb, boxes)

        for encoding in encodings:
            known_encodings.append(encoding)
            known_ids.append(student_id)
            known_names.append(get_student_name(student_id))

# Save encodings to file
data = {"encodings": known_encodings, "ids": known_ids, "names": known_names}
with open(ENCODING_FILE, "wb") as f:
    pickle.dump(data, f)

# Summary
print("\n✅ [ENCODING COMPLETED]")
print(f"🧠 Total Encoded Faces : {len(known_encodings)}")
print(f"💾 Saved to: {ENCODING_FILE}")
print(f"📚 Students Loaded:")
for sid, name in zip(known_ids, known_names):
    print(f"   - {sid} : {name}")