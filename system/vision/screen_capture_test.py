import mss
import numpy as np
import cv2
import time

def capture_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        img = np.array(sct.grab(monitor))
        return img[:, :, :3]

print("📸 Screen capture started. Press Q or Ctrl+C to stop.")

while True:
    screen = capture_screen()
    cv2.imshow("Live Screen Snapshot", screen)

    key = cv2.waitKey(1)
    if key == ord('q'):
        break

    time.sleep(2)

cv2.destroyAllWindows()

