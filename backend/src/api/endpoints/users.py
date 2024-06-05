from models.repository.collections import CollectionHandler
from models.connection_options.connections import DBConnectionHandler
from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import Annotated, Dict, Optional
from src.api.schema.default_answer import Default_Answer
from src.api.schema.users import UserOut, UserIn
from bson.objectid import ObjectId


router = APIRouter()


db_name = 'smartkitchien'
collection = 'users'

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(
    db_connection, collection)


@router.get('/', response_model=Default_Answer)
async def read_users():

    request_attribute = {'_id': 0, 'password': 0}

    data = await collection_repository.find_document(request_attribute=request_attribute)

    if not data:
        raise HTTPException(status_code=404, detail='Users not found')

    response = {
        "status": "success",
        "message": "Users found",
        "data": data
    }

    return response


@router.get('/{user_id}', response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def read_user(user_id: Annotated[str, Path(
        title='The ID of the item to get',
        description='The unique identifier for the item, represented as a MongoDB ObjectId',
        regex=r"^[a-fA-F0-9]{24}$"
)]):

    filter_document = {'_id': ObjectId(user_id)}
    request_attribute = {'_id': 0, 'password': 0}

    data = await collection_repository.find_document_one(
        filter_document, request_attribute)

    if not data:
        raise HTTPException(status_code=404, detail='User not found')

    response = {
        "status": "success",
        "message": "User found",
        "data": data
    }

    return response


@router.post('/', response_model=Default_Answer, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserIn):
    data_user = new_user.model_dump()
    await collection_repository.insert_document(data_user)
    new_dict = [
        {key: value for key, value in data_user.items()if key != 'password'}
    ]
    response = {
        "status": "success",
        "message": "User created",
        "data": new_dict
    }
    return response


@router.delete('/{id}',
               response_model=Default_Answer,
               status_code=status.HTTP_200_OK
               )
async def del_user(id: str):

    collection_repository.delete_document({'_id': ObjectId(id)})

    response = {
        "status": "success",
        "message": "User deleted",
        "data": None
    }

    return response
