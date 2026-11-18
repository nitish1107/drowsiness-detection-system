<div align="center">

# 👁️ Drowsiness Detection System

### Real-time AI-powered driver drowsiness detection

Detect prolonged eye closure through a webcam using computer vision, trigger an audio warning, and track drowsiness events from a clean Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Face%20Mesh-FF6F00?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

[Features](#-features) · [How it works](#-how-it-works) · [Quick start](#-quick-start) · [Configuration](#-configuration) · [Roadmap](#-roadmap)

</div>

---

## 🌿 About

**Drowsiness Detection System** is a real-time computer vision application that monitors eye activity through a webcam and detects prolonged eye closure.

The system uses **MediaPipe Face Mesh** to locate eye landmarks and calculates the **Eye Aspect Ratio (EAR)** to determine whether the eyes are closed. If the EAR remains below the configured threshold for a number of consecutive frames, the application displays a warning, plays an audio alert, and records the event.

The project is built with **Python and Streamlit**, making it easy to run and interact with locally.

## 🎯 Features

| | Feature | What it does |
|---|---|---|
| 👁️ | **Eye tracking** | Detects eye landmarks in real time using MediaPipe Face Mesh. |
| 📐 | **EAR calculation** | Measures eye openness using the Eye Aspect Ratio. |
| 🚨 | **Drowsiness detection** | Detects prolonged eye closure using consecutive-frame analysis. |
| 🔊 | **Audio alert** | Plays an alarm when drowsiness is detected. |
| 🎚️ | **Adjustable threshold** | Change the EAR sensitivity directly from the sidebar. |
| 📋 | **Session logging** | Records drowsiness and wake-up timestamps. |
| ⏱️ | **Duration tracking** | Calculates how long a drowsiness event lasted. |
| 🖥️ | **Streamlit dashboard** | Provides a simple interactive interface for detection and logs. |

## 🧩 How it works

```mermaid
flowchart LR
    A[Webcam] --> B[OpenCV]
    B --> C[MediaPipe Face Mesh]
    C --> D[Eye Landmarks]
    D --> E[EAR Calculation]
    E --> F{EAR < Threshold?}
    F -->|Yes| G[Count Consecutive Frames]
    G --> H{20+ Frames?}
    H -->|Yes| I[Drowsiness Detected]
    I --> J[Audio Alert]
    I --> K[Session Log]
    F -->|No| L[Reset Counter]
```

### 👁️ Eye Aspect Ratio

The system calculates EAR using six landmark points around each eye:

```text
EAR = (Vertical Distance 1 + Vertical Distance 2)
      / (2 × Horizontal Distance)
```

The EAR of both eyes is averaged and compared against the selected threshold.

To reduce false alerts from normal blinking, the project requires **20 consecutive frames** below the threshold before triggering an alert.

## 🗂 Project structure

```text
drowsiness-detection-system/
├── local_desktop.py    # Native desktop OpenCV window (fastest, no browser)
├── local_web.py        # Localhost web server & dashboard (http://localhost:8000)
├── app.py              # Streamlit web application
├── alert.mp3           # Optional audio alert
├── requirements.txt    # Python dependencies
├── README.md
└── .gitignore
```

## 🚀 Quick start

**Requirements:** Python 3.10 – 3.12 (recommended for MediaPipe), a working webcam.

### 1. Get the code

```bash
git clone https://github.com/nitish1107/drowsiness-detection-system.git
cd drowsiness-detection-system
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
```

Activate it:

| System | Command |
|---|---|
| Windows | `venv\Scripts\activate` |
| macOS / Linux | `source venv/bin/activate` |

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

You can run the project in three different ways:

#### Option A: Native Desktop Window (Recommended - Real-time & Fastest)
```bash
python local_desktop.py
```
*Press `q` inside the video window to exit.*

#### Option B: Localhost Web Dashboard (`http://localhost:8000`)
```bash
python local_web.py
```
*Opens a clean, dark-mode web dashboard running entirely on your local machine.*

#### Option C: Streamlit App (`http://localhost:8501`)
```bash
streamlit run app.py
```

## 🌐 Deploy to Vercel (Free & Instant)

This project includes client-side MediaPipe AI (`index.html`) ready for zero-config deployment on **Vercel**:

1. Go to [vercel.com](https://vercel.com) and log in with your GitHub account.
2. Click **Add New...** > **Project**.
3. Import your GitHub repository: **`nitish1107/drowsiness-detection-system`**.
4. Leave all build settings default and click **Deploy**.
5. Your live app will be live at `https://drowsiness-detection-system-xxx.vercel.app`! Anyone can open the link in any mobile or desktop browser to run real-time drowsiness detection.

## 🎚️ Configuration

The sidebar provides two main controls:

| Setting | Default | Purpose |
|---|---:|---|
| **Start Detection** | Off | Starts or stops webcam detection. |
| **EAR Threshold** | `0.25` | Controls eye-closure sensitivity. |

If the system is too sensitive or not sensitive enough, adjust the EAR threshold from the sidebar.

## 📋 Session logging

When drowsiness is detected, the application records the event timestamp.

When the user becomes alert again, it records the wake-up time and calculates the approximate drowsiness duration.

Example:

```text
Timestamp              Status
2026-10-20 19:42:10    Drowsy
2026-10-20 19:42:14    Awake (after 4.2s)
```

## 🛠️ Tech stack

- **Python** — Core programming language
- **OpenCV** — Webcam capture and image processing
- **MediaPipe Face Mesh** — Facial and eye landmark detection
- **SciPy** — Euclidean distance calculations for EAR
- **Streamlit** — Interactive web interface
- **Pygame** — Audio alert playback
- **Pandas** — Session log display

## ⚠️ Limitations

- Performance can vary with lighting conditions.
- Camera angle and face visibility affect landmark detection.
- Glasses or partially covered eyes may reduce accuracy.
- A fixed EAR threshold may not work equally well for every user.
- Current logs are maintained for the active Streamlit session.
- This is an educational prototype, not a certified automotive safety system.

## 🗺 Roadmap

- [x] Real-time webcam detection
- [x] MediaPipe eye landmarks
- [x] EAR-based detection
- [x] Configurable threshold
- [x] Audio warning
- [x] Session logging
- [ ] Yawning detection
- [ ] Head-pose detection
- [ ] ML-based drowsiness classification
- [ ] Persistent database
- [ ] Advanced analytics dashboard
- [ ] Mobile integration

## 🤝 Contributing

Ideas and pull requests are welcome.

1. Fork the repository
2. Create a branch:
   ```bash
   git checkout -b feature/my-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add my feature"
   ```
4. Push and open a pull request

## 📄 License

Released under the [MIT License](LICENSE).

---

<div align="center">

Built with Python, OpenCV, MediaPipe and Streamlit 🚗

**Stay Awake. Stay Alert. Stay Safe. 👁️**

If you find this project useful, consider giving it a ⭐

</div>
