import cv2
import os

# Chemin de la vidéo
video_path = "/home/priscille/github.com/projet_RF/Exam-Surveillance-master/verify"
# Dossier de sortie
output_folder = "/home/priscille/github.com/projet_RF/Exam-Surveillance-master/data/frame"

# Crée le dossier de sortie s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# Charge la vidéo
cap = cv2.VideoCapture(video_path)
frame_num = 0

while True:
    success, frame = cap.read()
    if not success:
        break
    # Sauvegarde la frame en tant qu’image
    frame_filename = os.path.join(output_folder, f"frame{frame_num:05d}.jpg")
    cv2.imwrite(frame_filename, frame)
    frame_num += 1

cap.release()
print(f" Extraction terminée : {frame_num} images enregistrées dans '{output_folder}'")
