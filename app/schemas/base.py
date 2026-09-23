"""Schemas base: paginação e ordenação comuns às listagens."""
from marshmallow import RAISE, Schema, fields, validate


class ListagemBaseSchema(Schema):
    """Parâmetros de query comuns (página, tamanho, direção). Parâmetros desconhecidos são recusados."""

    class Meta:
        unknown = RAISE

    pagina = fields.Int(load_default=1, validate=validate.Range(min=1, max=100000))
    por_pagina = fields.Int(load_default=20, validate=validate.Range(min=1, max=100))
    direcao = fields.Str(load_default="asc", validate=validate.OneOf(["asc", "desc"]))
