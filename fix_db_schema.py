import os
from app_factory import create_app
from models import db, PlacementDrive

def sync_schema():
    """
    Focused Schema Sync: 
    This script recreates the placement_drives table to match the new model fields.
    Using this focused approach is safer than dropping the entire database.
    """
    app = create_app()
    with app.app_context():
        print("Starting focused schema sync...")
        
        try:
            PlacementDrive.__table__.drop(db.engine, checkfirst=True)
            print("Dropped old 'placement_drives' table.")
            
            PlacementDrive.__table__.create(db.engine)
            print("Created new 'placement_drives' table with updated schema.")
            
            print("Database schema sync completed successfully!")
            
        except Exception as e:
            print(f"Error during schema sync: {e}")

if __name__ == "__main__":
    sync_schema()
