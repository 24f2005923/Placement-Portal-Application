from routes.auth import auth_bp
from routes.moderation_routes import admin_bp
from routes.engagement_routes import student_bp
from routes.organization_routes import company_bp
from routes.main import main_bp

__all__ = ["auth_bp", "admin_bp", "student_bp", "company_bp", "main_bp"]
