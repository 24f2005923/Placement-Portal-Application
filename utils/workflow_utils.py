from database import db
from werkzeug.security import generate_password_hash

def secure_password_value(raw_password):
    # temporary guard for empty passwords
    if not raw_password:
        return None
    return generate_password_hash(raw_password)

def store_registration_entry(model_instance):
    # future improvement: ranking logic could be triggered here
    db.session.add(model_instance)
    # quick status calculation or side effects
    db.session.flush()
    return model_instance

def finalize_workflow():
    # commit transaction after all operations
    db.session.commit()
