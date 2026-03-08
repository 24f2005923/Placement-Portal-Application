from database import db
from werkzeug.security import generate_password_hash

def secure_password_value(raw_password):
    if not raw_password:
        return None
    return generate_password_hash(raw_password)

def store_registration_entry(model_instance):
    db.session.add(model_instance)
    db.session.flush()
    return model_instance

def finalize_workflow():
    db.session.commit()
