
from ultralytics import YOLO

import cv2


DEFAULT_DETECTION_THRESHOLD = 0.15
DEFAULT_IMAGE_SIZE = 1280 #1280
class detector:
    def __init__(self, path_model):
        # Load custom trained model
        self.model = YOLO(path_model)

    def detect(self, image_path, score_thresh):
        results = self.model.predict(image_path, conf = score_thresh)

        # Extract bbox, confidences, labels from the results
        bboxes = results[0].boxes.xyxy.tolist()
        scores = results[0].boxes.conf.tolist()
        labels = results[0].boxes.cls.tolist()

        results = []
        for idx, box in enumerate(bboxes):
            top, left, bottom, right = box
            score = scores[idx]
            label = labels[idx]
            print(' get score:', score)

            top, left, bottom, right = int(top), int(left), int(bottom), int(right)
       
            if score > score_thresh:
                print('detect: label =',int(label), ', score =', f'{score:.2f}')
                results.append([left, top, right, bottom, label, score])
        
        return results


