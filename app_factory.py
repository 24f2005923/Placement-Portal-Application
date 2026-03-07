from flask import Flask
from database import configure_db, db
from routes import auth_bp, admin_bp, student_bp, company_bp, main_bp
from routes.application_api import application_api_bp
from utils.helpers import init_filters

def create_app():
    # central application initialization hub
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'placement_secret_key'

    configure_db(app)
    db.init_app(app)
    
    # registering specialized portal controllers
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(application_api_bp)

    # bootstrap custom rendering filters
    init_filters(app)

    with app.app_context():
        db.create_all()

    return app
