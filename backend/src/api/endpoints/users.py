from fastapi import APIRouter
from models.connection_options.connectiionCollection import minha_collection_repository


router = APIRouter()


@router.get("/")
async def read_users():
    return {"message": "Users"}
