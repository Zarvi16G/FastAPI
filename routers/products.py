from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"], responses={404: {"message": "Not found"}})

@router.get("/")
async def products():
    return ["prodc 1", "prodc 2", "prodc 3"]