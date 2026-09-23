"""CRUD de usuários (cadastro simples: nome e e-mail)."""
from flask import Blueprint, jsonify

from app.routes.utils import carregar_query, container, get_json, resposta_paginada
from app.schemas.usuario_schema import UsuarioListagemSchema, UsuarioSchema

usuarios_bp = Blueprint("usuarios", __name__, url_prefix="/api/v1/usuarios")

_schema = UsuarioSchema()
_listagem_schema = UsuarioListagemSchema()


@usuarios_bp.post("")
def criar_usuario():
    """Cadastra um usuário.
    ---
    tags: [Usuários]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/UsuarioEntrada'
    responses:
      201:
        description: Usuário criado
        schema:
          $ref: '#/definitions/Usuario'
      409:
        description: E-mail já cadastrado
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _schema.load(get_json())
    return jsonify(_schema.dump(container().usuario_service.criar(dados))), 201


@usuarios_bp.get("")
def list_usuarios():
    """Lista usuários com paginação e ordenação.
    ---
    tags: [Usuários]
    parameters:
      - {in: query, name: ordenar_por, type: string, enum: [id, nome, email, criado_em], default: id}
      - {in: query, name: direcao, type: string, enum: [asc, desc], default: asc}
      - {in: query, name: pagina, type: integer, default: 1}
      - {in: query, name: por_pagina, type: integer, default: 20}
    responses:
      200:
        description: Lista de usuários
        schema:
          $ref: '#/definitions/ListaUsuarios'
    """
    p = carregar_query(_listagem_schema)
    itens, total = container().usuario_service.list(p["ordenar_por"], p["direcao"], p["pagina"], p["por_pagina"])
    return jsonify(resposta_paginada(itens, total, p["pagina"], p["por_pagina"], _schema))


@usuarios_bp.get("/<int:id_>")
def get_usuario(id_: int):
    """Busca um usuário pelo id.
    ---
    tags: [Usuários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      200:
        description: Usuário encontrado
        schema:
          $ref: '#/definitions/Usuario'
      404:
        description: Usuário não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    return jsonify(_schema.dump(container().usuario_service.get(id_)))


@usuarios_bp.put("/<int:id_>")
def atualizar_usuario(id_: int):
    """Atualiza nome e e-mail de um usuário.
    ---
    tags: [Usuários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/UsuarioEntrada'
    responses:
      200:
        description: Usuário atualizado
        schema:
          $ref: '#/definitions/Usuario'
      404:
        description: Usuário não encontrado
        schema:
          $ref: '#/definitions/Erro'
      409:
        description: E-mail já cadastrado
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    dados = _schema.load(get_json())
    return jsonify(_schema.dump(container().usuario_service.atualizar(id_, dados)))


@usuarios_bp.delete("/<int:id_>")
def remover_usuario(id_: int):
    """Remove um usuário (e os comentários dele).
    ---
    tags: [Usuários]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
    responses:
      204:
        description: Usuário removido
      404:
        description: Usuário não encontrado
        schema:
          $ref: '#/definitions/Erro'
    """
    container().usuario_service.remover(id_)
    return "", 204
