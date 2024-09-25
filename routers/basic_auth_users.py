from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

#Authorization protocol 
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

class User(BaseModel):
    username: str
    full_name: str
    email: str
    disabled: bool

class UserDB(User):
    password: str

users_db = {
    "zarvi16g": {
        "username": "zarvi16g",
        "full_name": "Santiago Boada Rivas",
        "email": "zarvi16@google.com",
        "disabled": "False",
        "password": "123456"
    },
    "zarvi16g III": {
        "username": "zarvi16g III",
        "full_name": "Santiago Boada Rivas",
        "email": "zarvi16g@amazon.com",
        "disabled": "True",
        "password": "654321"
    }
}

#The ** in return is for show al the information.
def search_user_db(username: str):
    if username in users_db:
        return UserDB(**users_db[username])
    
def search_user(username: str):
    if username in users_db:
        return User(**users_db[username])
    
async def current_user(token: str = Depends(oauth2)):
    user = search_user(token)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid autentication credentials", headers={"www-authenticate": "Bearer"})
    
    if user.disabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="inactive user")
    
    return user



@router.post("/login_no_crypt")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    user_db = users_db.get(form.username)
    if not user_db:
        raise HTTPException(status_code=400, detail="User does not exist")
    
    user = search_user_db(form.username)
    if not form.password == user.password:
        raise HTTPException(status_code=400, detail="password incorrect")
        
    return {"acces_token": user.username,"token_type": "bearer"}


@router.get("/user/me_no_crypt")
async def me(user: User = Depends(current_user)):
    return user