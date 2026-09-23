"""Consulta pública de cafés: combina o banco local com a API externa SampleAPIs Coffee."""
from flask import Blueprint, jsonify

from app.routes.utils import carregar_query, container
from app.schemas.cafe_schema import CafeConsultaSchema, CafePublicoListagemSchema

cafes_bp = Blueprint("cafes", __name__, url_prefix="/api/v1/cafes")

_listagem_schema = CafePublicoListagemSchema()
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
    params = carregar_query(_listagem_schema)
    incluir_externos = params.pop("incluir_externos")
    pagina, por_pagina = params.pop("pagina"), params.pop("por_pagina")
    ordenar_por, direcao = params.pop("ordenar_por"), params.pop("direcao")
    resultado = container().cafe_service.list_publico(
        params, ordenar_por, direcao, pagina, por_pagina, incluir_externos
    )
    return jsonify(resultado)


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
