import cv2
from yolo_v8_detector import detect_objects_yolov8

img = cv2.imread("E:/Master 2 2025/reconnaissance/projet_RF/Exam-Surveillance-master/action_model/frame_00002.jpg")
frame, detections = detect_objects_yolov8(img)

print("Détections :", detections)

cv2.imshow("YOLOv8 - Détection", frame)
cv2.waitKey(0)
cv2.destroyAllWindows()
