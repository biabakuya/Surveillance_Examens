
# Exam Surveillance System 

This project implements an intelligent proctoring system using real-time object detection and face recognition to detect suspicious behaviors during in-person examinations.

##Key Features

- **Real-time detection** of:
  - Mobile phones
  - Head movements
  - Interaction between students (e.g. paper exchange)
- **Face recognition** using FaceNet to identify students involved in alerts
- **Alert generation** with annotated images and timestamps
- **Web interface** (Flask) for visualizing alerts and reports

## Technologies Used

| Component         | Technology         |
|------------------|--------------------|
| Object Detection | YOLOv8 (Ultralytics) |
| Face Recognition | FaceNet (Keras .h5 model) |
| Computer Vision  | OpenCV             |
| Deep Learning    | PyTorch            |
| Backend          | Flask + SQLAlchemy |
| Frontend         | HTML/CSS/JS + Bootstrap |
| Database         | SQLite             |

## Dataset Summary

- **Total Images**: 800
  - Training (YOLOv8): 560
  - Validation: 120
  - Test: 120
- **FaceNet base**: 30 registered faces

## Architecture Overview

1. **Camera** captures real-time footage
2. **YOLOv8** detects people and banned objects
3. **FaceNet** identifies detected faces via cosine similarity
4. **Behavior Analysis** determines if cheating is likely
5. **Flask App** displays alerts and exam session logs

##  Sample Results

> Add screenshots in the `docs/` folder and reference them here

##  Model Performance

| Model   | Metric               | Score     |
|---------|----------------------|-----------|
| YOLOv8  | mAP@0.5              | 89.3%     |
|         | Precision            | 87.5%     |
|         | Recall               | 84.2%     |
| FaceNet | Recognition Accuracy | 94%       |
|         | False Positive Rate  | 3–5%      |
|         | Inference Time       | ~30ms     |

## Installation

```bash
git clone https://github.com/yourname/exam-surveillance-system.git
cd exam-surveillance-system
pip install -r requirements.txt
```

> Avoid pushing large files like `.h5`, `.pt`, or `venv/`. Use `.gitignore` or Git LFS.

## Running the App

```bash
python portal.py
```

Then open [http://localhost:5000](http://localhost:5000)

##  License

This project is licensed for academic and research use.
