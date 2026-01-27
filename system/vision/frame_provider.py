import cv2
import numpy as np
import mss
from system.vision.webcam import get_webcam_frame

def get_screen_frame():
    with mss.mss() as sct:
        # 👇 IMPORTANT: choose correct monitor
        monitor = sct.monitors[1]  # change to 2 if external display

        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)

        # BGRA → BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame


def get_combined_frame():
    # 1️⃣ Get webcam
    cam = get_webcam_frame()

    # 2️⃣ Get screen
    screen = get_screen_frame()

    # 3️⃣ Resize webcam to match screen height
    h, w, _ = screen.shape
    cam = cv2.resize(cam, (int(w * 0.4), h))

    # 4️⃣ Combine horizontally
    combined = np.hstack((cam, screen))

    return combined

