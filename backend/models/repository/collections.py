from typing import Dict, List
from bson.objectid import ObjectId
from models.connection_options.mongo_db_config import mongo_db_infos


class MinhaCollectuionRepository:
    def __init__(self, db_connection, collection) -> None:
        self.__collection_name = collection
        self.__db_connection = db_connection

    def find_document(self, filter_document: Dict, request_attribute: Dict) -> List:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        cursor = collection.find(filter_document, request_attribute)
        # data = [ i for i in cursor]
        # return data
        return cursor

    def insert_document(self, document: Dict) -> None:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.insert_one(document)

    def insert_many_document(self, listDocument: List[Dict]) -> None:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.insert_many(listDocument)

    def update_document(self, id: str, attr: Dict) -> None:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.update_one({"_id": ObjectId(id)}, {"$set": attr})

    def delete_document(self, id: str) -> None:
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.delete_one({"_id": ObjectId(id)})

    def delete_many_document(self, id: List) -> None:
        object_ids = [ObjectId(i) for i in id]
        collection = self.__db_connection.get_collection(
            self.__collection_name)
        collection.delete_many({"_id": {"$in": object_ids}})
