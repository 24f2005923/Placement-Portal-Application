from app_factory import create_app
from database import db
from models import Account, CompanyProfile, AccountRole
import json

app = create_app()

def check():
    with app.app_context():
        data = {"accounts": [], "profiles": []}
        accounts = Account.query.all()
        for acc in accounts:
            data["accounts"].append({
                "id": acc.id,
                "identifier": acc.login_identifier,
                "role": acc.role.value,
                "state": acc.account_state.value
            })
        
        profiles = CompanyProfile.query.all()
        for p in profiles:
            p_dict = {c.name: str(getattr(p, c.name)) for c in p.__table__.columns}
            data["profiles"].append(p_dict)
            
        with open("db_data.json", "w") as f:
            json.dump(data, f, indent=4)

if __name__ == "__main__":
    check()
