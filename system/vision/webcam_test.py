import cv2

cap = cv2.VideoCapture(0)

print("🎥 Webcam started. Press q to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Webcam", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
