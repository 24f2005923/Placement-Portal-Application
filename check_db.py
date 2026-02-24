from app_factory import create_app
from database import db
from models import Account, AccountRole

app = create_app()

def check_accounts():
    with app.app_context():
        accounts = Account.query.all()
        print(f"Total accounts: {len(accounts)}")
        for acc in accounts:
            print(f"ID: {acc.id}, Identifier: '{acc.login_identifier}', Role: {acc.role}, State: {acc.account_state}")
            
        admin = Account.query.filter_by(login_identifier="admin@admin").first()
        if admin:
            print(f"Found admin@admin: {admin}")
            print(f"Role matches ADMIN: {admin.role == AccountRole.ADMIN}")
        else:
            print("admin@admin NOT FOUND in database")

if __name__ == "__main__":
    check_accounts()
