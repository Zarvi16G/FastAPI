from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

#Type of algorithm
ALGORITHM = "HS256"

#Duration token with variable.
ACCESS_TOKEN_DURATION = 1

#Safe backend with a seed.
SECRET = "086795c908d23093ad71f9529a6205076b9daa63c23bbcaec2a46184bd4babeb"

router = APIRouter()

#When the url is login the oauth2 will be working.
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

#The password has a bcrypt.
users_db = {
    "zarvi16g": {
        "username": "zarvi16g",
        "full_name": "Santiago Boada Rivas",
        "email": "zarvi16@google.com",
        "disabled": "False",
        "password": "$2a$12$sH.AgJzxSl7ZTexxyXvHsuoO53iq1TUb/otzX2WOXe3lmv2V6i7za"
    },
    "zarvi16g III": {
        "username": "zarvi16g III",
        "full_name": "Santiago Boada Rivas",
        "email": "zarvi16g@amazon.com",
        "disabled": "True",
        "password": "$2a$12$OQxP1/SfBquFTzYDPS1zzu7m93oaoPx5SJnTdZsUdDBiObrCh5PJS"
    }
}


def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])

async def auth_user(token: str = Depends(oauth2)):

    exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid autentication credentials", headers={"www-authenticate": "Bearer"})

    try:
        username = jwt.decode(token, SECRET, algorithms=[ALGORITHM]).get("sub")
        if username is None:
            raise exception
    
    except JWTError:
        raise exception

    return search_user(username)

async def current_user(user: User = Depends(auth_user)):
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inactive user")
    
    return user

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    user = search_user_db(form.username)
    
    if not crypt.verify(form.password, user.password):
        raise HTTPException(status_code=400, detail="password incorrect")
    
    access_token = {"sub": user.username, "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)}

#SECRET has a seed for manipulate the encode = more security.
    return {"acces_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM), "token_type": "bearer"}

@router.get("/user/me")
async def me(user: User = Depends(current_user)):
    return user