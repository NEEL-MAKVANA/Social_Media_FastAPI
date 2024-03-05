from src.models.user import User
from database.db_config import SessionLocal

db = SessionLocal()



def verify_user(user_id):
    find_user_with_is_verified_true = db.query(User).filter(User.id == user_id , User.is_verified==True).first()
    if not find_user_with_is_verified_true:
        return False
    else:
        return True
