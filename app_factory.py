from flask import Flask
from database import configure_db, db
from routes import auth_bp, admin_bp, student_bp, company_bp, main_bp
from routes.application_api import application_api_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "placement_secret_key"

    # Configure Database
    configure_db(app)

    # Register Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(application_api_bp)

    with app.app_context():
        # Ensure tables are created
        db.create_all()

    return app
