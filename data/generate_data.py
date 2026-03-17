"""
Run this once to generate the student dataset.
It creates student_data.csv with 500 student records.
"""

import csv
import random
import os

random.seed(42)

names = [
    "Aarav Sharma","Bijay Thapa","Chandan Rai","Dipika Gurung","Elina Shrestha",
    "Farhan Ansari","Gita Magar","Hari Poudel","Isha Tamang","Janak Karki",
    "Kamala Bist","Lokesh Neupane","Manisha Adhikari","Nabin Dahal","Ojha Prasad",
    "Puja Basnet","Qasim Ali","Rita Lama","Sagar Koirala","Tina Joshi",
    "Uday Bhattarai","Vijay Subedi","Wangchuk Sherpa","Xina Rana","Yash Mishra",
    "Zara Khan","Amrit Regmi","Binita Dhakal","Chitra Oli","Deepak Acharya",
    "Elisha Pandey","Fumiko Rai","Ganesh Thapa","Hina Bajracharya","Indra Limbu",
    "Jyoti Chaudhary","Kiran Bhandari","Laxmi Mahat","Manoj Khatri","Nisha Pokhrel",
    "Om Prakash","Prem Bahadur","Qumar Hussain","Rupa Giri","Suresh KC",
    "Tulasa Parajuli","Ujjwal Mahato","Vandana Singh","Wrisha Tamang","Yuvraj Chand"
]

def generate_grade(attendance, assignment_avg, quiz_avg, midterm, study_hours):
    """Realistic grade based on input factors"""
    score = (
        attendance * 0.15 +
        assignment_avg * 0.25 +
        quiz_avg * 0.20 +
        midterm * 0.25 +
        min(study_hours * 2, 20) * 0.15
    )
    noise = random.uniform(-3, 3)
    final = min(100, max(0, score + noise))
    return round(final, 1)

def score_to_grade(score):
    if score >= 90: return "A+"
    elif score >= 80: return "A"
    elif score >= 70: return "B+"
    elif score >= 60: return "B"
    elif score >= 50: return "C+"
    elif score >= 40: return "C"
    elif score >= 35: return "D"
    else: return "F"

rows = []
for i in range(500):
    name = random.choice(names) + f" {i+1}"
    roll = f"BCA{random.randint(2020,2023)}{str(i+1).zfill(3)}"
    semester = random.randint(1, 6)
    attendance = round(random.uniform(40, 100), 1)
    assignment1 = round(random.uniform(20, 50), 1)
    assignment2 = round(random.uniform(20, 50), 1)
    assignment3 = round(random.uniform(20, 50), 1)
    assignment_avg = round((assignment1 + assignment2 + assignment3) / 3 * 2, 1)  # scale to 100
    quiz1 = round(random.uniform(5, 20), 1)
    quiz2 = round(random.uniform(5, 20), 1)
    quiz_avg = round((quiz1 + quiz2) / 20 * 100, 1)
    midterm = round(random.uniform(20, 50), 1) * 2  # scale to 100
    study_hours = round(random.uniform(1, 10), 1)
    behavior = random.choice(["Excellent", "Good", "Average", "Poor"])

    final_score = generate_grade(attendance, assignment_avg, quiz_avg, midterm, study_hours)
    grade = score_to_grade(final_score)

    rows.append({
        "name": name,
        "roll_number": roll,
        "semester": semester,
        "attendance_percent": attendance,
        "assignment1": assignment1,
        "assignment2": assignment2,
        "assignment3": assignment3,
        "quiz1": quiz1,
        "quiz2": quiz2,
        "midterm_score": round(midterm/2, 1),
        "study_hours_per_day": study_hours,
        "behavior": behavior,
        "final_score": final_score,
        "grade": grade
    })

out_path = os.path.join(os.path.dirname(__file__), "student_data.csv")
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print(f"Generated {len(rows)} student records -> {out_path}")
