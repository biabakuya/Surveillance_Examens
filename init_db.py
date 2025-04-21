from portal import app
from model.database import db
from model.Model import Course,Instructor, Room, Student, Exam, DetectionAlert, FrameData
from sqlalchemy import inspect

with app.app_context():
    print(" Suppression des anciennes tables...")
    db.drop_all()
    db.create_all()

    inspector = inspect(db.engine)
    print("Tables créées :", inspector.get_table_names())

    # Vérifier si les tables sont encore vides
    if not Course.query.first():
        print("Tables vides, insertion des données...")
    
        # Ajout des enseignants
        instructors = [
        Instructor(name="Dr. Ho Tuong Vinh"),  # ID sera généré automatiquement
        Instructor(name="PhD. NGUYEN Manh Hung"),
        Instructor(name="Mm GIANH VIEN"),
    ]
        db.session.add_all(instructors)
        db.session.commit()

        # IMPORTANT : Récupérer les IDs après insertion
        instructors_db = Instructor.query.all()
        instructor_mapping = {instr.name: instr.instructor_id for instr in instructors_db}

        print("Enseignants insérés avec succès !")

        # Ajout des cours
        courses = [
        Course(course_name="Biobiographie", cr_hours=3, instructor_id=instructor_mapping["Dr. Ho Tuong Vinh"]),
        Course(course_name="SMA", cr_hours=3, instructor_id=instructor_mapping["PhD. NGUYEN Manh Hung"]),
        Course(course_name="Reconnaissance de Forme", cr_hours=3, instructor_id=instructor_mapping["Dr. Ho Tuong Vinh"]),
        Course(course_name="Computer Vision", cr_hours=3, instructor_id=instructor_mapping["Mm GIANH VIEN"]),
    ]
        db.session.add_all(courses)
        db.session.commit()

        print(" Cours insérés avec succès !")

        # Ajout des salles
        rooms = [
            Room(room_id=1, room_code='R-206', capacity=50, stream_address="local", output_port=12345),# Caméra locale
            Room(room_id=2, room_code='R-205', capacity=50, stream_address="action_model//v43.mp4", output_port=12345),
            Room(room_id=3, room_code='R-204', capacity=45, stream_address='http://192.168.1.2:5001/video', output_port=12346),
            Room(room_id=4, room_code='S-203', capacity=65, stream_address='http://192.168.1.2:5001/video', output_port=12345),
        ]
        db.session.add_all(rooms)
        db.session.commit()

        # Ajout des étudiants
        students = [
            Student(student_id='k163890', name='BIABA KUYA Jirince', ph_number='0345244524'),
            Student(student_id='k163886', name='BYAOMBE Dieu donne', ph_number='0325689994'),
            Student(student_id='k163863', name='DIALLO Ibrahima', ph_number='0325587555'),
            Student(student_id='k163862', name='EBWALA Priscille', ph_number='0336831008'),
            Student(student_id='k163905', name='HABACK Olivia', ph_number='0325123456'),
            Student(student_id='k163865', name='ISSA Fiti', ph_number='0321200252'),
            Student(student_id='unknown', name='unknown', ph_number='000000000'),
        ]
        db.session.add_all(students)

        # Ajout des examens
        exams = [
            Exam(exam_id=1, time_slot='Wed Apr 8 03:24:00 2020', room_id=1, course_id=2, duration=1, facenetStatus=0),
            Exam(exam_id=2, time_slot='Wed Apr 8 03:25:00 2020', room_id=2, course_id=1, duration=1, facenetStatus=0),
            Exam(exam_id=3, time_slot='Wed Apr 8 03:22:00 2020', room_id=3, course_id=0, duration=1, facenetStatus=0),
        ]
        db.session.add_all(exams)

        db.session.commit()
        print(" Données insérées avec succès !")
    else:
        print(" Données déjà présentes, aucune réinsertion nécessaire.")

