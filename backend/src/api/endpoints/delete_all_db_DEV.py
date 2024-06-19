from fastapi import APIRouter

from src.api.endpoints.pantry import delete_db_pantry
from src.api.endpoints.shopping_cart import delete_db_shopping_cart
from src.api.endpoints.users import delete_all_users

router = APIRouter()


@router.delete("/")
async def delete_all_users_route():
    await delete_db_pantry()
    await delete_db_shopping_cart()
    await delete_all_users()
