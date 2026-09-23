"""Modelo de negócio Usuario (cadastro simples: nome e e-mail)."""
from datetime import datetime, timezone

from app.extensions import db


def agora_utc() -> datetime:
    """Data/hora atual em UTC, usada como valor padrão de criado_em."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Usuario(db.Model):
    """Usuário que pode comentar cafés."""

    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora_utc)

    comentarios = db.relationship(
        "Comentario", back_populates="usuario", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Usuario {self.id} {self.email!r}>"
