from app_factory import create_app
from models import db, Account, CompanyProfile, AccountRole

app = create_app()
with app.app_context():
    print("--- Database Diagnostic ---")
    company_accounts = Account.query.filter_by(role=AccountRole.COMPANY.value).all()
    print(f"Found {len(company_accounts)} company accounts.")
    
    orphans = []
    for acc in company_accounts:
        profile = CompanyProfile.query.filter_by(account_id=acc.id).first()
        status = "OK" if profile else "MISSING PROFILE"
        if not profile:
            orphans.append(acc)
        print(f"Account: {acc.login_identifier} (ID: {acc.id}) -> {status}")
    
    print("\n--- Repairing orphans ---")
    for acc in orphans:
        # Create a basic profile so dashboard doesn't loop
        new_profile = CompanyProfile(
            account_id=acc.id,
            name=f"Company {acc.id}",
            company_id_field=f"COMP-{acc.id}",
            hr_contact="Admin",
            work_email=acc.login_identifier
        )
        db.session.add(new_profile)
        print(f"Created placeholder profile for {acc.login_identifier}")
    
    db.session.commit()
    print("\nDiagnostic and repair completed.")
