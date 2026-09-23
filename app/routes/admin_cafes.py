"""Gestão de cafés pelo Admin (POST, GET, PUT e DELETE), somente no banco local."""
from flask import Blueprint, jsonify

from app.routes.decorators import admin_required
from app.routes.utils import carregar_query, container, get_json, resposta_paginada
from app.schemas.cafe_schema import CafeListagemSchema, CafeSchema

admin_cafes_bp = Blueprint("admin_cafes", __name__, url_prefix="/api/v1/admin/cafes")

_schema = CafeSchema()
_listagem_schema = CafeListagemSchema()


@admin_cafes_bp.post("")
@admin_required
def criar_cafe():
    """Cria um café no banco local.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CafeEntrada'
    responses:
      201:
        description: Café criado
        schema:
          $ref: '#/definitions/Cafe'
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
      403:
        description: Sem permissão de admin
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _schema.load(get_json())
    cafe = container().cafe_service.criar(dados)
    return jsonify(_schema.dump(cafe)), 201


@admin_cafes_bp.get("")
@admin_required
def list_cafes():
    """Lista os cafés do banco local (sem a SampleAPIs Coffee), com filtros e paginação.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: query, name: nome, type: string}
      - {in: query, name: ordenar_por, type: string, enum: [id, nome], default: id}
      - {in: query, name: direcao, type: string, enum: [asc, desc], default: asc}
      - {in: query, name: pagina, type: integer, default: 1}
      - {in: query, name: por_pagina, type: integer, default: 20}
    responses:
      200:
        description: Lista de cafés locais
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
    """
    params = carregar_query(_listagem_schema)
    pagina, por_pagina = params.pop("pagina"), params.pop("por_pagina")
    ordenar_por, direcao = params.pop("ordenar_por"), params.pop("direcao")
    itens, total = container().cafe_service.list_local(params, ordenar_por, direcao, pagina, por_pagina)
    return jsonify(resposta_paginada(itens, total, pagina, por_pagina, _schema))


@admin_cafes_bp.get("/<int:id_>")
@admin_required
def get_cafe(id_: int):
    """Busca um café do banco local pelo id.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      200:
        description: Café encontrado
        schema:
          $ref: '#/definitions/Cafe'
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
      404:
        description: Café não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    return jsonify(_schema.dump(container().cafe_service.get_local(id_)))


@admin_cafes_bp.put("/<int:id_>")
@admin_required
def atualizar_cafe(id_: int):
    """Atualiza (substitui) os dados de um café local. Campos opcionais omitidos ficam vazios.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: id_, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/CafeEntrada'
    responses:
      200:
        description: Café atualizado
        schema:
          $ref: '#/definitions/Cafe'
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
      404:
        description: Café não encontrado
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _schema.load(get_json())
    return jsonify(_schema.dump(container().cafe_service.atualizar(id_, dados)))


@admin_cafes_bp.delete("/<int:id_>")
@admin_required
def remover_cafe(id_: int):
    """Remove um café local (e os comentários dele).
    ---
    tags: [Admin]
    security:
      - Bearer: []
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      204:
        description: Café removido
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
      404:
        description: Café não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    container().cafe_service.remover(id_)
    return "", 204
