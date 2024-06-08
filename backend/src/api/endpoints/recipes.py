from bson.objectid import ObjectId
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from models.connection_options.connections import DBConnectionHandler
from models.repository.collections import CollectionHandler

router = APIRouter()

db_name = "smartkitchien"
collection = "recipes"

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(db_connection, collection)


@router.get("/")
async def recipes(recipe_id: str) -> List[Dict]:
    data = (
        collection_repository.find_document({}, {"_id": 0})
        if not recipe_id
        else collection_repository.find_document({"_id": ObjectId(recipe_id)}, {"_id": 0})
    )
    return data


@router.post("/")
async def create_recipe(data: Dict) -> Dict:
    try:
        await collection_repository.insert_document(data)
        return {"result": "success"}

    except:
        raise HTTPException(status_code=400, detail="Erro nos tipo de dados")


@router.put("/{userId}")
def update_recipe(userid: str, data: Dict) -> str:
    try:
        collection_repository.update_document(userid, data)
        return "success"
    except:
        return "error"


@router.delete("/{userId}")
def delete_recipe(id: str) -> str:
    collection_repository.delete_document(id)
    return "success"
