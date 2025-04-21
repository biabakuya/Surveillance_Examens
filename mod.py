import cv2
import numpy as np
import os
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Charger le modèle
net = cv2.dnn.readNetFromDarknet("/home/priscille/github.com/projet_RF/Exam-Surveillance-master/action_model/cfg/yolov3.cfg", "/home/priscille/github.com/projet_RF/Exam-Surveillance-master/action_model/yolov3.weights")

# Liste des classes (tu peux modifier selon ton dataset)
classes = ["person", "car", "truck", "motorbike"]  # exemple

# Charger les données de test : images + ground truth
# ==> À adapter selon ta structure de projet
image_dir = "./test_images/"
annotations = {
    "img1.jpg": ["car"],
    "img2.jpg": ["motorbike"],
    # ...
}

# Prédictions et vérités
y_true = []
y_pred = []

for img_name, true_labels in annotations.items():
    img_path = os.path.join(image_dir, img_name)
    img = cv2.imread(img_path)
    height, width = img.shape[:2]

    # Prétraitement YOLO
    blob = cv2.dnn.blobFromImage(img, 1/255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    # Récupérer les noms des couches de sortie
    ln = net.getUnconnectedOutLayersNames()
    layer_outputs = net.forward(ln)

    # Stocker les prédictions
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Ground truth et prédictions
    y_true.append(classes.index(true_labels[0]))  # simplifié pour 1 GT
    if class_ids:
        y_pred.append(class_ids[0])  # simplifié pour 1 prédiction
    else:
        y_pred.append(-1)  # ou une classe "inconnue"

# Nettoyage (supprimer les -1 si tu veux)
filtered_y_true = [y for y, p in zip(y_true, y_pred) if p != -1]
filtered_y_pred = [p for p in y_pred if p != -1]

# Générer la matrice de confusion
cm = confusion_matrix(filtered_y_true, filtered_y_pred)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
disp.plot(cmap='Blues')
plt.title("Matrice de Confusion YOLOv3")
plt.show()
