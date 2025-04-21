from ultralytics import YOLO
import cv2

DEFAULT_DETECTION_THRESHOLD = 0.15

# Charger le modèle YOLOv8 (à ajuster selon ton modèle .pt)
model = YOLO("yolov8n.pt")  # ou yolov8s.pt, yolov8m.pt etc.

def detect_objects_yolov8(frame, score_thresh=DEFAULT_DETECTION_THRESHOLD):
    # Convertir en BGR → RGB si nécessaire
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = model.predict(source=img, conf=score_thresh, verbose=False)
    boxes = results[0].boxes

    detections = []
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        conf = float(box.conf[0])
        cls_id = int(box.cls[0])
        detections.append([int(x1), int(y1), int(x2), int(y2), cls_id, conf])

        # Dessiner sur l’image
        label = f"{model.names[cls_id]} {conf:.2f}"
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.putText(frame, label, (int(x1), int(y1)-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    return frame, detections
