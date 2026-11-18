import cv2
import mediapipe as mp
from scipy.spatial import distance
import pygame
import threading
import time
import os
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

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

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

EAR_THRESH = 0.25
CONSEC_FRAMES = 20

# Global shared state
current_jpeg = None
current_status = "Waiting for camera..."
current_ear = 0.0
is_drowsy = False
session_logs = []
lock = threading.Lock()

def camera_worker():
    global current_jpeg, current_status, current_ear, is_drowsy, session_logs

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if not cap.isOpened():
        cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access webcam.")
        current_status = "Error: Webcam not found"
        return

    frame_counter = 0
    drowsy_start = None
    alert_playing = False

    while True:
        ret, frame = cap.read()
        if not ret:
            time.sleep(0.05)
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(rgb_frame)

        status_text = "Awake / Attentive"
        drowsy_flag = False
        ear_val = 0.0

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                h, w, _ = frame.shape
                left_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in LEFT_EYE]
                right_eye = [(int(face_landmarks.landmark[i].x * w), int(face_landmarks.landmark[i].y * h)) for i in RIGHT_EYE]

                ear = (calculate_ear(left_eye) + calculate_ear(right_eye)) / 2.0
                ear_val = ear

                if ear < EAR_THRESH:
                    frame_counter += 1
                    if frame_counter >= CONSEC_FRAMES:
                        status_text = "DROWSINESS DETECTED!"
                        drowsy_flag = True
                        if not alert_playing:
                            drowsy_start = time.time()
                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                            with lock:
                                session_logs.append({"timestamp": timestamp, "status": "Drowsy"})
                            threading.Thread(target=play_alert, daemon=True).start()
                            alert_playing = True
                else:
                    frame_counter = 0
                    if drowsy_start:
                        dur = time.time() - drowsy_start
                        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                        with lock:
                            session_logs.append({"timestamp": timestamp, "status": f"Awake (after {dur:.1f}s)"})
                        drowsy_start = None
                        alert_playing = False
                        stop_alert()

                for pt in left_eye + right_eye:
                    cv2.circle(frame, pt, 2, (0, 255, 0), -1)

        # Overlay text
        color = (0, 0, 255) if drowsy_flag else (0, 255, 0)
        cv2.putText(frame, f"EAR: {ear_val:.2f}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, status_text, (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ret:
            with lock:
                current_jpeg = jpeg.tobytes()
                current_status = status_text
                current_ear = round(ear_val, 2)
                is_drowsy = drowsy_flag

        time.sleep(0.03)

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Drowsiness Detection System (Localhost)</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background: #0f172a; color: #f8fafc; padding: 24px; }
    .container { max-width: 960px; margin: 0 auto; }
    header { margin-bottom: 24px; text-align: center; }
    h1 { font-size: 28px; margin-bottom: 8px; color: #38bdf8; }
    p.subtitle { color: #94a3b8; font-size: 14px; }
    .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }
    @media (max-width: 768px) { .grid { grid-template-columns: 1fr; } }
    .card { background: #1e293b; border-radius: 12px; padding: 16px; border: 1px solid #334155; }
    .video-container { border-radius: 8px; overflow: hidden; background: #000; display: flex; justify-content: center; }
    img#stream { width: 100%; height: auto; display: block; }
    .status-badge { display: inline-block; padding: 8px 16px; border-radius: 20px; font-weight: bold; font-size: 16px; margin-top: 12px; }
    .status-normal { background: #065f46; color: #34d399; }
    .status-alert { background: #7f1d1d; color: #f87171; animation: pulse 1s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
    .metric { margin-top: 16px; padding: 12px; background: #0f172a; border-radius: 8px; }
    .metric-title { font-size: 12px; color: #94a3b8; text-transform: uppercase; }
    .metric-value { font-size: 24px; font-weight: bold; color: #f8fafc; margin-top: 4px; }
    table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
    th, td { text-align: left; padding: 8px 10px; border-bottom: 1px solid #334155; }
    th { color: #94a3b8; }
    .badge-drowsy { color: #f87171; font-weight: bold; }
    .badge-awake { color: #34d399; }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <h1>👁️ Drowsiness Detection System</h1>
      <p class="subtitle">Running locally on <strong>http://localhost:8000</strong></p>
    </header>

    <div class="grid">
      <div class="card">
        <h3 style="margin-bottom: 12px; color: #94a3b8; font-size: 14px;">LIVE WEBCAM FEED</h3>
        <div class="video-container">
          <img id="stream" src="/video_feed" alt="Webcam Stream">
        </div>
        <div style="text-align: center; margin-top: 12px;">
          <span id="badge" class="status-badge status-normal">Status: Initializing...</span>
        </div>
      </div>

      <div class="card">
        <h3 style="margin-bottom: 12px; color: #94a3b8; font-size: 14px;">MONITORING STATS</h3>
        <div class="metric">
          <div class="metric-title">Current Eye Aspect Ratio (EAR)</div>
          <div id="ear_val" class="metric-value">0.00</div>
        </div>
        <div class="metric">
          <div class="metric-title">EAR Threshold</div>
          <div class="metric-value">0.25</div>
        </div>

        <h3 style="margin-top: 20px; margin-bottom: 8px; color: #94a3b8; font-size: 14px;">SESSION EVENT LOG</h3>
        <div style="max-height: 260px; overflow-y: auto;">
          <table>
            <thead>
              <tr><th>Time</th><th>Status</th></tr>
            </thead>
            <tbody id="log_table">
              <tr><td colspan="2" style="color:#64748b;">No events recorded yet.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>

  <script>
    setInterval(async () => {
      try {
        const res = await fetch('/status');
        const data = await res.json();
        
        document.getElementById('ear_val').innerText = data.ear.toFixed(2);
        const badge = document.getElementById('badge');
        badge.innerText = data.status;
        if (data.is_drowsy) {
          badge.className = 'status-badge status-alert';
        } else {
          badge.className = 'status-badge status-normal';
        }

        if (data.logs && data.logs.length > 0) {
          const tbody = document.getElementById('log_table');
          tbody.innerHTML = data.logs.slice(-10).reverse().map(l => `
            <tr>
              <td>${l.timestamp}</td>
              <td class="${l.status.startsWith('Drowsy') ? 'badge-drowsy' : 'badge-awake'}">${l.status}</td>
            </tr>
          `).join('');
        }
      } catch (e) {}
    }, 400);
  </script>
</body>
</html>
"""

class VideoStreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        elif self.path == '/status':
            with lock:
                payload = {
                    "ear": current_ear,
                    "status": current_status,
                    "is_drowsy": is_drowsy,
                    "logs": list(session_logs)
                }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(payload).encode('utf-8'))
        elif self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            try:
                while True:
                    with lock:
                        jpeg = current_jpeg
                    if jpeg is not None:
                        self.wfile.write(b'--frame\r\n')
                        self.send_header('Content-Type', 'image/jpeg')
                        self.send_header('Content-Length', str(len(jpeg)))
                        self.end_headers()
                        self.wfile.write(jpeg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.04)
            except Exception:
                pass
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Silence HTTP request terminal spam
        return

def main():
    PORT = 8000
    print("=" * 60)
    print("👁️  Starting Localhost Web Server (No Streamlit required)")
    print("=" * 60)
    print(f"• Server address: http://localhost:{PORT}")
    print("• Press Ctrl + C in this terminal to stop.")
    print("=" * 60)

    # Start webcam thread
    cam_thread = threading.Thread(target=camera_worker, daemon=True)
    cam_thread.start()

    server = HTTPServer(('127.0.0.1', PORT), VideoStreamHandler)
    webbrowser.open(f"http://localhost:{PORT}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        stop_alert()
        server.server_close()

if __name__ == "__main__":
    main()
