# 🎥 Touchless Media Control using Hand Gestures (Jetson Nano)

A real-time touchless Human–Computer Interaction (HCI) system that enables media control using hand gestures.  
Built using **MediaPipe**, **OpenCV**, and deployed on **NVIDIA Jetson Nano** for edge AI execution.

---

## 🚀 Overview

This project implements a gesture-based media controller capable of:

- ▶️ Play / Pause
- ⏩ Seek Forward / Rewind
- 🔊 Volume Control
- 🖥 Fullscreen Toggle
- ❌ Exit via Gesture

The system uses real-time hand landmark detection and biomechanically distinct gesture mapping to ensure high accuracy and minimal false triggers.

---

## 🧠 Key Features

- Real-time hand tracking using MediaPipe (21 landmarks)
- Deterministic landmark-based gesture recognition
- Temporal stability and cooldown logic
- Distinct gesture separation to reduce false positives
- Optimized for NVIDIA Jetson Nano (Edge AI)
- Linux-compatible media control
- FPS monitoring and system feedback UI

---

## ✋ Gesture Mapping

| Gesture | Action |
|----------|----------|
| ✋ Open Palm | Play / Pause |
| ✊ Closed Fist | Seek (Drag Left/Right) |
| 👌 Pinch | Volume Control |
| 🤟 Rock Sign | Fullscreen Toggle |
| ✌️ Peace Sign (Hold 3s) | Exit Application |

---

## 🏗 System Architecture

Camera Input
↓
Frame Capture (OpenCV)
↓
Hand Landmark Detection (MediaPipe)
↓
Gesture Classification Logic
↓
Media Control Command (PyAutoGUI / Linux Audio)
↓
Active Media Application (VLC / YouTube / Browser)



---

## 📊 Performance (Jetson Nano)

- Accuracy: ~98%
- FPS: 10-14 FPS
- Latency: 50–80 ms
- False Positives: Very Low (after optimization)
- False Negatives: Rare

---

## 🖥 Hardware Requirements

- NVIDIA Jetson Nano (JetPack 4.6.1 recommended)
- USB Webcam
- HDMI Monitor (or headless via VNC)
- Ubuntu 18.04

---

## ⚙️ Software Requirements

- Python 3.6 (recommended for Jetson Nano)
- MediaPipe 0.8.5
- OpenCV
- NumPy
- PyAutoGUI

---

## 📦 Installation (Jetson Nano)

```bash
sudo apt update
sudo apt install python3-pip
pip3 install --upgrade pip
pip3 install --no-cache-dir mediapipe==0.8.5
pip3 install opencv-python numpy pyautogui
---

##🛠 Optimization Techniques Used

Reduced model complexity for Jetson compatibility

Cooldown mechanism to prevent repeated triggers

Strict finger-state validation

Gesture separation to avoid overlap

Hold-duration logic for quit command

Landmark-based geometric validation


⚠️ System Limitations

Performance may degrade under low lighting

Single-hand detection only

Requires active media window

Sensitive to severe occlusion



🔮 Future Improvements

Adaptive gesture learning

Multi-hand support

Context-aware gesture mapping

TensorRT acceleration

Low-light robustness enhancement

Gesture confidence scoring
