from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from database import db, get_db_connection
from models import StudentProfile, CompanyProfile, PlacementDrive, StudentApplication
from datetime import datetime

app = Flask(__name__)
app.secret_key = "placement_secret_key"

# Initialize Database
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        if username == "admin@admin" and password == "password":
            session["role"] = "admin"
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid Credentials", "danger")
            return redirect(url_for("admin_login"))
            
    return render_template("admin_login.html")

@app.route("/student/login", methods=["GET", "POST"])
def student_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = get_db_connection()
        student = conn.execute("SELECT * FROM students WHERE college_email = ? AND password = ?", (email, password)).fetchone()
        conn.close()
        
        if student:
            session["role"] = "student"
            session["student_id"] = student["id"]
            session["student_name"] = student["name"]
            session["student_email"] = student["college_email"]
            flash(f"Welcome back, {student['name']}!", "success")
            return redirect(url_for("student_dashboard"))
        else:
            flash("Invalid Email or Password", "danger")
            return redirect(url_for("student_login"))
    return render_template("student_login.html")

@app.route("/student/register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        # Placeholder for student registration logic
        flash("Student registration successful!", "success")
        return redirect(url_for("student_login"))
    return render_template("student_register.html")

# Student Panel Routes
@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") == "student":
        student_id = session.get("student_id")
        conn = get_db_connection()
        
        # Get counts for student
        app_count = conn.execute("SELECT COUNT(*) FROM applications WHERE student_id = ?", (student_id,)).fetchone()[0]
        
        # Get latest drives
        latest_drives = conn.execute("""
            SELECT drives.*, companies.name as company_name 
            FROM drives 
            JOIN companies ON drives.company_id = companies.id 
            ORDER BY drives.id DESC LIMIT 5
        """).fetchall()
        
        # Get recent applications
        recent_apps = conn.execute("""
            SELECT applications.*, drives.title as drive_title, companies.name as company_name 
            FROM applications 
            JOIN drives ON applications.drive_id = drives.id 
            JOIN companies ON drives.company_id = companies.id 
            WHERE applications.student_id = ? 
            ORDER BY applications.id DESC LIMIT 3
        """, (student_id,)).fetchall()
        
        conn.close()
        
        return render_template("student_dashboard.html", 
                               app_count=app_count, 
                               latest_drives=latest_drives, 
                               recent_apps=recent_apps)
    return redirect(url_for("student_login"))

@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if session.get("role") == "student":
        student_id = session.get("student_id")
        conn = get_db_connection()
        
        if request.method == "POST":
            name = request.form.get("name")
            personal_email = request.form.get("personal_email")
            mobile = request.form.get("mobile")
            dob = request.form.get("dob")
            
            conn.execute("""
                UPDATE students 
                SET name = ?, personal_email = ?, mobile = ?, dob = ? 
                WHERE id = ?
            """, (name, personal_email, mobile, dob, student_id))
            conn.commit()
            session["student_name"] = name
            flash("Profile updated successfully!", "success")
            return redirect(url_for("student_profile"))
            
        student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        conn.close()
        return render_template("student_profile.html", student=student)
    return redirect(url_for("student_login"))

# Note: Student placement view is handled in routes/student.py
@app.route("/student/search")
def student_search_jobs():
    if session.get("role") == "student":
        return render_template("student_view_drives.html") # Reuse drive view for simplicity
    return redirect(url_for("student_login"))

@app.route("/student/applications")
def student_applications():
    if session.get("role") == "student":
        student_id = session.get("student_id")
        conn = get_db_connection()
        applications = conn.execute("""
            SELECT applications.*, drives.title as drive_title, companies.name as company_name 
            FROM applications 
            JOIN drives ON applications.drive_id = drives.id 
            JOIN companies ON drives.company_id = companies.id 
            WHERE applications.student_id = ?
        """, (student_id,)).fetchall()
        conn.close()
        return render_template("student_applications.html", applications=applications)
    return redirect(url_for("student_login"))

@app.route("/student/history")
def student_history():
    if session.get("role") == "student":
        return render_template("student_history.html")
    return redirect(url_for("student_login"))

@app.route("/student/notifications")
def student_notifications():
    if session.get("role") == "student":
        return render_template("student_notifications.html")
    return redirect(url_for("student_login"))


@app.route("/student/logout")
def student_logout():
    session.clear()
    flash("Successfully logged out from student portal", "success")
    return redirect(url_for("student_login"))

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        conn = get_db_connection()
        company = conn.execute("SELECT * FROM companies WHERE work_email = ? AND password = ?", (email, password)).fetchone()
        conn.close()
        
        if company:
            session["role"] = "company"
            session["company_id"] = company["id"]
            session["company_name"] = company["name"]
            flash(f"Logged in successfully as {company['name']}", "success")
            return redirect(url_for("company_dashboard"))
        else:
            flash("Invalid Email or Password", "danger")
            return redirect(url_for("company_login"))
            
    return render_template("company_login.html")

@app.route("/company/register", methods=["GET", "POST"])
def company_register():
    if request.method == "POST":
        # Placeholder for company registration logic
        flash("Company registration submitted for approval!", "success")
        return redirect(url_for("company_login"))
    return render_template("company_register.html")

# Company Panel Routes
@app.route("/company/dashboard")
def company_dashboard():
    if session.get("role") == "company":
        company_id = session.get("company_id")
        conn = get_db_connection()
        
        # Get stats
        active_drives = conn.execute("SELECT COUNT(*) FROM drives WHERE company_id = ? AND status = 'Open'", (company_id,)).fetchone()[0]
        total_apps = conn.execute("""
            SELECT COUNT(*) FROM applications 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ?
        """, (company_id,)).fetchone()[0]
        
        pending_review = conn.execute("""
            SELECT COUNT(*) FROM applications 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ? AND applications.status = 'Pending'
        """, (company_id,)).fetchone()[0]
        
        hired = conn.execute("""
            SELECT COUNT(*) FROM applications 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ? AND applications.status = 'Selected'
        """, (company_id,)).fetchone()[0]
        
        # Recent drives
        recent_drives = conn.execute("SELECT * FROM drives WHERE company_id = ? ORDER BY id DESC LIMIT 5", (company_id,)).fetchall()
        
        conn.close()
        return render_template("company_dashboard.html", 
                               active_drives=active_drives, 
                               total_apps=total_apps, 
                               pending_review=pending_review, 
                               hired=hired,
                               recent_drives=recent_drives)
    return redirect(url_for("company_login"))

@app.route("/company/profile")
def company_profile():
    return render_template("company_profile.html")

# Note: Company drive creation is handled in routes/company.py
@app.route("/company/applications")
def company_applications():
    if session.get("role") == "company":
        company_id = session.get("company_id")
        conn = get_db_connection()
        applications = conn.execute("""
            SELECT applications.*, students.name as student_name, students.roll_number, drives.title as drive_title 
            FROM applications 
            JOIN students ON applications.student_id = students.id 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ?
        """, (company_id,)).fetchall()
        conn.close()
        return render_template("company_applications.html", applications=applications)
    return redirect(url_for("company_login"))

@app.route("/company/shortlisted")
def company_shortlisted():
    if session.get("role") == "company":
        company_id = session.get("company_id")
        conn = get_db_connection()
        students = conn.execute("""
            SELECT applications.*, students.name as student_name, students.roll_number, drives.title as drive_title 
            FROM applications 
            JOIN students ON applications.student_id = students.id 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ? AND applications.status = 'Shortlisted'
        """, (company_id,)).fetchall()
        conn.close()
        return render_template("company_shortlisted.html", students=students)
    return redirect(url_for("company_login"))

@app.route("/company/selected")
def company_selected():
    if session.get("role") == "company":
        company_id = session.get("company_id")
        conn = get_db_connection()
        students = conn.execute("""
            SELECT applications.*, students.name as student_name, students.roll_number, drives.title as drive_title 
            FROM applications 
            JOIN students ON applications.student_id = students.id 
            JOIN drives ON applications.drive_id = drives.id 
            WHERE drives.company_id = ? AND applications.status = 'Selected'
        """, (company_id,)).fetchall()
        conn.close()
        return render_template("company_selected.html", students=students)
    return redirect(url_for("company_login"))

@app.route("/company/logout")
def company_logout():
    session.pop("role", None)
    flash("Successfully logged out from company portal", "success")
    return redirect(url_for("company_login"))

@app.route("/admin/dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        counts = get_counts()
        return render_template("admin_dashboard.html", counts=counts)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/students")
def admin_students():
    if "role" in session and session["role"] == "admin":
        students = Student.get_all()
        return render_template("admin_students.html", students=students)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/companies")
def admin_companies():
    if "role" in session and session["role"] == "admin":
        companies = Company.get_all()
        return render_template("admin_companies.html", companies=companies)
    else:
        return redirect(url_for("admin_login"))

# Note: Admin drive management is handled in routes/admin.py

@app.route("/admin/applications")
def admin_applications():
    if "role" in session and session["role"] == "admin":
        applications = StudentApplication.query.all()
        return render_template("admin_applications.html", applications=applications)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/blacklisted")
def admin_blacklisted():
    if "role" in session and session["role"] == "admin":
        students = Student.get_blacklisted()
        return render_template("admin_blacklisted.html", students=students)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("role", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
