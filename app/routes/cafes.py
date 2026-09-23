"""CRUD de Café: a própria coleção /api/v1/cafes gerencia seus registros.

A leitura (GET, combinando banco local + SampleAPIs Coffee, com `?origem=local` para
restringir só ao banco) é toda pública; só a escrita (POST/PUT/DELETE) exige login de Admin.
"""
from flask import Blueprint, jsonify

from app.routes.decorators import admin_required
from app.routes.utils import carregar_query, container, get_json
from app.schemas.cafe_schema import CafeConsultaSchema, CafePublicoListagemSchema, CafeSchema

cafes_bp = Blueprint("cafes", __name__, url_prefix="/api/v1/cafes")

_schema = CafeSchema()
_listagem_publica_schema = CafePublicoListagemSchema()
_consulta_schema = CafeConsultaSchema()


@cafes_bp.get("")
def list_cafes():
    """Lista cafés do banco local concatenados com os da SampleAPIs Coffee que faltam no banco.
    A fonte externa expõe cafés quentes (hot) e gelados (iced) em endpoints separados; aqui os
    dois são buscados juntos, sem distinção. Itens externos vêm com `origem: externa`, `id: null`
    e o id da fonte em `id_externo`. Se a fonte estiver fora do ar, retorna só os dados locais
    (`fonte_externa: indisponivel`).
    ---
    tags: [Cafés]
    parameters:
      - {in: query, name: nome, type: string, description: "Contém (sem diferenciar maiúsculas/acentos)"}
      - {in: query, name: incluir_externos, type: boolean, default: true, description: "false = só banco local"}
      - {in: query, name: ordenar_por, type: string, enum: [id, nome], default: id}
      - {in: query, name: direcao, type: string, enum: [asc, desc], default: asc}
      - {in: query, name: pagina, type: integer, default: 1}
      - {in: query, name: por_pagina, type: integer, default: 20}
    responses:
      200:
        description: Lista combinada de cafés
        schema:
          $ref: '#/definitions/ListaCafes'
      422:
        description: Parâmetros inválidos
        schema:
          $ref: '#/definitions/Erro'
    """
    params = carregar_query(_listagem_publica_schema)
    incluir_externos = params.pop("incluir_externos")
    pagina, por_pagina = params.pop("pagina"), params.pop("por_pagina")
    ordenar_por, direcao = params.pop("ordenar_por"), params.pop("direcao")
    resultado = container().cafe_service.list_publico(
        params, ordenar_por, direcao, pagina, por_pagina, incluir_externos
    )
    return jsonify(resultado)


@cafes_bp.post("")
@admin_required
def criar_cafe():
    """Cria um café no banco local. Exige login de Admin.
    ---
    tags: [Cafés]
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


@cafes_bp.get("/<int:id_>")
def get_cafe(id_: int):
    """Busca um café por id.
    Por padrão procura no banco local e, se não achar, consulta a SampleAPIs Coffee.
    Use `origem=externa` para consultar diretamente pelo `id_externo` de um item da fonte
    (busca nas listas hot e iced; em caso de colisão de id entre elas, o primeiro achado vence).
    ---
    tags: [Cafés]
    parameters:
      - {in: path, name: id_, type: integer, required: true}
      - {in: query, name: origem, type: string, enum: [auto, local, externa], default: auto}
    responses:
      200:
        description: Café encontrado
        schema:
          $ref: '#/definitions/Cafe'
      404:
        description: Café não encontrado
        schema:
          $ref: '#/definitions/Erro'
      502:
        description: SampleAPIs Coffee indisponível (quando a consulta externa era necessária)
        schema:
          $ref: '#/definitions/Erro'
    """
    origem = carregar_query(_consulta_schema)["origem"]
    return jsonify(container().cafe_service.get_publico(id_, origem))


@cafes_bp.put("/<int:id_>")
@admin_required
def atualizar_cafe(id_: int):
    """Atualiza (substitui) os dados de um café local. Campos opcionais omitidos ficam vazios. Exige login de Admin.
    ---
    tags: [Cafés]
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


@cafes_bp.delete("/<int:id_>")
@admin_required
def remover_cafe(id_: int):
    """Remove um café local (e os comentários dele). Exige login de Admin.
    ---
    tags: [Cafés]
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
