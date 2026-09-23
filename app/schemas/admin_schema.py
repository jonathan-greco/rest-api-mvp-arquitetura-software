"""Schemas do Admin: login e dados públicos (nunca expõem o hash da senha)."""
from marshmallow import RAISE, Schema, fields, validate

from app.schemas.campos import EmailNormalizado


class LoginSchema(Schema):
    """Credenciais enviadas no login."""

    class Meta:
        unknown = RAISE

    email = EmailNormalizado(required=True, validate=validate.Length(max=254))
    # Sem regras de formato aqui: a senha só é comparada com o hash, nunca interpretada.
    senha = fields.Str(required=True, validate=validate.Length(min=1, max=128))


class AdminSchema(Schema):
    """Saída de dados do administrador autenticado."""

    id = fields.Int()
    nome = fields.Str()
    email = fields.Str()
    ativo = fields.Bool()
    criado_em = fields.DateTime()
    ultimo_login = fields.DateTime(allow_none=True)
