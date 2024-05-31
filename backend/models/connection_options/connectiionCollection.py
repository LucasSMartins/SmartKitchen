from models.connection_options.connections import DBConnectionHandler
from models.repository.collections import MinhaCollectuionRepository


db_name = 'smartkitchen'
collection = 'users'

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

minha_collection_repository = MinhaCollectuionRepository(
    db_connection, collection)
