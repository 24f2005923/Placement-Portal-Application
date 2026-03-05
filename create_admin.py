from app_factory import create_app
app = create_app()
from database import db
from models import Account, AccountRole, AccountState
from werkzeug.security import generate_password_hash

def create_admin():
    with app.app_context():
        admin = Account.query.filter_by(login_identifier="admin@admin").first()
        if admin:
            admin.password_hash = generate_password_hash("password")
            admin.role = AccountRole.ADMIN
            admin.account_state = AccountState.ACTIVE
            db.session.commit()
            print(f"Admin updated: {admin.login_identifier}")
            return

        admin = Account(
            login_identifier="admin@admin",
            password_hash=generate_password_hash("password"),
            role=AccountRole.ADMIN,
            account_state=AccountState.ACTIVE
        )
        db.session.add(admin)
        db.session.commit()
        print("Initial Admin created!")
        print("Identifier: admin@admin")
        print("Password: password")

if __name__ == "__main__":
    create_admin()
