from fastapi import APIRouter

from src.api.endpoints.pantry import router as pantry_router

# from src.api.endpoints.recipes import router as recipes_router
from src.api.endpoints.users import router as users_router

api_router = APIRouter()
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(pantry_router, prefix="/pantry", tags=["Pantry"])
# api_router.include_router(recipes_router, prefix='/recipes', tags=['Recipes'])
