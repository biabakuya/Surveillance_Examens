# 🎓 surveillance des Examens

**Système de surveillance intelligente des examens en salle de classe en temps réel.**

## 📸 Fonctionnalités

- Détection des personnes avec YOLOv8
- Détection de comportements suspects :
  - Utilisation du téléphone
  - Mouvements de tête anormaux
  - Échanges de documents
- Notifications visuelles à l’écran
- Interface web en Flask pour visualisation en direct
- Statistiques de tricheries

## ⚙️ Technologies utilisées

- Python
- Flask
- OpenCV
- PyTorch
- YOLOv8 (Ultralytics)

## 🚀 Lancer l'application

```bash
# Créer un environnement virtuel (facultatif mais recommandé)
python -m venv venv
source venv/bin/activate  # ou venv\Scripts\activate sous Windows

# Installer les dépendances
pip install -r requirements.txt

# Démarrer le serveur Flask
python portal.py
