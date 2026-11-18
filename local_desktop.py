import cv2
import mediapipe as mp
from scipy.spatial import distance
import pygame
import threading
import time
import os

# EAR calculation
def calculate_ear(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)

pygame.mixer.init()

def play_alert():
    try:
        if os.path.exists("alert.mp3"):
            pygame.mixer.music.load("alert.mp3")
            pygame.mixer.music.play(loops=-1)
        else:
            try:
                import winsound
                winsound.Beep(1200, 600)
            except Exception:
                pass
    except Exception as e:
        print(f"Error playing sound: {e}")

def stop_alert():
    try:
        pygame.mixer.music.stop()
    except Exception:
        pass

# Landmark points for left and right eyes
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESH = 0.25
CONSEC_FRAMES = 20

def main():
    print("=" * 60)
    print("👁️  Drowsiness Detection - Local Desktop Window")
    print("=" * 60)
    print("• Opening webcam...")
    print("• Press 'q' inside the video window at any time to exit.")
    print("=" * 60)

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("❌ Error: Could not access webcam. Ensure no other application is using it.")
        return

    frame_counter = 0
    drowsy_start = None
    alert_playing = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Webcam stream ended.")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        status_text = "Status: Awake / Attentive"
        color = (0, 255, 0)
        ear_display = 0.0

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE]
                right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE]

                ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2.0
                ear_display = ear

                if ear < EAR_THRESH:
                    frame_counter += 1
                    if frame_counter >= CONSEC_FRAMES:
                        status_text = "DROWSINESS DETECTED!"
                        color = (0, 0, 255)
                        if not alert_playing:
                            drowsy_start = time.time()
                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                            print(f"[{timestamp}] 🚨 DROWSINESS DETECTED! (EAR: {ear:.2f})")
                            threading.Thread(target=play_alert, daemon=True).start()
                            alert_playing = True
                else:
                    frame_counter = 0
                    if drowsy_start:
                        duration = time.time() - drowsy_start
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        print(f"[{timestamp}] ✅ User is awake again (Drowsy duration: {duration:.1f}s)")
                        drowsy_start = None
                        alert_playing = False
                        stop_alert()

                # Draw landmark dots on eyes
                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 2, (0, 255, 0), -1)

        # Overlay text on video frame
        cv2.putText(frame, f"EAR: {ear_display:.2f}", (30, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, status_text, (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        cv2.putText(frame, "Press 'q' to exit", (30, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        cv2.imshow("Drowsiness Detection - Local Window", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stop_alert()
    cap.release()
    cv2.destroyAllWindows()
    print("Application closed.")

if __name__ == "__main__":
    main()
