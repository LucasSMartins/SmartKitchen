from typing import Dict


class CollectionHandler:
    def __init__(self, db_connection, collection) -> None:
        self.__collection_name = collection
        self.__db_connection = db_connection

    async def find_document(self, filter_document: Dict = {}, request_attribute: Dict = {}):
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        async_cursor = collection.find(filter_document, request_attribute)
        data = await async_cursor.to_list(length=None)
        return data

    async def find_document_one(self, filter_document: Dict = {}, request_attribute: Dict = {}):
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        data = [await collection.find_one(filter_document, request_attribute)]
        return data

    async def insert_document(self, document: Dict) -> None:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.insert_one(document)

    # def insert_many_document(self, listDocument: List[Dict]) -> None:
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.insert_many(listDocument)

    # def update_document(self, id: str, attr: Dict) -> None:
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.update_one({"_id": ObjectId(id)}, {"$set": attr})

    # def delete_document(self, id: str) -> None:
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.delete_one({"_id": ObjectId(id)})

    # def delete_many_document(self, id: List) -> None:
    #     object_ids = [ObjectId(i) for i in id]
    #     collection = self.__db_connection.get_collection(
    #         self.__collection_name)
    #     collection.delete_many({"_id": {"$in": object_ids}})
