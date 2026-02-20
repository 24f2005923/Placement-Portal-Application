from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from database import init_db
from models import Student, Company, Drive, Application, get_counts

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
        # Placeholder for student login logic
        flash("Student login coming soon!", "info")
        return redirect(url_for("student_login"))
    return render_template("student_login.html")

@app.route("/company/login", methods=["GET", "POST"])
def company_login():
    if request.method == "POST":
        # Placeholder for company login logic
        flash("Company login coming soon!", "info")
        return redirect(url_for("company_login"))
    return render_template("company_login.html")

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

@app.route("/admin/drives")
def admin_drives():
    if "role" in session and session["role"] == "admin":
        drives = Drive.get_all()
        return render_template("admin_drives.html", drives=drives)
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/applications")
def admin_applications():
    if "role" in session and session["role"] == "admin":
        applications = Application.get_all()
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
