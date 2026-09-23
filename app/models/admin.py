"""Modelo de negócio Admin: perfil que gerencia (cria, altera e remove) os cafés e escreve comentários."""
from app.extensions import db
from app.models._util import agora_utc


class Admin(db.Model):
    """Administrador autenticado por e-mail e senha (guardada apenas como hash)."""

    __tablename__ = "admin"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora_utc)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    comentarios = db.relationship(
        "Comentario", back_populates="admin", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Admin {self.id} {self.email!r}>"
