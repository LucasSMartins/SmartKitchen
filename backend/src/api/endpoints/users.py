from typing import Annotated

from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, Path, status

from models.connection_options.connections import DBConnectionHandler
from models.repository.collections import CollectionHandler
from src.api.schema.default_answer import Attr_Default_Answer, Default_Answer
from src.api.schema.users import UserOut, UserIn

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

    if not data or not data[0]:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="Users not found")).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(detail=Attr_Default_Answer(
        status="success", msg="Users found", data=data))


@router.get('/{user_id}', response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def read_user(user_id: Annotated[str, Path(
        title='The ID of the item to get',
        description='The unique identifier for the item, represented as a MongoDB ObjectId',
        regex=r"^[a-fA-F0-9]{24}$")]):

    filter_document = {'_id': ObjectId(user_id)}
    request_attribute = {'_id': 0, 'password': 0}

    data = await collection_repository.find_document_one(
        filter_document, request_attribute)

    if not data or not data[0]:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="User not found")).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(detail=Attr_Default_Answer(status="success", msg="User found", data=data))


@router.post('/', response_model=Default_Answer, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserIn):

    data_user = new_user.model_dump()

    # filter_document = {
    #     '$or': [{'username': data_user['username']}, {'email': data_user['email']}]}

    filter_document_username = {'username': data_user['username']}
    filter_document_email = {'email': data_user['email']}

    request_attribute = {'_id': 0, 'password': 0}

    does_the_username_exist = await collection_repository.find_document(filter_document_username, request_attribute)

    does_the_email_exist = await collection_repository.find_document(filter_document_email, request_attribute)

    if does_the_email_exist and does_the_username_exist:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="username and email already exists")).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=response)

    if does_the_username_exist:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="username already exists")).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=response)

    if does_the_email_exist:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="This email already exists")).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=response)

    await collection_repository.insert_document(data_user)

    data = list(UserOut(username=data_user["username"],
                        email=data_user["email"]))

    return Default_Answer(detail=Attr_Default_Answer(status="success", msg="User created", data=data))


@router.delete('/{id}', response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def del_user(user_id: str):

    filter_document = {'_id': ObjectId(user_id)}
    request_attribute = {'_id': 0, 'password': 0}

    does_the_user_exist = await collection_repository.find_document(filter_document, request_attribute)

    if not does_the_user_exist:
        response = Default_Answer(detail=Attr_Default_Answer(
            status="fail", msg="User not found")).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=response)

    collection_repository.delete_document({'_id': ObjectId(user_id)})

    return Default_Answer(detail=Attr_Default_Answer(status='success', msg='User deleted'))
