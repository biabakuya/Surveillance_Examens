import os
from model.database import db

project_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(project_dir, '..', "database.db"))

# Classe Instructor (Enseignant)
class Instructor(db.Model):
    __tablename__ = "Instructor"  
    instructor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)

# Classe Course (Cours)
class Course(db.Model):
    __tablename__ = "Course"  
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  
    course_name = db.Column(db.String(100), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey("Instructor.instructor_id"), nullable=False)  
    cr_hours = db.Column(db.Integer, nullable=False)

    # Relation simplifiée
    instructor = db.relationship("Instructor", backref="courses")

    def __repr__(self):
        return "<Course: {}>".format(self.course_name)

# Classe Student (Étudiant)
class Student(db.Model):
    __tablename__ = "Student"
    student_id = db.Column(db.String(50), unique=True, nullable=False, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    ph_number = db.Column(db.String(80), unique=True, nullable=False)
    
    detections = db.relationship('DetectionAlert', backref='student', lazy=True)

    def __repr__(self):
        return "<Student: {}>".format(self.name)

# Classe Room (Salle)
class Room(db.Model):
    __tablename__ = "Room"
    room_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_code = db.Column(db.String(80), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    stream_address = db.Column(db.String(200), nullable=False)
    output_port = db.Column(db.String(200), nullable=False)

    exams = db.relationship('Exam', backref='room', lazy=True)

    def __repr__(self):
        return "<Room: {}>".format(self.room_code)

# Classe Exam (Examen)
class Exam(db.Model):
    __tablename__ = "Exam"
    exam_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    time_slot = db.Column(db.String(80), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('Room.room_id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('Course.course_id'), nullable=False)
    facenetStatus = db.Column(db.Integer, nullable=False)
    duration = db.Column(db.Integer, nullable=True)

    detections = db.relationship('DetectionAlert', backref='exam', lazy=True)

    def __repr__(self):
        return "<Exam: {}>".format(self.exam_id)

# Classe DetectionAlert (Détection d’alerte)
class DetectionAlert(db.Model):
    __tablename__ = "DetectionAlert"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('Exam.exam_id'), nullable=False)
    student_id = db.Column(db.String(50), db.ForeignKey('Student.student_id'), nullable=False)
    det_type = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50))

    frames = db.relationship("FrameData", backref="detection", lazy=True)

# Classe FrameData (Données des images capturées)
class FrameData(db.Model):
    __tablename__ = "FrameData"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    frameID = db.Column(db.String(30), nullable=False)
    detection_id = db.Column(db.Integer, db.ForeignKey("DetectionAlert.id"), nullable=False)

# Fonction pour initialiser la base de données
def init_db():
    """Crée toutes les tables si elles n'existent pas encore."""
    db.create_all()

# Exécuter la création si le script est exécuté directement
if __name__ == '__main__':
    init_db()
