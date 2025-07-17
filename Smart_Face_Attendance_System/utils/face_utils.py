# utils/face_utils.py

import cv2
import os

def capture_face_images(student_id, save_path, num_images=3):
    cap = cv2.VideoCapture(0)
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow("Capture Face - Press 's' to Save", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            img_path = os.path.join(save_path, f"img{count+1}.jpg")
            cv2.imwrite(img_path, frame)
            count += 1
            print(f"Saved {img_path}")

        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return count == num_images