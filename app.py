"""
app.py — Main Flask application for Student Grading Prediction System
Run with: python app.py
Then open: http://127.0.0.1:5000
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import pandas as pd
import pickle
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = "sgps_secret_2025"

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DATA_PATH  = os.path.join(BASE_DIR, "data", "student_data.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model", "grade_model.pkl")
ENC_PATH   = os.path.join(BASE_DIR, "model", "behavior_encoder.pkl")
FEAT_PATH  = os.path.join(BASE_DIR, "model", "features.pkl")
PRED_PATH  = os.path.join(BASE_DIR, "data", "predictions.json")

# ── Load ML model once at startup ─────────────────────────────────────────
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)
with open(ENC_PATH, "rb") as f:
    behavior_enc = pickle.load(f)
with open(FEAT_PATH, "rb") as f:
    FEATURES = pickle.load(f)

# ── Demo users (teacher / admin / student) ────────────────────────────────
USERS = {
    "admin":   {"password": "admin123",   "role": "admin",   "name": "Admin User"},
    "teacher": {"password": "teacher123", "role": "teacher", "name": "Hikmat Rokaya"},
    "sahaj":   {"password": "sahaj123",   "role": "student", "name": "Sahaj Koirala",  "roll": "BCA2020001"},
    "rohan":   {"password": "rohan123",   "role": "student", "name": "Rohan Mishra",   "roll": "BCA2020002"},
}

# ── Helper Functions ───────────────────────────────────────────────────────

def load_students():
    df = pd.read_csv(DATA_PATH)
    return df

def save_prediction(record):
    """Append a new prediction record to predictions.json"""
    preds = []
    if os.path.exists(PRED_PATH):
        with open(PRED_PATH) as f:
            try: preds = json.load(f)
            except: preds = []
    preds.append(record)
    with open(PRED_PATH, "w") as f:
        json.dump(preds, f, indent=2)

def load_predictions():
    if not os.path.exists(PRED_PATH):
        return []
    with open(PRED_PATH) as f:
        try: return json.load(f)
        except: return []

def predict_grade(attendance, assignment1, assignment2, assignment3,
                  quiz1, quiz2, midterm, study_hours, behavior, semester):
    """Run ML model and return predicted grade + confidence"""
    assignment_avg = ((assignment1 + assignment2 + assignment3) / 3 / 50) * 100
    quiz_avg       = ((quiz1 + quiz2) / 2 / 20) * 100
    midterm_pct    = (midterm / 50) * 100

    try:
        beh_enc = behavior_enc.transform([behavior])[0]
    except:
        beh_enc = 1  # fallback to "Good"

    X = pd.DataFrame([{
        "attendance_percent":  attendance,
        "assignment_avg":      assignment_avg,
        "quiz_avg":            quiz_avg,
        "midterm_pct":         midterm_pct,
        "study_hours_per_day": study_hours,
        "behavior_encoded":    beh_enc,
        "semester":            semester
    }])[FEATURES]

    grade       = model.predict(X)[0]
    probas      = model.predict_proba(X)[0]
    confidence  = round(max(probas) * 100, 1)

    # Estimated final score from features
    est_score = round(
        attendance * 0.15 +
        assignment_avg * 0.25 +
        quiz_avg * 0.20 +
        midterm_pct * 0.25 +
        min(study_hours * 2, 20) * 0.15, 1
    )
    return grade, confidence, est_score

def grade_color(grade):
    colors = {"A+": "#1a7a1a", "A": "#2e8b2e", "B+": "#2060b0",
              "B": "#3070c0", "C+": "#e07800", "C": "#e09000",
              "D": "#c03000", "F": "#990000"}
    return colors.get(grade, "#555555")

def login_required(role=None):
    """Decorator-like check (used inline in routes)"""
    if "user" not in session:
        return False
    if role and session["user"]["role"] != role:
        return False
    return True

# ══════════════════════════════════════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "").strip()
        user = USERS.get(username)
        if user and user["password"] == password:
            session["user"] = {
                "username": username,
                "name":     user["name"],
                "role":     user["role"],
                "roll":     user.get("roll", "")
            }
            flash(f"Welcome back, {user['name']}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    df    = load_students()
    preds = load_predictions()
    role  = session["user"]["role"]

    # Stats
    total      = len(df)
    grade_dist = df["grade"].value_counts().to_dict()
    avg_score  = round(df["final_score"].mean(), 1)
    at_risk    = len(df[df["final_score"] < 40])
    avg_attend = round(df["attendance_percent"].mean(), 1)

    # Recent predictions (last 5)
    recent_preds = preds[-5:][::-1]

    return render_template("dashboard.html",
        total=total, grade_dist=grade_dist, avg_score=avg_score,
        at_risk=at_risk, avg_attend=avg_attend,
        recent_preds=recent_preds, role=role,
        grade_dist_json=json.dumps(grade_dist)
    )


@app.route("/students")
def students():
    if "user" not in session:
        return redirect(url_for("login"))

    df = load_students()
    search = request.args.get("search", "").strip()
    grade_filter = request.args.get("grade", "")
    sem_filter = request.args.get("semester", "")

    if search:
        df = df[df["name"].str.contains(search, case=False) |
                df["roll_number"].str.contains(search, case=False)]
    if grade_filter:
        df = df[df["grade"] == grade_filter]
    if sem_filter:
        df = df[df["semester"] == int(sem_filter)]

    records = df.head(100).to_dict("records")
    grades  = sorted(load_students()["grade"].unique())
    return render_template("students.html",
        records=records, search=search,
        grade_filter=grade_filter, sem_filter=sem_filter,
        grades=grades, total=len(df)
    )


@app.route("/student/<roll>")
def student_detail(roll):
    if "user" not in session:
        return redirect(url_for("login"))

    df = load_students()
    row = df[df["roll_number"] == roll]
    if row.empty:
        flash("Student not found.", "warning")
        return redirect(url_for("students"))

    student = row.iloc[0].to_dict()
    student["grade_color"] = grade_color(student["grade"])

    # Peer comparison (same semester)
    peers = df[df["semester"] == student["semester"]]
    student["sem_avg"] = round(peers["final_score"].mean(), 1)
    student["sem_rank"] = int((peers["final_score"] > student["final_score"]).sum()) + 1
    student["sem_total"] = len(peers)

    return render_template("student_detail.html", student=student)


@app.route("/predict", methods=["GET", "POST"])
def predict():
    if "user" not in session:
        return redirect(url_for("login"))

    result = None
    if request.method == "POST":
        try:
            name       = request.form.get("name", "Unknown")
            roll       = request.form.get("roll", "N/A")
            attendance = float(request.form["attendance"])
            a1         = float(request.form["assignment1"])
            a2         = float(request.form["assignment2"])
            a3         = float(request.form["assignment3"])
            q1         = float(request.form["quiz1"])
            q2         = float(request.form["quiz2"])
            midterm    = float(request.form["midterm"])
            study_hrs  = float(request.form["study_hours"])
            behavior   = request.form["behavior"]
            semester   = int(request.form["semester"])

            grade, confidence, est_score = predict_grade(
                attendance, a1, a2, a3, q1, q2, midterm, study_hrs, behavior, semester
            )

            result = {
                "name": name, "roll": roll,
                "grade": grade, "confidence": confidence,
                "est_score": est_score,
                "color": grade_color(grade),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            # Save prediction
            save_prediction({**result, "inputs": {
                "attendance": attendance, "assignment1": a1, "assignment2": a2,
                "assignment3": a3, "quiz1": q1, "quiz2": q2,
                "midterm": midterm, "study_hours": study_hrs,
                "behavior": behavior, "semester": semester
            }})
            flash(f"Prediction complete for {name}!", "success")

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template("predict.html", result=result)


@app.route("/predictions")
def predictions():
    if "user" not in session:
        return redirect(url_for("login"))
    preds = load_predictions()[::-1]   # newest first
    return render_template("predictions.html", preds=preds)


@app.route("/report")
def report():
    if "user" not in session:
        return redirect(url_for("login"))
    df = load_students()

    # Grade distribution
    grade_dist = df["grade"].value_counts().sort_index().to_dict()

    # Semester-wise average
    sem_avg = df.groupby("semester")["final_score"].mean().round(1).to_dict()

    # Behavior vs score
    beh_avg = df.groupby("behavior")["final_score"].mean().round(1).to_dict()

    # Attendance buckets
    df["att_bucket"] = pd.cut(df["attendance_percent"],
        bins=[0,50,60,70,80,90,100],
        labels=["<50%","50-60%","60-70%","70-80%","80-90%","90-100%"])
    att_score = df.groupby("att_bucket", observed=True)["final_score"].mean().round(1).to_dict()
    att_score = {str(k): v for k, v in att_score.items()}

    at_risk_students = df[df["final_score"] < 40][
        ["name","roll_number","semester","final_score","grade","attendance_percent"]
    ].head(20).to_dict("records")

    return render_template("report.html",
        grade_dist=json.dumps(grade_dist),
        sem_avg=json.dumps(sem_avg),
        beh_avg=json.dumps(beh_avg),
        att_score=json.dumps(att_score),
        at_risk=at_risk_students,
        total=len(df),
        avg_score=round(df["final_score"].mean(), 1),
        pass_rate=round(len(df[df["final_score"] >= 40]) / len(df) * 100, 1),
    )


@app.route("/api/predict", methods=["POST"])
def api_predict():
    """Simple JSON API endpoint for prediction"""
    data = request.json
    try:
        grade, conf, score = predict_grade(
            data["attendance"], data["assignment1"], data["assignment2"],
            data["assignment3"], data["quiz1"], data["quiz2"],
            data["midterm"], data["study_hours"], data["behavior"], data["semester"]
        )
        return jsonify({"grade": grade, "confidence": conf, "estimated_score": score})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


# ── Run ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 55)
    print("  Student Grading Prediction System")
    print("  Open your browser: http://127.0.0.1:5000")
    print("=" * 55)
    print("  Login credentials:")
    print("  admin   / admin123")
    print("  teacher / teacher123")
    print("  sahaj   / sahaj123")
    print("  rohan   / rohan123")
    print("=" * 55)
    app.run(debug=True, port=5000)
