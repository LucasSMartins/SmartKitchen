from typing import Annotated

from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, Path, status

from models.connection_options.connections import DBConnectionHandler
from models.repository.collections import CollectionHandler
from src.api.endpoints.pantry import create_categories
from src.api.schema.default_answer import Attr_Default_Answer, Default_Answer
from src.api.schema.users import UserIn, UserInUpdate, UserOut

router = APIRouter()

db_name = "smartkitchien"
collection = "users"

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(db_connection, collection)


@router.get("/", response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def read_users():
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document(
        request_attribute=request_attribute
    )

    if not data or not data[0]:
        response = Default_Answer(
            detail=Attr_Default_Answer(status="fail", msg="Users not found")
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="Users found", data=data)
    )


@router.get("/{_id}", response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def read_user(
    _id: Annotated[
        str,
        Path(
            title="The ID of the item to get",
            description="The unique identifier for the item, represented as a MongoDB"
            "ObjectId",
            regex=r"^[a-fA-F0-9]{24}$",
        ),
    ]
):
    filter_document = {"_id": ObjectId(_id)}
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document_one(
        filter_document, request_attribute
    )

    if not data:
        response = Default_Answer(
            detail=Attr_Default_Answer(status="fail", msg="User not found")
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="User found", data=data)
    )


@router.post("/", response_model=Default_Answer, status_code=status.HTTP_201_CREATED)
async def create_user(new_user: UserIn):
    data_user = new_user.model_dump()

    filter_document_username = {"username": data_user["username"]}
    filter_document_email = {"email": data_user["email"]}

    request_attribute = {"_id": 0, "password": 0}

    does_the_username_exist = await collection_repository.find_document(
        filter_document_username, request_attribute
    )

    does_the_email_exist = await collection_repository.find_document(
        filter_document_email, request_attribute
    )

    if does_the_email_exist and does_the_username_exist:
        response = Default_Answer(
            detail=Attr_Default_Answer(
                status="fail", msg="username and email already exists"
            )
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    if does_the_username_exist:
        response = Default_Answer(
            detail=Attr_Default_Answer(status="fail", msg="username already exists")
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    if does_the_email_exist:
        response = Default_Answer(
            detail=Attr_Default_Answer(status="fail", msg="This email already exists")
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    insert_one_result = await collection_repository.insert_document(data_user)

    data = [UserOut(username=data_user["username"], email=data_user["email"])]

    await create_categories(
        user_id=insert_one_result.inserted_id, username=data_user["username"]
    )

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="User created", data=data)
    )


@router.delete("/{_id}", response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def del_document(_id: str):
    filter_document = {"_id": ObjectId(_id)}

    delete_result = await collection_repository.delete_document(filter_document)

    if not delete_result.deleted_count:
        response = Default_Answer(
            detail=Attr_Default_Answer(
                status="fail", msg="user not found or does not exist"
            )
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="User deleted")
    )


@router.put("/{user_id}", response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def update_document(user_id: str, data_user_update: UserInUpdate):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=Default_Answer(
                detail=Attr_Default_Answer(status="Fail", msg="Invalid user ID")
            ).model_dump(),
        )

    filter_document = {"_id": ObjectId(user_id)}

    # Verifica se o usuário existe
    existing_user = await collection_repository.find_document_one(filter_document)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Default_Answer(
                detail=Attr_Default_Answer(status="Fail", msg="User not found")
            ).model_dump(),
        )

    # Verifica se o username já está em uso
    if data_user_update.username:
        if await collection_repository.find_document_one(
            {"username": data_user_update.username}
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Default_Answer(
                    detail=Attr_Default_Answer(
                        status="Fail", msg="Username already in use"
                    )
                ).model_dump(),
            )

    # Verifica se o email já está em uso
    if data_user_update.email:
        if await collection_repository.find_document_one(
            {"email": data_user_update.email}
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=Default_Answer(
                    detail=Attr_Default_Answer(
                        status="success", msg="Email already in use"
                    )
                ).model_dump(),
            )

    # Removendo os attr com valores None
    request_attribute = data_user_update.dict(exclude_unset=True)

    # Atualiza o documento no MongoDB
    update_result = await collection_repository.update_document(
        filter_document=filter_document, request_attribute=request_attribute
    )

    if update_result.modified_count == 1:
        return Default_Answer(
            detail=Attr_Default_Answer(
                status="success", msg="User updated successfully"
            )
        ).model_dump()
    else:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=Default_Answer(
                detail=Attr_Default_Answer(status="success", msg="User not modified")
            ).model_dump(),
        )
