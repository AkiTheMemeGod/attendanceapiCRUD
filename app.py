from flask import Flask, request, render_template, jsonify, g
import sqlite3 as sq
from assets import Database, Fetch  # Your classes

app = Flask(__name__)

# Database connection setup
def get_db():
    if "db" not in g:
        g.db = sq.connect("student.db")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def homepage():
    connection = get_db()
    fetcher = Fetch(connection)
    student_count = len(fetcher.fetch_all_rolls())

    subject_count = 5

    return render_template("home.html", student_count=student_count, subject_count=subject_count)

@app.route("/admin")
def admin_page():
    connection = get_db()
    fetcher = Fetch(connection)
    all_rolls = fetcher.fetch_all_rolls()
    return render_template("admin.html", rolls=all_rolls)

@app.route("/add_student", methods=["POST"])
def add_student():
    connection = get_db()
    db = Database(connection)
    data = request.form
    rollno = data.get("rollno")
    name = data.get("name")
    email = data.get("email")
    db.rollinit(rollno, name, email)
    return "Student added successfully!"

@app.route("/mark_attendance", methods=["POST"])
def mark_attendance():
    connection = get_db()
    db = Database(connection)
    data = request.form
    rollno = data.get("rollno")
    sub = data.get("subject")
    db.attendance(rollno, sub)
    return f"Attendance marked for rollno {rollno} for subject {sub}"


@app.route("/fetch_attendance", methods=["GET"])
def fetch_attendance():
    connection = get_db()
    fetcher = Fetch(connection)
    all_rolls = fetcher.fetch_all_rolls()

    # Fetch all attendance for all students
    attendance_data = []
    for rollno in all_rolls:
        student_data = fetcher.fetch_all_attendance(rollno)
        attendance_data.append({
            "rollno": rollno,
            "name": student_data[1],  # Assuming name is in the 2nd column
            "attendance": student_data[3:]  # Assuming attendance starts from the 3rd column
        })

    return render_template("view_attendance.html", attendance_data=attendance_data)


@app.route("/reset_attendance", methods=["POST"])
def reset_attendance():
    connection = get_db()
    db = Database(connection)
    data = request.form
    rollno = data.get("rollno")
    sub = data.get("subject")
    db.reset_attendance(rollno, sub)
    return f"Attendance reset for rollno {rollno} for subject {sub}"

@app.route("/mark_only_absent", methods=["POST"])
def mark_only_absent():
    roll = request.form.get("roll").split(',')  # List of roll numbers
    subject = request.form.get("subject")
    db = Database(get_db())  # Create Database instance
    db.mark_only_absent(roll, subject)  # Call the method to mark attendance
    return "Attendance marked as absent for selected roll numbers"

@app.route("/mark_only_present", methods=["POST"])
def mark_only_present():
    roll = request.form.get("roll").split(',')  # List of roll numbers
    subject = request.form.get("subject")
    db = Database(get_db())  # Create Database instance
    db.mark_only_present(roll, subject)  # Call the method to mark attendance
    return "Attendance marked as present for selected roll numbers"



if __name__ == "__main__":
    app.run(debug=True)
