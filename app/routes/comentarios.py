"""CRUD de comentários: usuários escrevem sobre cafés do banco local."""
from flask import Blueprint, jsonify

from app.routes.utils import carregar_query, container, get_json, resposta_paginada
from app.schemas.comentario_schema import (
    ComentarioAtualizacaoSchema,
    ComentarioListagemSchema,
    ComentarioSchema,
)

comentarios_bp = Blueprint("comentarios", __name__, url_prefix="/api/v1/comentarios")

_schema = ComentarioSchema()
_atualizacao_schema = ComentarioAtualizacaoSchema()
_listagem_schema = ComentarioListagemSchema()


@comentarios_bp.post("")
def criar_comentario():
    """Cria um comentário de um usuário sobre um café do banco local.
    ---
    tags: [Comentários]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ComentarioEntrada'
    responses:
      201:
        description: Comentário criado
        schema:
          $ref: '#/definitions/Comentario'
      422:
        description: Dados inválidos ou usuário/café inexistente
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _schema.load(get_json())
    return jsonify(_schema.dump(container().comentario_service.criar(dados))), 201


@comentarios_bp.get("")
def list_comentarios():
    """Lista comentários, com filtros por café e por usuário.
    ---
    tags: [Comentários]
    parameters:
      - {in: query, name: cafe_id, type: integer}
      - {in: query, name: usuario_id, type: integer}
      - {in: query, name: ordenar_por, type: string, enum: [id, nota, criado_em, cafe_id], default: id}
      - {in: query, name: direcao, type: string, enum: [asc, desc], default: asc}
      - {in: query, name: pagina, type: integer, default: 1}
      - {in: query, name: por_pagina, type: integer, default: 20}
    responses:
      200:
        description: Lista de comentários
        schema:
          $ref: '#/definitions/ListaComentarios'
    """
    params = carregar_query(_listagem_schema)
    pagina, por_pagina = params.pop("pagina"), params.pop("por_pagina")
    ordenar_por, direcao = params.pop("ordenar_por"), params.pop("direcao")
    itens, total = container().comentario_service.list(params, ordenar_por, direcao, pagina, por_pagina)
    return jsonify(resposta_paginada(itens, total, pagina, por_pagina, _schema))


@comentarios_bp.get("/<int:id_>")
def get_comentario(id_: int):
    """Busca um comentário pelo id.
    ---
    tags: [Comentários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      200:
        description: Comentário encontrado
        schema:
          $ref: '#/definitions/Comentario'
      404:
        description: Comentário não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    return jsonify(_schema.dump(container().comentario_service.get(id_)))


@comentarios_bp.put("/<int:id_>")
def atualizar_comentario(id_: int):
    """Atualiza texto e nota de um comentário (autor e café não mudam).
    ---
    tags: [Comentários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/ComentarioAtualizacao'
    responses:
      200:
        description: Comentário atualizado
        schema:
          $ref: '#/definitions/Comentario'
      404:
        description: Comentário não encontrado
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _atualizacao_schema.load(get_json())
    return jsonify(_schema.dump(container().comentario_service.atualizar(id_, dados)))


@comentarios_bp.delete("/<int:id_>")
def remover_comentario(id_: int):
    """Remove um comentário.
    ---
    tags: [Comentários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      204:
        description: Comentário removido
      404:
        description: Comentário não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    container().comentario_service.remover(id_)
    return "", 204
