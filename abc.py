import cv2
import time
import math
import numpy as np
import mediapipe as mp
import pyautogui
import subprocess

# --- CONFIGURATION ---
MODEL_COMPLEXITY = 0
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.7
CAMERA_WIDTH, CAMERA_HEIGHT = 640, 480

# --- INITIALIZATION ---
cap = cv2.VideoCapture(0)
cap.set(3, CAMERA_WIDTH)
cap.set(4, CAMERA_HEIGHT)

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    model_complexity=MODEL_COMPLEXITY,
    max_num_hands=1,
    min_detection_confidence=MIN_DETECTION_CONFIDENCE,
    min_tracking_confidence=MIN_TRACKING_CONFIDENCE
)
mp_draw = mp.solutions.drawing_utils

# --- VARIABLES ---
vol_bar = 400
vol_per = 0
last_action_time = 0
ACTION_COOLDOWN = 0.6
pTime = 0
prev_hand_x = 0
SCRUB_THRESHOLD = 30
tip_ids = [4, 8, 12, 16, 20]

quit_start_time = 0
QUIT_DURATION = 3.0

current_command = "WAITING..."
command_timer = 0
CMD_DURATION = 0.5

print("------------------------------------------------")
print("Gesture Media Controller (Jetson/Linux)")
print("✋ Palm  → Play/Pause")
print("✊ Fist  → Seek")
print("👌 Pinch → Volume")
print("✌ Peace → Hold 3s Quit")
print("🤟 Rock  → Fullscreen")
print("------------------------------------------------")

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    lm_list = []
    active_mode = "IDLE"

    if results.multi_hand_landmarks:
        for hand_lms in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)
            for id, lm in enumerate(hand_lms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy])

    if len(lm_list) != 0:
        fingers = []

        # Thumb
        if lm_list[tip_ids[0]][1] < lm_list[tip_ids[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for i in range(1, 5):
            if lm_list[tip_ids[i]][2] < lm_list[tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        hand_center_x = lm_list[9][1]

        # --- SEEK MODE (FIST ✊) ---
        if fingers == [0, 0, 0, 0, 0]:
            active_mode = "SEEK"
            quit_start_time = 0

            if prev_hand_x != 0:
                delta_x = hand_center_x - prev_hand_x
                if abs(delta_x) > SCRUB_THRESHOLD:
                    if (time.time() - last_action_time) > ACTION_COOLDOWN:
                        if delta_x > 0:
                            pyautogui.press('right')
                            current_command = ">> FORWARD"
                        else:
                            pyautogui.press('left')
                            current_command = "<< REWIND"
                        last_action_time = time.time()
                        command_timer = time.time()
            prev_hand_x = hand_center_x

        # --- PLAY/PAUSE (PALM ✋) ---
        elif fingers == [1, 1, 1, 1, 1]:
            active_mode = "PLAY/PAUSE"
            prev_hand_x = 0
            quit_start_time = 0

            if (time.time() - last_action_time) > 1.0:
                pyautogui.press('space')
                last_action_time = time.time()
                current_command = "PLAY / PAUSE"
                command_timer = time.time()

        # --- FULLSCREEN (ROCK 🤟) ---
        elif fingers == [1, 1, 0, 0, 1]:
            active_mode = "FULLSCREEN"
            prev_hand_x = 0
            quit_start_time = 0

            if (time.time() - last_action_time) > 1.0:
                pyautogui.press('f')
                last_action_time = time.time()
                current_command = "FULLSCREEN TOGGLE"
                command_timer = time.time()

        # --- QUIT MODE (PEACE ✌️) ---
        elif fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:
            active_mode = "QUIT"
            prev_hand_x = 0

            if quit_start_time == 0:
                quit_start_time = time.time()

            elapsed = time.time() - quit_start_time
            bar_width = int(np.interp(elapsed, [0, QUIT_DURATION], [0, 200]))

            cv2.rectangle(img, (220, 300), (220 + bar_width, 330), (0, 0, 255), cv2.FILLED)
            cv2.rectangle(img, (220, 300), (420, 330), (255, 255, 255), 2)
            cv2.putText(img, "QUITTING...", (220, 280),
                        cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

            if elapsed > QUIT_DURATION:
                print("Exited via Gesture.")
                break

        # --- VOLUME MODE (PINCH 👌) ---
        elif fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            active_mode = "VOLUME"
            prev_hand_x = 0
            quit_start_time = 0

            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]

            length = math.hypot(x2 - x1, y2 - y1)

            vol_per = np.interp(length, [20, 150], [0, 100])
            vol_bar = np.interp(length, [20, 150], [400, 150])

            subprocess.run([
                "pactl",
                "set-sink-volume",
                "@DEFAULT_SINK@",
                f"{int(vol_per)}%"
            ])

            cv2.putText(img, f"VOL: {int(vol_per)}%", (50, 100),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

        else:
            active_mode = "IDLE"
            prev_hand_x = 0
            quit_start_time = 0

    # --- UI ---
    cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
    cv2.rectangle(img, (50, int(vol_bar)), (85, 400), (255, 0, 0), cv2.FILLED)

    cTime = time.time()
    fps = 1 / (cTime - pTime) if (cTime - pTime) > 0 else 0
    pTime = cTime
    cv2.putText(img, f'{int(fps)} FPS', (500, 30),
                cv2.FONT_HERSHEY_PLAIN, 1.5, (0, 255, 0), 2)

    cv2.putText(img, f"MODE: {active_mode}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

    if time.time() - command_timer < CMD_DURATION:
        cv2.putText(img, current_command, (150, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 3)

    cv2.imshow("Hand Gesture Control (Linux)", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
