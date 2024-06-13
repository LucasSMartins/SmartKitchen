from typing import Annotated

from bson.objectid import ObjectId
from fastapi import APIRouter, HTTPException, Path, status

from models.connection_options.connections import DBConnectionHandler
from models.connection_options.mongo_db_config import mongo_db_infos
from models.repository.collections import CollectionHandler
from src.api.endpoints.pantry import create_categories, update_username_pantry
from src.api.schema.default_answer import DefaultAnswer, StatusMsg
from src.api.schema.users import UserIn, UserInUpdate, UserOut

router = APIRouter()

collection = "users"

db_handler = DBConnectionHandler()
db_handler.connect_to_db(mongo_db_infos["DB_NAME"])
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(
    db_connection, mongo_db_infos["COLLECTIONS"]["collection_users"]  # type: ignore
)


@router.get("/", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def read_users():
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document(
        request_attribute=request_attribute
    )

    if not data:
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="Users not found"
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="Users found", data=data)


@router.get("/{_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
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
    if not ObjectId.is_valid(_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {"_id": ObjectId(_id)}
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document_one(
        filter_document, request_attribute
    )

    if not data:
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="User not found"
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="User found", data=data)


@router.post("/", response_model=DefaultAnswer, status_code=status.HTTP_201_CREATED)
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
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="username and email already exists"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    if does_the_username_exist:
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="username already exists"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    if does_the_email_exist:
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="This email already exists"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    insert_one_result = await collection_repository.insert_document(data_user)

    data = [
        UserOut(username=data_user["username"], email=data_user["email"]).model_dump()
    ]

    await create_categories(
        user_id=insert_one_result.inserted_id, username=data_user["username"]
    )

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="User created", data=data)


@router.delete("/{_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def del_document(_id: str):
    # TODO Devo chamar uma função aqui também que deleta o DB pantry do usuário porque e se ele quiser voltar a usar o App?

    if not ObjectId.is_valid(_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {"_id": ObjectId(_id)}

    delete_result = await collection_repository.delete_document(filter_document)

    print(_id)

    if not delete_result.deleted_count:
        response = DefaultAnswer(
            status=StatusMsg.FAIL, msg="user not found"
        ).model_dump()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=response)

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="User deleted")


@router.put("/{user_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def update_document(user_id: str, data_user_update: UserInUpdate):

    # TODO: Faz sentido esses updates estarem na mesma rota no caso eu deveria criar rotas para cada attr do usuário a ser atualizado.

    # TODO: Precisa criar o método de atualizar o user name da collection pantry também

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {"_id": ObjectId(user_id)}

    # Verifica se o usuário existe
    existing_user = await collection_repository.find_document_one(filter_document)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="User not found"
            ).model_dump(),
        )

    # Verifica se o username já está em uso
    if data_user_update.username:
        if await collection_repository.find_document_one(
            {"username": data_user_update.username}
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=DefaultAnswer(
                    status=StatusMsg.FAIL, msg="Username already in use"
                ).model_dump(),
            )

    # Verifica se o email já está em uso
    if data_user_update.email:
        if await collection_repository.find_document_one(
            {"email": data_user_update.email}
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=DefaultAnswer(
                    status=StatusMsg.FAIL, msg="Email already in use"
                ).model_dump(),
            )

    # Removendo os attr com valores None
    request_attribute = {"$set": data_user_update.model_dump(exclude_unset=True)}

    # Atualiza o documento no MongoDB
    update_result = await collection_repository.update_document(
        filter_document=filter_document, request_attribute=request_attribute
    )

    if update_result.modified_count == 1:

        # TODO: Após atualizado o usuário, no caso do username ele atualiza na collection pantry. Nesse caso ele vai atualizar mesmo que nome se a que ele já em lá logo preciso mudar essa func de lugar.
        if data_user_update.username:
            await update_username_pantry(user_id, data_user_update.username)

        return DefaultAnswer(
            status=StatusMsg.SUCCESS, msg="User updated successfully"
        ).model_dump()
    else:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="User not modified"
            ).model_dump(),
        )
