"""Schemas de validação e serialização do Usuario."""
from marshmallow import RAISE, Schema, fields, validate

from app.schemas.base import ListagemBaseSchema
from app.schemas.campos import EmailNormalizado, TextoSeguro


class UsuarioSchema(Schema):
    """Entrada (POST/PUT) e saída de usuário: apenas nome e e-mail."""

    class Meta:
        unknown = RAISE

    id = fields.Int(dump_only=True)
    nome = TextoSeguro(required=True, validate=validate.Length(min=2, max=120))
    email = EmailNormalizado(required=True, validate=validate.Length(max=254))
    criado_em = fields.DateTime(dump_only=True)


class UsuarioListagemSchema(ListagemBaseSchema):
    """Ordenação da listagem de usuários."""

    ordenar_por = fields.Str(
        load_default="id", validate=validate.OneOf(["id", "nome", "email", "criado_em"])
    )
