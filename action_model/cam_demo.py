import torch
import cv2
import numpy as np
import pickle as pkl
import random
import pandas as pd
import time
import torch.nn as nn
from torch.autograd import Variable
import sys
import os
import math

from darknet import Darknet
from util import load_classes, write_results
from preprocess import prep_image, inp_to_image

from action_model.yolo_v8_detector import detect_objects_yolov8

# === Setup environnement ===
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

CUDA = torch.cuda.is_available()

# === Charger le modèle YOLOv3 (non utilisé ici mais gardé si besoin)
cfgfile = "action_model/cfg/yolov3.cfg"
weightsfile = "action_model/yolov3.weights"
model = Darknet(cfgfile)
model.load_weights(weightsfile)
model.eval()
if CUDA:
    model.cuda()

# === Paramètres
num_classes = 80
bbox_attrs = 5 + num_classes
confidence = 0.25
nms_thesh = 0.4
inp_dim = int(model.net_info["height"])
classes = load_classes("data/coco.names")
colors = pkl.load(open("pallete", "rb"))

# === Suivi des positions pour détecter les mouvements
last_positions = []
movement_counter = 0
movement_threshold = 2  # nombre de frames consécutives
movement_display_duration = 15  # frames d'affichage
movement_display_timer = 0

# === Suivi des objets pour échange
last_object_positions = {}
exchange_alert_display_timer = 0


def euclidean_distance(p1, p2):
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

# === Traitement de chaque frame ===
def process_frame(frame):
    global last_positions, movement_counter, movement_display_timer, last_object_positions, exchange_alert_display_timer
    frame, detections = detect_objects_yolov8(frame, score_thresh=0.25)

    current_centers = []
    object_positions = []

    for det in detections:
        x1, y1, x2, y2, cls_id, score = det
        label = classes[int(cls_id)] if int(cls_id) < len(classes) else str(cls_id)
        center = (int((x1 + x2) / 2), int((y1 + y2) / 2))

        if label == "person":
            current_centers.append(center)
        elif label in ["book", "cell phone", "remote", "laptop"]:
            object_positions.append(center)

    # Mouvement de tête
    if len(last_positions) == len(current_centers):
        moved = any(euclidean_distance(c1, c2) > 15 for c1, c2 in zip(current_centers, last_positions))
        if moved:
            movement_counter += 1
        else:
            movement_counter = 0

        if movement_counter >= movement_threshold:
            movement_display_timer = movement_display_duration
            movement_counter = 0

    if movement_display_timer > 0:
        cv2.putText(frame, "Mouvement de tete detecte !", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)
        movement_display_timer -= 1

    last_positions = current_centers

    # Détection d’échange suspect
    for obj_pos in object_positions:
        for person_pos in current_centers:
            dist = euclidean_distance(obj_pos, person_pos)
            if dist < 80:  # seuil de proximité suspecte
                exchange_alert_display_timer = 30
                break

    if exchange_alert_display_timer > 0:
        cv2.putText(frame, "Suspicion d'echange de copies !", (30, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        exchange_alert_display_timer -= 1

    return frame

# === Programme principal ===
if __name__ == "__main__":
    print(">>> Lancement de la detection en direct")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print(" Erreur : impossible d'acceder a la camera.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print(" Impossible de lire la frame")
            break

        result = process_frame(frame)
        cv2.imshow("Detection avec mouvement de tete", result)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
     # === Affichage final des statistiques ===
    print("\n==== STATISTIQUES DE TRICHERIE ====")
    for key, value in detection_stats.items():
        print(f"{key} : {value} fois")
