from pprint import pp
from typing import Annotated

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Path, Query, status
from httpx import request

from models.connection_options.connections import DBConnectionHandler
from models.connection_options.mongo_db_config import mongo_db_infos
from models.repository.collections import CollectionHandler
from src.api.schema.default_answer import DefaultAnswer, StatusMsg
from src.api.schema.pantry import CategoryValue, ItemsIn, ItemsOut

router = APIRouter()


db_handler = DBConnectionHandler()
db_handler.connect_to_db(mongo_db_infos["DB_NAME"])
db_connection = db_handler.get_db_connection()

collection_repository = CollectionHandler(
    db_connection, mongo_db_infos["COLLECTIONS"]["collection_pantry"]  # type: ignore
)


# TODO: Obtém a despensa de todos os usuários, não sei se faz sentido ter essa rota.
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


# Obter todas as categorias da despensa:
@router.get("/{user_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK)
async def read_user_pantry(
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

    if not data:
        raise HTTPException(
            status_code=404,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Pantry not found"
            ).model_dump(),
        )
    else:
        data[0]["user_id"] = str(data[0]["user_id"])

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="Pantry found", data=data)


# Obter todos os itens de uma categoria específica:
@router.get(
    "/category/{user_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK
)
async def all_items_specific_category(user_id: str, category_value: CategoryValue):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {
        "user_id": ObjectId(user_id),
        "pantry.category_value": category_value,
    }

    request_attribute = {"_id": 0, "pantry.$": 1}

    # Verifica se o usuário existe
    existing_user = await collection_repository.find_document_one(
        {"user_id": ObjectId(user_id)}
    )
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="User not found"
            ).model_dump(),
        )

    result_find = await collection_repository.find_document_one(
        filter_document, request_attribute
    )

    if not result_find:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Category not found"
            ).model_dump(),
        )

    return DefaultAnswer(
        status=StatusMsg.SUCCESS, msg="Pantry Items Found", data=result_find
    )


# Adicionar um novo item a uma categoria:
@router.post(
    "/{user_id}/category/{category_value}",
    response_model=DefaultAnswer,
    status_code=status.HTTP_201_CREATED,
)
async def create_items(
    user_id: str,
    category_value: Annotated[
        CategoryValue,
        Path(description="List of food category values, is a 3-digit integer value"),
    ],
    data_items: ItemsIn,
):
    """
    **List of food category values**\n
    Candy = 101,\n
    Frozen = 102,\n
    Drinks = 103,\n
    Laundry = 104,\n
    Meat and Fish = 105,\n
    Dairy and Eggs = 106,\n
    Grocery Products = 107,\n
    Personal hygiene = 108,\n
    Grains and Cereals = 109,\n
    Cleaning materials = 110,\n
    Fruits and vegetables = 111,\n
    Condiments and Sauces = 112,\n
    Pasta and Wheat Products = 113,\n
    Breads and Bakery Products = 114,\n
    Canned goods and preserves = 115,\n
    """

    # VRF se o user_id é válido como ObjectID.
    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

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

    # TODO O ID aqui é bom usar o ObjectID mesmo ou usa um incremental?
    item_id = ObjectId()
    data = ItemsOut(item_id=item_id, **data_items.model_dump())

    request_attribute = {"$addToSet": {"pantry.$.items": data.model_dump()}}

    filter_document = {
        "user_id": ObjectId(user_id),
        "pantry.category_value": category_value,
    }

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
    )


# Atualizar um item específico de uma categoria
@router.delete(
    "/{item_id}", response_model=DefaultAnswer, status_code=status.HTTP_200_OK
)
async def delete_item(user_id: str, item_id: str, category_value: CategoryValue):

    if not ObjectId.is_valid(item_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document = {
        "user_id": ObjectId(user_id),
        "pantry.category_value": category_value,
        "pantry.items.item_id": item_id,
    }

    request_attribute = {"$pull": {"pantry.$[element].items": {"item_id": item_id}}}

    # array_filters = [{"category.category_value": category_value}]
    array_filters = [{"element.category_value": category_value}]

    # Atualiza o documento removendo o item com o item_id especificado
    update_result = await collection_repository.update_document(
        filter_document=filter_document,  # Localiza o item
        request_attribute=request_attribute,  # Aplica a ação [remover o item]
        array_filters=array_filters,  # Condição
        # O operador posicional $[<identifier>] irá atuar como um espaço reservado para todos os elementos do campo selecionado que correspondem às condições que foram especificadas no arrayFiltros.
    )

    if update_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="No items were found"
            ).model_dump(),
        )

    return DefaultAnswer(status=StatusMsg.SUCCESS, msg="Item deleted successfully")


# TODO: Acabou que eu fiz uma rota em que ele adiciona um novo item após remover o id informado uma tentativa de update, mas acaba que se não houver o item a ser removido ele adiciona mesmo assim, e então uso essa rota, tanto para criar quanto para atualizar ou deixo assim porque tecnicamente eu agora tenho duas rotas iguais.
@router.put(
    "/{user_id}/category_value/{category_value}",
    response_model=DefaultAnswer,
    status_code=status.HTTP_200_OK,
)
async def Updates_pantry_item(
    user_id: str,
    item_id: str,
    category_value: CategoryValue,
    data_items_update: ItemsIn,
):

    if not ObjectId.is_valid(user_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Invalid user ID"
            ).model_dump(),
        )

    filter_document_pull = {
        "user_id": ObjectId(user_id),
        "pantry.category_value": category_value,
        "pantry.items.item_id": item_id,
    }

    # Remover o item
    request_pull = {"$pull": {"pantry.$[element].items": {"item_id": item_id}}}

    array_filters_pull = [
        {"element.category_value": category_value},
    ]

    # Executar a remoção do item
    pull_result = await collection_repository.update_document(
        filter_document=filter_document_pull,
        request_attribute=request_pull,
        array_filters=array_filters_pull,
    )

    if pull_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL,
                msg="The item was not found or was not removed",
            ).model_dump(),
        )

    filter_document_addtoset = {
        "user_id": ObjectId(user_id),
        "pantry.category_value": category_value,
    }

    # adiciona o item atualizado
    request_push = {
        "$addToSet": {
            "pantry.$.items": {"item_id": item_id, **data_items_update.model_dump()}
        }
    }

    # Executar a adição do item atualizado
    addtoset_result = await collection_repository.update_document(
        filter_document=filter_document_addtoset, request_attribute=request_push
    )

    if addtoset_result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail=DefaultAnswer(
                status=StatusMsg.FAIL, msg="Item not modified"
            ).model_dump(),
        )

    return DefaultAnswer(
        status=StatusMsg.SUCCESS, msg="Item updated successfully"
    ).model_dump()


async def create_categories(user_id: ObjectId, username: str):
    """
    TODO Oque é melhor nessa situação, receber um modelo do banco, depois fazer um update ou enviar esses dados abaixo mesmo fazendo apenas um insert??

    '101' == 52 bytes
     101  == 28 bytes
    """

    pantry_model = {
        "user_id": user_id,
        "username": username,
        "pantry": [
            {"category_value": 101, "category_name": "Candy", "items": []},
            {"category_value": 102, "category_name": "Frozen", "items": []},
            {"category_value": 103, "category_name": "Drinks", "items": []},
            {"category_value": 104, "category_name": "Laundry", "items": []},
            {"category_value": 105, "category_name": "Meat and Fish", "items": []},
            {"category_value": 106, "category_name": "Dairy and Eggs", "items": []},
            {"category_value": 107, "category_name": "Grocery Products", "items": []},
            {"category_value": 108, "category_name": "Personal hygiene", "items": []},
            {
                "category_value": 109,
                "category_name": "Grains and Cereals",
                "items": [],
            },
            {
                "category_value": 110,
                "category_name": "Cleaning materials",
                "items": [],
            },
            {
                "category_value": 111,
                "category_name": "Fruits and vegetables",
                "items": [],
            },
            {
                "category_value": 112,
                "category_name": "Condiments and Sauces",
                "items": [],
            },
            {
                "category_value": 113,
                "category_name": "Pasta and Wheat Products",
                "items": [],
            },
            {
                "category_value": 114,
                "category_name": "Breads and Bakery Products",
                "items": [],
            },
            {
                "category_value": 115,
                "category_name": "Canned goods and preserves",
                "items": [],
            },
        ],
    }

    await collection_repository.insert_document(pantry_model)


async def update_username_pantry(user_id: str, username: str):

    filter_document = {"user_id": ObjectId(user_id)}

    request_attribute = {"$set": {"username": username}}

    await collection_repository.update_document(filter_document, request_attribute)


async def delete_db_pantry():
    collection_repository.delete_many()
