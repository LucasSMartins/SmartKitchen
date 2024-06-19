from enum import Enum
from typing import Dict

from pydantic import BaseModel


class StatusMsg(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    FAIL = "fail"


class DefaultAnswer(BaseModel):
    status: StatusMsg
    msg: str
    data: list[Dict] | None = None


"""
    TODO: É correto ou não cria um padrão de resposta para cada rota ?
    por exemplo eu deveria ter um padrão de resposta para o /pantry e outra para o /users

    O motivo disso é que lá em pantry e em shopping_cart o retorno contém um ObjectId e o pydantic não sereliza isso. consegui corrigir com uma lib mas,
    como a resposta padrão diz que o retorno será um Dict ele não aceita o tratamento porque o que vem do banco não é tratado, eu resolvi isso convertendo o para uma string. 
"""
