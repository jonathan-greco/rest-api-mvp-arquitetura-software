"""Schemas de validação e serialização do Comentario."""
from marshmallow import RAISE, Schema, fields, validate

from app.schemas.base import ListagemBaseSchema
from app.schemas.campos import TextoSeguro


class ComentarioSchema(Schema):
    """Criação (POST) e saída de comentário."""

    class Meta:
        unknown = RAISE

    id = fields.Int(dump_only=True)
    usuario_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    cafe_id = fields.Int(required=True, strict=True, validate=validate.Range(min=1))
    texto = TextoSeguro(required=True, validate=validate.Length(min=1, max=1000))
    nota = fields.Int(required=True, strict=True, validate=validate.Range(min=1, max=5))
    criado_em = fields.DateTime(dump_only=True)


class ComentarioAtualizacaoSchema(Schema):
    """Atualização (PUT): só texto e nota mudam; autor e café do comentário são fixos."""

    class Meta:
        unknown = RAISE

    texto = TextoSeguro(required=True, validate=validate.Length(min=1, max=1000))
    nota = fields.Int(required=True, strict=True, validate=validate.Range(min=1, max=5))


class ComentarioListagemSchema(ListagemBaseSchema):
    """Filtros e ordenação da listagem de comentários."""

    cafe_id = fields.Int(validate=validate.Range(min=1))
    usuario_id = fields.Int(validate=validate.Range(min=1))
    ordenar_por = fields.Str(
        load_default="id", validate=validate.OneOf(["id", "nota", "criado_em", "cafe_id"])
    )
