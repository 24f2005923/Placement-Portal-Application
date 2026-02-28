from app_factory import create_app
from models import db, StudentApplication

def sync_applications_schema():
    """
    Focused Schema Sync for Applications:
    Recreates the applications table to match the new model fields.
    """
    app = create_app()
    with app.app_context():
        print("Starting focused schema sync for 'student_applications' table...")
        
        try:
            # Drop only the applications table if it exists
            StudentApplication.__table__.drop(db.engine, checkfirst=True)
            print("Dropped old 'student_applications' table.")
            
            # Recreate only the applications table with new schema
            StudentApplication.__table__.create(db.engine)
            print("Created new 'student_applications' table with updated schema (including applied_at).")
            
            print("StudentApplications table sync completed successfully!")
            
        except Exception as e:
            print(f"Error during schema sync: {e}")

if __name__ == "__main__":
    sync_applications_schema()
