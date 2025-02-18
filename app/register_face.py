import cv2
import face_recognition
import os

DATASET_PATH = "faces/"

def register_face(username):
    """Captures the user's face and saves it as an image."""
    if not os.path.exists(DATASET_PATH):
        os.makedirs(DATASET_PATH)

    cap = cv2.VideoCapture(0)  # Open the camera
    print(f"Capturing face for {username}. Look at the camera...")

    while True:
        ret, frame = cap.read()
        if not ret:
            continue
        
        face_locations = face_recognition.face_locations(frame)
        if face_locations:
            face_path = os.path.join(DATASET_PATH, f"{username}.jpg")
            cv2.imwrite(face_path, frame)
            print(f"Face registered for {username} at {face_path}")
            break  # Stop after capturing one good image

    cap.release()
    return f"Face registered for {username}"
