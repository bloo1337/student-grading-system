# Student Grading Prediction System
### Tribhuvan University — United College | BCA 6th Semester Project
**By: Sahaj Koirala & Rohan Mishra | Supervisor: Hikmat Rokaya**

---

## How to Run (Step by Step)

### Step 1 — Install Python
Make sure Python 3.8+ is installed. Check with:
```
python --version
```

### Step 2 — Install Required Libraries
Open terminal/command prompt in this folder and run:
```
pip install -r requirements.txt
```

### Step 3 — Train the ML Model (run only once)
```
python train_model.py
```
This will generate the model files inside the `model/` folder.

### Step 4 — Start the Website
```
python app.py
```

### Step 5 — Open in Browser
Go to: **http://127.0.0.1:5000**

---

## Login Credentials

| Username | Password     | Role    |
|----------|-------------|---------|
| admin    | admin123    | Admin   |
| teacher  | teacher123  | Teacher |
| sahaj    | sahaj123    | Student |
| rohan    | rohan123    | Student |

---

## Features

- **Dashboard** — Stats, grade distribution charts, recent predictions
- **Students** — Browse, search and filter all 500 student records
- **Student Detail** — Individual profile with performance bars and semester rank
- **Predict Grade** — ML-powered grade prediction using Random Forest
- **Predictions Log** — History of all predictions made
- **Analytics Report** — Charts: grade distribution, semester trends, behavior vs score, attendance analysis, at-risk students

---

## Project Structure

```
student_grading_system/
├── app.py                  ← Main Flask app (run this)
├── train_model.py          ← Train ML model (run once)
├── requirements.txt        ← Python dependencies
├── data/
│   ├── generate_data.py    ← Script to regenerate dataset
│   ├── student_data.csv    ← 500 student records
│   └── predictions.json    ← Saved predictions (auto-created)
├── model/
│   ├── grade_model.pkl     ← Trained Random Forest model
│   ├── behavior_encoder.pkl
│   └── features.pkl
└── templates/
    ├── base.html           ← Layout with sidebar
    ├── login.html
    ├── dashboard.html
    ├── students.html
    ├── student_detail.html
    ├── predict.html
    ├── predictions.html
    └── report.html
```

---

## ML Model Details

- **Algorithm:** Random Forest Classifier (200 trees)
- **Features:** Attendance, Assignment avg, Quiz avg, Midterm score, Study hours, Behavior, Semester
- **Target:** Grade (A+, A, B+, B, C+, C, D, F)
- **Accuracy:** ~76% on test set
- **Dataset:** 500 generated student records

---
*Student Grading Prediction System — November 2025*
