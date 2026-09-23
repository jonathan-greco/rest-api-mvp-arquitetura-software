"""Mapper: equivalência entre os campos do nosso Cafe (português) e os da SampleAPIs Coffee (inglês).

Formato da fonte externa (https://api.sampleapis.com/coffee/hot e /iced):
{"title": "Latte", "description": "...", "ingredients": ["Espresso", "Steamed milk"], "image": "https://...", "id": 2}

Toda a correspondência fica em `EQUIVALENCIA_CAMPOS`. Se a API externa mudar um
nome de campo, só este dicionário precisa ser alterado.
"""
from typing import Any

# campo local (português) -> campo da SampleAPIs Coffee (inglês)
EQUIVALENCIA_CAMPOS: dict[str, str] = {
    "nome": "title",
    "descricao": "description",
    "ingredientes": "ingredients",
    "imagem_url": "image",
}

ORIGEM_EXTERNA = "externa"
ORIGEM_LOCAL = "local"


def _para_texto(valor: Any) -> str | None:
    """Converte para texto simples; usado em nome, descrição e URL da imagem."""
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto or None


def _para_id_externo(valor: Any) -> int | None:
    """Normaliza o id da fonte externa para int (ou None quando malformado).

    A SampleAPIs Coffee às vezes devolve ids inválidos (ex.: a string "number" ou
    um número como texto, como "123456") em vez de um inteiro. Tratamos qualquer
    valor que não converta para int como ausente, para nunca quebrar comparações
    e ordenações mais adiante.
    """
    if valor is None:
        return None
    if isinstance(valor, bool):
        return None
    if isinstance(valor, int):
        return valor
    try:
        return int(str(valor).strip())
    except (TypeError, ValueError):
        return None


def _para_lista_texto(valor: Any) -> list[str]:
    """Normaliza ingredientes para lista de strings, aceitando lista, string única ou None."""
    if valor is None:
        return []
    if isinstance(valor, (list, tuple, set)):
        return [str(v).strip() for v in valor if str(v).strip()]
    texto = str(valor).strip()
    return [texto] if texto else []


class CafeMapper:
    """Converte cafés da SampleAPIs Coffee para o formato local e vice-versa."""

    @staticmethod
    def para_local(dado_externo: dict) -> dict:
        """Converte um item da SampleAPIs Coffee para o formato do nosso Cafe.

        O item retornado NÃO tem `id` local (é None): o id da fonte externa vai em
        `id_externo`, para nunca colidir com ids do nosso banco. Como a fonte não
        distingue quente/gelado para consulta, `id_externo` pode colidir entre os dois
        tipos (a fonte não expõe um id global único).
        """
        if not isinstance(dado_externo, dict):
            raise ValueError("Item externo em formato inesperado.")

        cafe = {
            "nome": _para_texto(dado_externo.get(EQUIVALENCIA_CAMPOS["nome"])),
            "descricao": _para_texto(dado_externo.get(EQUIVALENCIA_CAMPOS["descricao"])),
            "ingredientes": _para_lista_texto(dado_externo.get(EQUIVALENCIA_CAMPOS["ingredientes"])),
            "imagem_url": _para_texto(dado_externo.get(EQUIVALENCIA_CAMPOS["imagem_url"])),
        }
        cafe["id"] = None
        cafe["id_externo"] = _para_id_externo(dado_externo.get("id"))
        cafe["origem"] = ORIGEM_EXTERNA
        return cafe

    @staticmethod
    def para_externo(cafe_local: dict) -> dict:
        """Faz o caminho inverso (português -> inglês); útil para documentar e para futuras escritas."""
        return {
            "title": cafe_local.get("nome"),
            "description": cafe_local.get("descricao"),
            "ingredients": cafe_local.get("ingredientes") or [],
            "image": cafe_local.get("imagem_url"),
        }
