from typing import Dict

from pymongo.results import UpdateResult


class CollectionHandler:
    def __init__(self, db_connection, collection) -> None:
        self.__collection_name = collection
        self.__db_connection = db_connection

    async def find_document(
        self, filter_document: Dict = {}, request_attribute: Dict = {}
    ):
        collection = self.__db_connection.get_collection(self.__collection_name)
        async_cursor = collection.find(filter_document, request_attribute)
        data = await async_cursor.to_list(length=None)
        return data

    async def find_document_one(
        self, filter_document: Dict = {}, request_attribute: Dict = {}
    ):
        collection = self.__db_connection.get_collection(self.__collection_name)
        data = await collection.find_one(filter_document, request_attribute)
        if data:
            data = [data]
        return data

    async def insert_document(self, document: Dict):
        collection = self.__db_connection.get_collection(self.__collection_name)
        insert_result = await collection.insert_one(document)
        return insert_result

    # def insert_many_document(self, listDocument: List[Dict]) -> None:
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.insert_many(listDocument)

    async def update_document(self, filter_document: Dict, request_attribute: Dict) -> UpdateResult:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        update_result: UpdateResult = await collection.update_one(filter_document, {"$set": request_attribute})
        return update_result

    def delete_document(self, _id: Dict):
        collection = self.__db_connection.get_collection(self.__collection_name)
        delete_result = collection.delete_one(_id)
        return delete_result

    # def delete_many_document(self, userId: List) -> None:
    #     object_ids = [ObjectId(i) for i in userId]
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.delete_many({"_id": {"$in": object_ids}})


