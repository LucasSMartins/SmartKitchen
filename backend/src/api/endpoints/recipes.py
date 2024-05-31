from fastapi import APIRouter, HTTPException
from models.connection_options.connectiionCollection import minha_collection_repository
from bson.objectid import ObjectId
from typing import Dict, List


router = APIRouter()


@router.get('/')
async def recipes(id: str) -> List[Dict]:
    data = minha_collection_repository.find_document(
        {}, {"_id": 0}) if not id else minha_collection_repository.find_document({"_id": ObjectId(id)}, {"_id": 0})
    return data


@router.post('/')
async def create_recipe(data: Dict) -> Dict:
    try:
        minha_collection_repository.insert_document(data)
        return {"result": 'success'}
    except:
        raise HTTPException(status_code=400, detail="Erro nos tipo de dados")


@router.put("/{id}")
def update_recipe(id: str, data: Dict) -> str:
    try:
        minha_collection_repository.update_document(id, data)
        return 'success'
    except:
        return 'error'


@router.delete("/{id}")
def delete_recipe(id: str) -> str:
    minha_collection_repository.delete_document(id)
    return 'success'
