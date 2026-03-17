"""
train_model.py - Trains the Random Forest model and saves it.
Run this once before starting the app: python train_model.py
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# ── Load Data ─────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "student_data.csv")

df = pd.read_csv(DATA_PATH)
print(f"Loaded {len(df)} records")
print(df.head(3))

# ── Feature Engineering ────────────────────────────────────────────────────
# Encode behavior column
behavior_enc = LabelEncoder()
df["behavior_encoded"] = behavior_enc.fit_transform(df["behavior"])

# Calculate assignment average (all scaled 0-50 → convert to %)
df["assignment_avg"] = ((df["assignment1"] + df["assignment2"] + df["assignment3"]) / 3 / 50) * 100

# Calculate quiz average (quiz max 20 each → convert to %)
df["quiz_avg"] = ((df["quiz1"] + df["quiz2"]) / 2 / 20) * 100

# Midterm as percentage (max 50)
df["midterm_pct"] = (df["midterm_score"] / 50) * 100

# Features used for prediction
FEATURES = [
    "attendance_percent",
    "assignment_avg",
    "quiz_avg",
    "midterm_pct",
    "study_hours_per_day",
    "behavior_encoded",
    "semester"
]

X = df[FEATURES]
y = df["grade"]

# ── Train / Test Split ─────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── Train Random Forest ────────────────────────────────────────────────────
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=12,
    min_samples_split=4,
    random_state=42
)
model.fit(X_train, y_train)

# ── Evaluate ───────────────────────────────────────────────────────────────
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\nModel Accuracy: {acc * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# ── Save Model & Encoder ───────────────────────────────────────────────────
MODEL_PATH = os.path.join(BASE_DIR, "model", "grade_model.pkl")
ENC_PATH   = os.path.join(BASE_DIR, "model", "behavior_encoder.pkl")
FEAT_PATH  = os.path.join(BASE_DIR, "model", "features.pkl")

with open(MODEL_PATH, "wb") as f:
    pickle.dump(model, f)

with open(ENC_PATH, "wb") as f:
    pickle.dump(behavior_enc, f)

with open(FEAT_PATH, "wb") as f:
    pickle.dump(FEATURES, f)

print(f"\nModel saved to: {MODEL_PATH}")
print("Done! You can now run:  python app.py")
