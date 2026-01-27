import cv2

_cap = cv2.VideoCapture(0)

def get_webcam_frame():
    """
    Returns a single webcam frame as numpy array (BGR)
    """
    if not _cap.isOpened():
        return None

    ret, frame = _cap.read()
    if not ret:
        return None

    return frame
