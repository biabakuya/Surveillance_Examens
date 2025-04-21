from __future__ import division
from flask import Flask, render_template, request, jsonify, Response, send_from_directory
from model.database import db
from model.Model import *
import os
import cv2
import numpy as np
import struct
import time
import socket

import torch
import pickle as pkl

from action_model.darknet import Darknet
from action_model.util import load_classes, write_results
from action_model.cam_demo import process_frame
from action_model.yolo_v8_detector import detect_objects_yolov8

# Charger le modèle
cfgfile = os.path.abspath(os.path.join("action_model", "cfg", "yolov3.cfg"))
weightsfile = os.path.abspath(os.path.join("action_model", "yolov3.weights"))

model = Darknet(cfgfile)
model.load_weights(weightsfile)
model.eval()  # Mode évaluation (désactive le dropout)


# Charger les classes
class_names = load_classes(os.path.join("action_model", "data", "coco.names"))


# Paramètres du modèles
confidence_threshold = 0.5
nms_threshold = 0.4


# Initialisation de l'application Flask
app = Flask(__name__)
project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, "database.db"))
app.config["SQLALCHEMY_DATABASE_URI"] = database_file

# Initialisation de la base de données
db.init_app(app)
with app.app_context():
    db.create_all()

# Variables pour la gestion du flux vidéo
MAX_DGRAM = 2**16  # Taille max des paquets UDP
pp = 0  # Port de sortie vidéo

# ** Gestion du buffer UDP**
def dump_buffer(s):
    """Vide le buffer UDP pour éviter les retards"""
    start = time.time()
    while True:
        if (time.time() - start) >= 15:
            s.close()
            return False
        seg, addr = s.recvfrom(MAX_DGRAM)
        if struct.unpack("B", seg[0:1])[0] == 1:
            print("🛠 Buffer vidé.")
            break
    return True

# **Routes de l’application**
@app.route('/')
@app.route('/login')
def hello():
    return render_template('login.html')

@app.route('/home')
def homescreen():
    detections = DetectionAlert.query.all()
    details = []
    
    if detections:
        for det in detections:
            if det.exam and det.exam.course and det.exam.room:
                details.append({
                    's_name': det.student.name,
                    'c_name': det.exam.course.course_name,
                    'r_name': det.exam.room.room_code
                })
    
    return render_template('homescreen.html', details=details)

@app.route('/live_video/<string:video_id>')
def live_video(video_id):
    Examdetails = Exam.query.filter_by(exam_id=video_id).first()
    if not Examdetails:
        print(f" Aucun examen trouvé pour ID {video_id}")
        return "Erreur : Aucun examen trouvé.", 404

    coursedetails = Course.query.filter_by(course_id=Examdetails.course_id).first()
    if not coursedetails:
        print(f"Aucun cours trouvé pour examen ID {video_id}")
        return "Erreur : Aucun cours associé.", 404

    roomdetails = Room.query.filter_by(room_id=Examdetails.room_id).first()
    if not roomdetails:
        print(f" Aucune salle trouvée pour examen ID {video_id}")
        return "Erreur : Aucune salle associée.", 404

    global pp
    pp = roomdetails.output_port

    # Liste des autres examens
    OtherExam = Exam.query.filter(Exam.exam_id != video_id).all()
    temp = [{"href": f"/live_video/{exam.exam_id}", "id": exam.exam_id} for exam in OtherExam]

    return render_template(
        'live_video.html', 
        Examdetails=Examdetails, 
        coursedetails=coursedetails, 
        roomdetails=roomdetails, 
        OtherExam=OtherExam, 
        temp=temp, 
        id=video_id
    )


# **Gestion du flux vidéo**
def get_frame(source, is_udp=False, detect=False):
    if is_udp:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', int(pp)))
        dat = b''
        flag = dump_buffer(s)

        while flag:
            seg, addr = s.recvfrom(MAX_DGRAM)
            if struct.unpack("B", seg[0:1])[0] > 1:
                dat += seg[1:]
            else:
                dat += seg[1:]
                frame = cv2.imdecode(np.frombuffer(dat, dtype=np.uint8), 1)

                if detect:
                    frame, detections = detect_objects_yolov8(frame)  # Ajout de la détection

                ret, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                dat = b''
    else:
        cap = cv2.VideoCapture(source)
        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            
            if detect:
                frame, _ = detect_objects_yolov8(frame)  # Ajout de la détection

            ret, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        cap.release()

def detect_objects(frame):
    """Détecte les objets et affiche un message en fonction de la situation."""
    img = cv2.resize(frame, (608, 608))  # Redimensionner pour YOLO
    img_ = img[:, :, ::-1].transpose((2, 0, 1))  # Convertir BGR → RGB
    img_ = torch.from_numpy(img_).float().div(255.0).unsqueeze(0)

    with torch.no_grad():
        detections = model(img_)

    detections = write_results(detections, confidence_threshold, 80, nms=True, nms_conf=nms_threshold)

    if isinstance(detections, int):  # Aucun objet détecté
        return frame

    detections[:, 1:5] = detections[:, 1:5] * frame.shape[1] / 608  # Ajuster la taille

    personne_detectee = False
    telephone_detecte = False
    mouvement_suspect = False  # Indicateur de mouvement suspect

    for det in detections:
        x1, y1, x2, y2, conf, cls = map(int, det[:6])
        label = f"{class_names[cls]} {conf:.2f}"
        
        if class_names[cls] == "person":
            personne_detectee = True  # Une personne a été détectée

        if class_names[cls] == "cell phone":
            telephone_detecte = True  # Un téléphone a été détecté

        # Détecter des mouvements suspects (ex: tête tournée, rire, parler)
        if class_names[cls] in ["hand", "mouth", "face"]:
            mouvement_suspect = True

        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Ajout des notifications en fonction des détections
    if personne_detectee:
        cv2.putText(frame, "Étudiant présent", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    if telephone_detecte:
        cv2.putText(frame, "Téléphone détecté ! Tricherie possible !", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

    if mouvement_suspect:
        cv2.putText(frame, " Mouvement suspect détecté !", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 165, 255), 3)

    return frame

@app.route('/detect_feed/<int:room_id>')
def detect_feed(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if not room:
        return "Erreur : Salle non trouvée.", 404

    return Response(get_frame(room.stream_address, detect=True), mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/video_feed/<int:room_id>')
def video_feed(room_id):
    room = Room.query.filter_by(room_id=room_id).first()
    if not room:
        return "Erreur : Salle non trouvée.", 404

    global pp
    pp = room.output_port

    #  Sélection de la source vidéo
    if room.stream_address == "local":
        return Response(get_frame(0,detect=True), mimetype='multipart/x-mixed-replace; boundary=frame')
    elif room.stream_address.startswith("http"):
        return Response(get_frame(room.stream_address,detect=True), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response(get_frame(room.stream_address, is_udp=True,detect=True), mimetype='multipart/x-mixed-replace; boundary=frame')
    

@app.route('/detect_video/<int:room_id>')
def detect_video(room_id):
    print(f"Debug : Détection activée pour la salle {room_id}")
    room = Room.query.filter_by(room_id=room_id).first()
    if not room:
        print("Erreur : Salle non trouvée")
        return "Erreur : Salle non trouvée.", 404

    print( "Debug : Connexion à la webcam")
    
    def generate():
        cap = cv2.VideoCapture(1)  # 0 pour webcam locale, changer si besoin
        while True:
            success, frame = cap.read()
            if not success:
                print(" Erreur : Impossible de lire la vidéo")
                break
            
            print("Debug : Image capturée, appliquons la détection")

            # Ici, applique la détection si besoin
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        cap.release()

    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')


#####################################################################
#  **Mise à jour de la base après détection**
@app.route("/updateDatabase", methods=['POST'])
def updateDatabase():
    x = request.form['value']
    did = int(request.form['did']) 
    db.session.query(DetectionAlert).filter_by(id=did).update({DetectionAlert.status: x})
    db.session.commit()
    return jsonify({'value': x})

@app.route("/exams", methods=["GET", "POST"])
def exams():
    allCourses = Course.query.all()
    allRooms = Room.query.all()
    exams = Exam.query.all()
    return render_template("Examination.html", exams=exams, allCourses=allCourses, allRooms=allRooms)

@app.route("/changestatus", methods=["GET", "POST"])
def change():
    detected = None
    exam_detected = None
    course_detected = None
    frame1 = []

    if request.method == "POST":
        det_id = request.form.get("detection_id")
        exam_id = request.form.get("exam_id")

        if exam_id:
            detected = DetectionAlert.query.filter_by(exam_id=exam_id, student_id='unknown').first()
        else:
            detected = DetectionAlert.query.filter_by(id=det_id).first()
        if detected:
            exam_detected = Exam.query.filter_by(exam_id=detected.exam_id).first()
            course_detected = Course.query.filter_by(course_id=exam_detected.course_id).first()
            frame1 = FrameData.query.filter_by(DetectionID=detected.id).all()

    return render_template('changestatus.html', detected=detected, exam_detected=exam_detected, course_detected=course_detected, frame=frame1)

##################################################################

#  **Accès aux fichiers**
@app.route('/action_model/database/<string:name>/<path:filename>')
def Custom_Static(name, filename):
    assets_folder = os.path.join(app.root_path, 'action_model//database', name)
    return send_from_directory(assets_folder, filename)

#  **Démarrage de l'application**
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
