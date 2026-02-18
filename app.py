from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "placement_secret_key"

@app.route("/")
def home():
    return "Placement Portal Running Successfully!"

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

@app.route("/admin/dashboard")
def admin_dashboard():
    if "role" in session and session["role"] == "admin":
        return render_template("admin_dashboard.html")
    else:
        return redirect(url_for("admin_login"))

@app.route("/admin/logout")
def admin_logout():
    session.pop("role", None)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(debug=True)
