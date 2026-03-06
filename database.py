from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement_portal.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
