from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

from models.connection_options.mongo_db_config import mongo_db_infos


class DBConnectionHandler:
    def __init__(self) -> None:
        self.__connection_string = f"mongodb+srv://{mongo_db_infos['USERNAME']}:{mongo_db_infos['PASSWORD']}@smartkitchencluster0.escnq8a.mongodb.net/{mongo_db_infos['DB_NAME']}?retryWrites=true&w=majority&appName={mongo_db_infos['CLUSTER']}"
        self.__client = None
        self.__db_connection = None

    def connect_to_db(self, db_name):
        self.__client = AsyncIOMotorClient(
            self.__connection_string, server_api=ServerApi("1")
        )
        self.__db_connection = self.__client[db_name]

    def get_db_connection(self):
        return self.__db_connection

    def get_db_client(self):
        return self.__client

    # TODO Criar um método de teste de conexão e implementar nas rotas.
    # async def ping_db(self):
    #     try:
    #         # Testar a conexão com o banco de dados
    #         await self.__client.admin.command("ping")
    #         print("Conexão com o banco de dados estabelecida com sucesso.")
    #     except ServerSelectionTimeoutError:
    #         print("Falha ao conectar ao banco de dados.")
