from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from routers import products, basic_auth_users, jwt_auth_users, users_db
from fastapi.staticfiles import StaticFiles

#Start api with: uvicorn main:app --reload
app = FastAPI()

#Include connections with router and APIRouter with include_router and statics files with: mount.
app.include_router(products.router)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(basic_auth_users.router)
app.include_router(jwt_auth_users.router)
app.include_router(users_db.router)

class User(BaseModel):
    id: int
    name: str
    surname: str
    url: str
    age: int

users_list = [User(id=1, name="Santiago", surname="Boada", url="www.youtube.com", age="23"),
              User(id=2, name="Haidis", surname="Sinning", url="www.sinningtube.com", age="24"),
              User(id=3, name="Zarvi", surname="16G", url="www.zarvitube.com", age="25")]

#This is a endpoint with CRUD: GET
@app.get("/user/{id}")
async def user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return "Error: user not found"
 
@app.get("/users")
async def users():
    return users_list

@app.get("/user/{id}")
async def user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return "Error: user not found"

#Query
#Endpoint with get + data on query.
@app.get("/user/")
async def user(id: int, user: str):
    return search_user(id)

def search_user(id: int):
    users = filter(lambda user: user.id == id, users_list)
    try:
        return list(users)[0]
    except:
        return "Error: user not found"
    
# POST
@app.post("/user/", status_code=201)
async def create_user(user: User):
    if type(search_user(user.id)) == User:
        raise HTTPException(status_code=404, detail= "User exist already")
    else:
        users_list.append(user) 

# PUT 
@app.put("/user/")
async def update_user(user: User):

    found = False

    for index, saved_user in enumerate(users_list):
        if saved_user.id == user.id:
            users_list[index] = user
            found = True
    if not found:
        return {"error": "User does not exist."}
    
    return user

@app.delete("/user/{id}")
async def delete_user(id: int):
    for index, saved_user in enumerate(users_list):
        if saved_user.id == id:
            del users_list[index]

#Documentation with SWAGGER: /docs
#Documentation with Redocly: /redoc