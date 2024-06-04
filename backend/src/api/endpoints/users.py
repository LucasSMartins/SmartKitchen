from models.repository.collections import CollectionHandler
from models.connection_options.connections import DBConnectionHandler
from fastapi import APIRouter
from typing import Dict


router = APIRouter()


db_name = 'smartkitchien'
collection = 'users'

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(
    db_connection, collection)


@router.get("/")
async def read_users() -> list[Dict]:
    async_cursor = collection_repository.find_document({}, {"_id": 0})
    data_list = [doc async for doc in async_cursor]
    return data_list
