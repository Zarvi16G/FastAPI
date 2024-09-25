from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from routers import products, basic_auth_users, jwt_auth_users
from fastapi.staticfiles import StaticFiles
from db.models.user import User
from db.client import db_client
from db.schemas.user import user_schema, users_schema
from bson import ObjectId

router = APIRouter(prefix="/userdb",
                   tags=["userdb"],
                   responses={status.HTTP_404_NOT_FOUND: {"message": "Not found"}})

@router.get("/", response_model=list[User])
async def users():
    return users_schema(db_client.users.find())

@router.get("/{id}")
async def user(id: str):
    return search_user("_id", ObjectId(id))
      


def search_user(field: str, key: str):
    try:
        user = db_client.users.find_one({field: key})
        print(user)
        return User(**user_schema(user))
    except:
        return "Error: user not found"
    


    
@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    if type(search_user("email", user.email)) == User:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= "User exist already")
    
    user_dict = dict(user)
    del user_dict["id"]  

    id = db_client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(db_client.users.find_one({"_id": id}))

    return User(**new_user)

@router.put("/", response_model=User)
async def update_user(user: User):

    if type(search_user("email", user.email)) == User:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail= "User exist already")

    user_dict = dict(user)
    del user_dict["id"]

    try:
        found = db_client.users.find_one_and_replace({"_id": ObjectId(user.id)}, user_dict)

    except:
        return {"error": "User does not exist."}
    
    return search_user("_id", ObjectId(user.id))

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: str):
    found = db_client.users.find_one_and_delete({"_id": ObjectId(id)}) 
    if not found:
        return {"error": "User doesn't deleted."}
