import cv2
import time
from audio.tts import init_tts, say
from sensors.ultrasonic_serial import SerialUltrasonic

# ======================
# Configuration
# ======================
CONF_THRESHOLD = 0.4   # Minimum confidence to speak
SPEAK_COOLDOWN_S = 1.0
MAX_OBJECTS = 5
OBSTACLE_DANGER_CM = 40
OBSTACLE_WARN_CM = 120

# ======================
# Initialize TTS
# ======================
init_tts(rate=180, volume=1.0)
say("Smart Vision Assistant ready.")

# ======================
# Initialize Ultrasonic Sensor (Serial RX/TX)
# ======================
ultrasonic = SerialUltrasonic(port="/dev/serial0")
say("Ultrasonic sensor initialized.")

# ======================
# Load MobileNet SSD
# ======================
net = cv2.dnn.readNetFromCaffe(
    "models/MobileNetSSD_deploy.prototxt",
    "models/MobileNetSSD_deploy.caffemodel"
)

CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair",
           "cow", "diningtable", "dog", "horse", "motorbike",
           "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]

# ======================
# Initialize USB Webcam
# ======================
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

last_spoken = 0
spoken_objects = set()

# ======================
# Main loop
# ======================
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # -------------------------
        # Ultrasonic distance
        # -------------------------
        dist = ultrasonic.get_distance()
        if dist is not None:
            if dist <= OBSTACLE_DANGER_CM:
                say("Stop. Obstacle very close.")
                time.sleep(0.4)
                continue
            elif dist <= OBSTACLE_WARN_CM:
                now = time.time()
                if now - last_spoken > SPEAK_COOLDOWN_S:
                    say(f"Obstacle at {dist:.1f} centimeters")
                    last_spoken = now

        # -------------------------
        # Object Detection
        # -------------------------
        blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
        net.setInput(blob)
        detections = net.forward()

        objects_detected = []
        for i in range(detections.shape[2]):
            conf = detections[0, 0, i, 2]
            if conf > CONF_THRESHOLD:
                idx = int(detections[0, 0, i, 1])
                label = CLASSES[idx]
                if label not in spoken_objects:
                    objects_detected.append(label)
                    spoken_objects.add(label)

        # Speak detected objects
        if objects_detected:
            now = time.time()
            if now - last_spoken > SPEAK_COOLDOWN_S:
                say(", ".join(objects_detected[:MAX_OBJECTS]))
                last_spoken = now

        # Reset spoken_objects for next frame
        spoken_objects.clear()

        # Optional: Show frame on monitor (remove if headless)
        # cv2.imshow("MobileNet SSD Detection", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

except KeyboardInterrupt:
    say("Stopping Smart Vision Assistant.")

finally:
    cap.release()