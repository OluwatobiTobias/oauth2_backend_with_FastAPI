from pydantic import BaseModel
from typing import Union

class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    diasbled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    acces_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None