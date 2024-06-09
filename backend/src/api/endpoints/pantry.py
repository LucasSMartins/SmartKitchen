from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, status

from models.connection_options.connections import DBConnectionHandler
from models.repository.collections import CollectionHandler
from src.api.schema.default_answer import Attr_Default_Answer, Default_Answer

router = APIRouter()

db_name = "smartkitchien"
collection = "pantry"

db_handler = DBConnectionHandler()
db_handler.connect_to_db(db_name)
db_connection = db_handler.get_db_connection()
collection_repository = CollectionHandler(db_connection, collection)


@router.get("/", status_code=status.HTTP_200_OK, response_model=Default_Answer)
async def read_pantry():
    request_attribute = {"_id": 0, "password": 0}

    data = await collection_repository.find_document(
        request_attribute=request_attribute
    )

    if not data:
        response = Default_Answer(
            detail=Attr_Default_Answer(status="fail", msg="Pantry not found")
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="Pantry found", data=data)
    )


@router.get("/{_id}", response_model=Default_Answer, status_code=status.HTTP_200_OK)
async def read_user(
    _id: Annotated[
        str,
        Path(
            title="The ID of the item to get",
            description="The unique identifier for the item, represented as a MongoDB ObjectId",
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
            detail=Attr_Default_Answer(status="fail", msg="Pantry not found")
        ).model_dump()
        raise HTTPException(status_code=404, detail=response)

    return Default_Answer(
        detail=Attr_Default_Answer(status="success", msg="Pantry found", data=data)
    )


async def create_categories(user_id: ObjectId, username: str):
    """
    TODO
    Oque é melhor nessa situação, receber um modelo do banco, depois fazer um update ou enviar esses dados abaixo
    mesmo fazendo apenas um insert??
    """

    pantry_model = {
        "user_id": user_id,
        "username": username,
        "pantry": {
            "categories": [
                {"category_name": "Grains and Cereals", "items": []},
                {"category_name": "Fruits and vegetables", "items": []},
                {"category_name": "Meat and Fish", "items": []},
                {"category_name": "Dairy and Eggs", "items": []},
                {"category_name": "Breads and Bakery Products", "items": []},
                {"category_name": "", "items": []},
                {"category_name": "Frozen", "items": []},
                {"category_name": "Pasta and Wheat Products", "items": []},
                {"category_name": "Canned goods and preserves", "items": []},
                {"category_name": "Drinks", "items": []},
                {"category_name": "Grocery Products", "items": []},
                {"category_name": "Candy", "items": []},
                {"category_name": "Condiments and Sauces", "items": []},
                {"category_name": "Cleaning materials", "items": []},
                {"category_name": "Personal hygiene", "items": []},
                {"category_name": "Laundry", "items": []},
            ]
        },
    }
    await collection_repository.insert_document(pantry_model)
