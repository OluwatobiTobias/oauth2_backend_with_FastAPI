from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .db import db_users, get_user
from .models import UserInDB, User, Token, TokenData
from typing import Dict, Union
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# def get_password_hash(password):
#     return pwd_context.hash(password)

def authenticate_user(db, username: str, password: str) -> UserInDB:
    user =  get_user(db, username)
    if not user:
        return False
    print(user.hashed_password, '----------------', password)
    if not verify_password(password, user.hashed_password):
        return False

    return user


def create_access_token(data: Dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    print(f'to_encode before-----{to_encode}')
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)

    to_encode.update({"exp": expire})
    print(f'to_encode after-----{to_encode}')

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    print(f'\n------encoded_jwt----{encoded_jwt}-----\n')

    return encoded_jwt


@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Dict[str, str]:

    user = authenticate_user(db_users, form_data.username, form_data.password)

    if not user:
        raise  HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}


async def get_currect_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})

    print(f'\n------token----{token}-----\n')

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f'----payload----{payload}')

        username: str = payload.get("sub")
        if username is None:
            raise credential_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credential_exception
    
    user = get_user(db_users, username=token_data.username)
    if user is None:
        raise credential_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_currect_user)) -> User:
    print(f'-----current_user-> {current_user}--------current_user.disabled-> {current_user.diasbled}')
    if current_user.diasbled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

@app.get('/users/me', response_model=User)
async def secured_api(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]