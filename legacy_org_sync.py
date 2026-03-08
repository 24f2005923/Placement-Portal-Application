from app_factory import create_app
from models import db, CompanyProfile

def sync_company_profile_schema():
    """
    Focused Schema Sync for CompanyProfile:
    Recreates the company_profiles table to match the model fields.
    """
    app = create_app()
    with app.app_context():
        print("Starting focused schema sync for 'company_profiles' table...")
        
        try:
            CompanyProfile.__table__.drop(db.engine, checkfirst=True)
            print("Dropped old 'company_profiles' table.")
            
            CompanyProfile.__table__.create(db.engine)
            print("Created new 'company_profiles' table with updated schema (including approval_status).")
            
            print("CompanyProfile table sync completed successfully!")
            
        except Exception as e:
            print(f"Error during schema sync: {e}")

if __name__ == "__main__":
    sync_company_profile_schema()
