"""Funções auxiliares compartilhadas pelas rotas."""
from flask import current_app, request

from app.errors.exceptions import RequisicaoInvalidaError


def container():
    """Retorna o container de dependências da aplicação atual."""
    return current_app.extensions["container"]


def get_json() -> dict:
    """Lê o corpo JSON; recusa corpo ausente, malformado ou que não seja um objeto."""
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        raise RequisicaoInvalidaError(
            "O corpo da requisição deve ser um objeto JSON (Content-Type: application/json)."
        )
    return dados


def carregar_query(schema) -> dict:
    """Valida os parâmetros de query com um schema; parâmetros desconhecidos são recusados."""
    return schema.load(request.args.to_dict())


def resposta_paginada(itens: list, total: int, pagina: int, por_pagina: int, schema) -> dict:
    """Monta o envelope padrão de listagem."""
    return {
        "itens": schema.dump(itens, many=True),
        "total": total,
        "pagina": pagina,
        "por_pagina": por_pagina,
    }
