import cv2
import face_recognition
import os
import numpy as np
import pickle
import sqlite3
from datetime import datetime
import pygame
import pyttsx3

# === Init: Sound & Voice === #
pygame.mixer.init()
BEEP_PATH = "sounds/beep-06.wav"

engine = pyttsx3.init()
engine.setProperty('rate', 160)

# === Load known encodings === #
with open("encodings/face_encodings.pkl", "rb") as f:
    known_data = pickle.load(f)

known_encodings = known_data["encodings"]
known_ids = known_data["ids"]

# === DB setup === #
conn = sqlite3.connect("db/attendance.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        timestamp TEXT
    )
""")
conn.commit()

# === Helper to log attendance === #
def mark_attendance(student_id):
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("SELECT * FROM attendance WHERE student_id = ? AND DATE(timestamp) = DATE('now')", (student_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO attendance (student_id, timestamp) VALUES (?, ?)", (student_id, timestamp))
        conn.commit()
        print(f"[INFO] Marked Present: {student_id} at {timestamp}")
        
        # ✅ Play beep sound
        pygame.mixer.music.load(BEEP_PATH)
        pygame.mixer.music.play()

        # ✅ Optional: Greet the student
        engine.say(f"Welcome {student_id}")
        engine.runAndWait()

# === Start Webcam === #
print("[INFO] Starting webcam. Press 'q' to quit...")
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    boxes = face_recognition.face_locations(rgb_small_frame)
    encodings = face_recognition.face_encodings(rgb_small_frame, boxes)

    for encoding, box in zip(encodings, boxes):
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=0.5)
        face_distances = face_recognition.face_distance(known_encodings, encoding)

        top, right, bottom, left = [v * 4 for v in box]

        if True in matches:
            best_match_index = np.argmin(face_distances)
            student_id = known_ids[best_match_index]
            label = student_id
            color = (0, 255, 0)  # Green box for registered

            mark_attendance(student_id)

        else:
            label = "Unregistered - Please Register"
            color = (0, 0, 255)  # Red box for unregistered
            engine.say("Please register first")
            engine.runAndWait()

        # Draw bounding box
        cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
        cv2.rectangle(frame, (left, bottom - 20), (right, bottom), color, cv2.FILLED)
        cv2.putText(frame, label, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    cv2.imshow("Smart Face Attendance", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# === Cleanup === #
cap.release()
cv2.destroyAllWindows()
conn.close()