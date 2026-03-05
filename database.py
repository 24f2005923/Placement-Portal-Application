import os

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def configure_db(app):
    db_path = os.path.join(os.path.dirname(__file__), "instance", "placement_portal.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
