from fastapi import APIRouter

from src.api.endpoints.delete_all_db_DEV import router as delete_all_router
from src.api.endpoints.pantry import router as pantry_router
from src.api.endpoints.shopping_cart import router as shopping_cart_router

# from src.api.endpoints.recipes import router as recipes_router
from src.api.endpoints.users import router as users_router

api_router = APIRouter()

api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(pantry_router, prefix="/pantry", tags=["Pantry"])
api_router.include_router(
    shopping_cart_router, prefix="/shopping_cart", tags=["Shopping Cart"]
)
# api_router.include_router(recipes_router, prefix='/recipes', tags=['Recipes'])
api_router.include_router(delete_all_router, prefix="/delete_all")
