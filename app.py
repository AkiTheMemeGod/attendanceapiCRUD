from flask import Flask, request, render_template, session, redirect, url_for, g, jsonify
import sqlite3 as sq
from assets import Database, Fetch  # Your classes

app = Flask(__name__)

app.secret_key = "your_secret_key"  # Used to secure sessions

# Hardcoded admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

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

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_page"))
        else:
            return render_template("admin_login.html", error="Invalid username or password")
    return render_template("admin_login.html")

# Admin panel route (protected)
@app.route("/admin")
def admin_page():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    connection = get_db()
    fetcher = Fetch(connection)
    all_rolls = fetcher.fetch_all_rolls()
    return render_template("admin.html", rolls=all_rolls)

# Logout route
@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("homepage"))

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


@app.route("/advanced_options", methods=["GET", "POST"])
def advanced_options():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))
    connection = get_db()
    db = Database(connection)
    fetcher = Fetch(connection)

    if request.method == "POST":
        if 'add_student' in request.form:
            rollno = request.form.get('rollno')
            name = request.form.get('name')
            email = request.form.get('email')
            db.rollinit(rollno, name, email)  # Call the method to add student
            return "Student added successfully!"

        elif 'reset_attendance' in request.form:
            rollno = request.form.get('reset_rollno')
            subject = request.form.get('reset_subject')
            db.reset_attendance(rollno, subject)  # Call the method to reset attendance
            return f"Attendance reset for rollno {rollno} for subject {subject}"


    return render_template("advanced_options.html")


@app.route("/api/add_student", methods=["POST"])
def api_add_student():
    data = request.get_json()
    rollno = data.get("rollno")
    name = data.get("name")
    email = data.get("email")
    connection = get_db()
    db = Database(connection)
    db.rollinit(rollno, name, email)
    return jsonify({"message": "Student added successfully!"}), 201

@app.route("/api/mark_attendance", methods=["POST"])
def api_mark_attendance():
    data = request.get_json()
    rollno = data.get("rollno")
    subject = data.get("subject")
    connection = get_db()
    db = Database(connection)
    db.attendance(rollno, subject)
    return jsonify({"message": f"Attendance marked for rollno {rollno} for subject {subject}"}), 200

@app.route("/api/fetch_attendance", methods=["GET"])
def api_fetch_attendance():
    connection = get_db()
    fetcher = Fetch(connection)
    all_rolls = fetcher.fetch_all_rolls()

    attendance_data = []
    for rollno in all_rolls:
        student_data = fetcher.fetch_all_attendance(rollno)
        attendance_data.append({
            "rollno": rollno,
            "name": student_data[1],
            "attendance": student_data[3:]
        })

    return jsonify(attendance_data)

@app.route("/api/reset_attendance", methods=["POST"])
def api_reset_attendance():
    data = request.get_json()
    rollno = data.get("rollno")
    subject = data.get("subject")
    connection = get_db()
    db = Database(connection)
    db.reset_attendance(rollno, subject)
    return jsonify({"message": f"Attendance reset for rollno {rollno} for subject {subject}"}), 200

@app.route("/api/mark_only_absent", methods=["POST"])
def api_mark_only_absent():
    data = request.get_json()
    roll = data.get("roll").split(',')  # List of roll numbers
    subject = data.get("subject")
    db = Database(get_db())
    db.mark_only_absent(roll, subject)
    return jsonify({"message": "Attendance marked as absent for selected roll numbers"}), 200

@app.route("/api/mark_only_present", methods=["POST"])
def api_mark_only_present():
    data = request.get_json()
    roll = data.get("roll").split(',')  # List of roll numbers
    subject = data.get("subject")
    db = Database(get_db())
    db.mark_only_present(roll, subject)
    return jsonify({"message": "Attendance marked as present for selected roll numbers"}), 200

@app.route("/api/rolls", methods=["GET"])
def api_fetch_rolls():
    connection = get_db()
    fetcher = Fetch(connection)
    all_rolls = fetcher.fetch_all_rolls()

    return jsonify(all_rolls)

if __name__ == "__main__":
    app.run(debug=True)

