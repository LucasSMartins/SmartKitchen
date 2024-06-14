from turtle import up
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, status

from models.connection_options.connections import DBConnectionHandler
from models.connection_options.mongo_db_config import mongo_db_infos
from models.repository.collections import CollectionHandler
from src.api.schema.default_answer import DefaultAnswer, StatusMsg
from src.api.schema.pantry import ItemsIn, ItemsOut

router = APIRouter()


db_handler = DBConnectionHandler()
db_handler.connect_to_db(mongo_db_infos["DB_NAME"])
db_connection = db_handler.get_db_connection()
collection_repository = CollectionHandler(
    db_connection, mongo_db_infos["COLLECTIONS"]["collection_pantry"]  # type: ignore
)


@router.get("/", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def read_pantry():

    request_attribute = {"_id": 0}

    data = await collection_repository.find_document(
        request_attribute=request_attribute
    )

    # Iterar sobre cada dicionário na lista de dados
    for user in data:
        # Verificar se o atributo user_id está presente e é um ObjectId
        if "user_id" in user and isinstance(user["user_id"], ObjectId):
            # Converter ObjectId para str e atribuir de volta ao atributo user_id
            user["user_id"] = str(user["user_id"])

    if not data:
        response = DefaultAnswer(status="fail", msg="Pantry not found").model_dump()
        raise HTTPException(status_code=404, detail=response)

    return DefaultAnswer(status="success", msg="Pantry found", data=data)


@router.get("/{user_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def read_user(
    user_id: Annotated[
        str,
        Path(
            title="The ID of the item to get",
            description="The unique identifier for the item, represented as a MongoDB ObjectId",
            regex=r"^[a-fA-F0-9]{24}$",
        ),
    ]
):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {"user_id": ObjectId(user_id)}
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document_one(
        filter_document, request_attribute
    )

    data[0]["user_id"] = str(data[0]["user_id"])

    if not data:
        raise HTTPException(
            status_code=404,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Pantry not found"
            ).model_dump(),
        )

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="Pantry found", data=data)


@router.post(
    "/{user_id}", response_model=DefaultAnswer, status_code=status.HTTP_201_CREATED
)
async def create_items(user_id: str, category_name: str, data_items: ItemsIn):

    # VRF se o user_id é válido como ObjectID.
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {
        "user_id": ObjectId(user_id),
        "pantry.category_name": category_name,
    }

    result_find = await collection_repository.find_document_one(
        filter_document={"user_id": ObjectId(user_id)},
        request_attribute={"_id": 0, "password": 0},
    )

    if not result_find:
        raise HTTPException(
            status_code=404,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Pantry not found"
            ).model_dump(),
        )

    # TODO Qual situação é a melhor para esse caso.

    #  $push ->> Adiciona um novo item a uma lista mesmo que tenha um exatamente igual.
    # request_attribute = {"$push": {"pantry.$.items": data_items.model_dump()}}

    #  $addToSet ->> Adiciona um novo item a lista mas se houver um exatamente igual ele não adiciona mas retorna um 200.
    # request_attribute = {"$addToSet": {"pantry.$.items": data_items.model_dump()}}

    item_id = ObjectId()
    data = ItemsOut(item_id=item_id, **data_items.model_dump())

    request_attribute = {"$addToSet": {"pantry.$.items": data.model_dump()}}

    update_result = await collection_repository.update_document(
        filter_document, request_attribute
    )

    if update_result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="User or category not found"
            ).model_dump(),
        )

    return DefaultAnswer(
        status=StatusMsg.SUCCESS, msg="The item was successfully added"
    ).model_dump()


@router.delete(
    "/{item_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK
)
async def delete_item(user_id: str, item_id: str, category_name: str):

    # TODO: Faz sentido receber o category_name pela url? ou devo receber pela query mesmo.

    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {
        "user_id": user_id,
        "pantry.category_name": category_name,
        "pantry.items.item_id": item_id,
    }

    request_attribute = {"$pull": {"pantry.$[category].items": {"item_id": item_id}}}

    array_filters = [{"category.category_name": category_name}]

    # Atualiza o documento removendo o item com o item_id especificado
    update_result = await collection_repository.update_document(
        filter_document, request_attribute, array_filters
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="No items were found"
            ).model_dump(),
        )

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="Item deleted successfully")


# TODO criar o put dos attr dos items


async def create_categories(user_id: ObjectId, username: str):
    """
    TODO Oque é melhor nessa situação, receber um modelo do banco, depois fazer um update ou enviar esses dados abaixo mesmo fazendo apenas um insert??
    """

    pantry_model = {
        "user_id": user_id,
        "username": username,
        "pantry": [
            {"category_name": "Candy", "items": []},
            {"category_name": "Frozen", "items": []},
            {"category_name": "Drinks", "items": []},
            {"category_name": "Laundry", "items": []},
            {"category_name": "Meat and Fish", "items": []},
            {"category_name": "Dairy and Eggs", "items": []},
            {"category_name": "Grocery Products", "items": []},
            {"category_name": "Personal hygiene", "items": []},
            {"category_name": "Grains and Cereals", "items": []},
            {"category_name": "Cleaning materials", "items": []},
            {"category_name": "Fruits and vegetables", "items": []},
            {"category_name": "Condiments and Sauces", "items": []},
            {"category_name": "Pasta and Wheat Products", "items": []},
            {"category_name": "Breads and Bakery Products", "items": []},
            {"category_name": "Canned goods and preserves", "items": []},
        ],
    }

    await collection_repository.insert_document(pantry_model)


async def update_username_pantry(user_id: str, username: str):

    filter_document = {"user_id": ObjectId(user_id)}

    request_attribute = {"$set": {"username": username}}

    await collection_repository.update_document(filter_document, request_attribute)
