from typing import Optional
from pydantic import BaseModel
import os
from passlib.context import CryptContext

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    hashed_password: str

class UserInDB(User):
    pass

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

demo_password = os.getenv("DEMO_USER_PASSWORD", "dev-password-change-in-production")
users_db = {
    "user_1": {
        "id": "user_1",
        "username": "manager",
        "email": "manager@arcticeicesolutions.com",
        "full_name": "John Manager",
        "role": "manager",
        "location_id": "loc_1",
        "hashed_password": get_password_hash(demo_password)
    },
    "user_2": {
        "id": "user_2", 
        "username": "dispatcher",
        "email": "dispatcher@arcticeicesolutions.com",
        "full_name": "Sarah Dispatcher",
        "role": "dispatcher",
        "location_id": "loc_2",
        "hashed_password": get_password_hash(demo_password)
    },
    "user_3": {
        "id": "user_3",
        "username": "accountant", 
        "email": "accountant@arcticeicesolutions.com",
        "full_name": "Mike Accountant",
        "role": "accountant",
        "location_id": "loc_1",
        "hashed_password": get_password_hash(demo_password)
    },
    "user_4": {
        "id": "user_4",
        "username": "driver",
        "email": "driver@arcticeicesolutions.com", 
        "full_name": "Tom Driver",
        "role": "driver",
        "location_id": "loc_2",
        "hashed_password": get_password_hash(demo_password)
    }
}

def get_user(username: str):
    for user_data in users_db.values():
        if user_data["username"] == username:
            return UserInDB(**user_data)
    return None
