from app import app
from database import db
from models import Account, AccountRole, AccountState
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        # Check if admin already exists
        admin = Account.query.filter_by(role=AccountRole.ADMIN).first()
        if admin:
            print(f"Admin already exists: {admin.login_identifier}")
            return

        admin = Account(
            login_identifier="admin@admin.com",
            password_hash=generate_password_hash("password123"),
            role=AccountRole.ADMIN,
            account_state=AccountState.ACTIVE
        )
        db.session.add(admin)
        db.session.commit()
        print("Initial Admin created!")
        print("Identifier: admin@admin.com")
        print("Password: password123")

if __name__ == "__main__":
    create_admin()
