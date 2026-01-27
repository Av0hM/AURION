import mss
import numpy as np
import cv2

def get_screen_frame():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # MAIN screen
        screenshot = sct.grab(monitor)
        img = np.array(screenshot)
        return cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
