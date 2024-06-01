from models.repository.collections import MinhaCollectuionRepository
from models.connection_options.connections import DBConnectionHandler
from fastapi import APIRouter
from models.connection_options.connectiionCollection import minha_collection_repository


router = APIRouter()


db_name = 'smartkitchen'
collection = 'users'

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

minha_collection_repository = MinhaCollectuionRepository(
    db_connection, collection)


@router.get("/")
async def read_users():
    async_cursor = minha_collection_repository.find_document({}, {"_id": 0})

    # Iterar sobre o cursor para obter os documentos
    async for document in async_cursor:
        print(document)

    # Fechar a conexão
    await db_connection.close()
    return {"msg": 'ok'}
