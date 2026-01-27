import cv2
import numpy as np
import mss
from system.vision.webcam import get_webcam_frame

def get_screen_frame():
    with mss.mss() as sct:
        monitor = sct.monitors[1]

        screenshot = sct.grab(monitor)
        frame = np.array(screenshot)

        # BGRA → BGR
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        return frame


def get_combined_frame():
    cam = get_webcam_frame()

    screen = get_screen_frame()

    h, w, _ = screen.shape
    cam = cv2.resize(cam, (int(w * 0.4), h))

    combined = np.hstack((cam, screen))

    return combined