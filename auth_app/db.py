from typing import Dict
from .models import User, UserInDB

db_users: Dict[str, Dict[str, str]] = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "hashedsecret2",
        "disabled": True,
    },
}

def get_user(db, username: str) -> UserInDB: #database
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

