"""Modelo de negócio Comentario: opinião do Admin sobre um café."""
from app.extensions import db
from app.models._util import agora_utc


class Comentario(db.Model):
    """Comentário (com nota de 1 a 5) escrito pelo Admin sobre um café local."""

    __tablename__ = "comentario"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    admin_id = db.Column(
        db.Integer, db.ForeignKey("admin.id", ondelete="CASCADE"), nullable=False, index=True
    )
    cafe_id = db.Column(
        db.Integer, db.ForeignKey("cafe.id", ondelete="CASCADE"), nullable=False, index=True
    )
    texto = db.Column(db.Text, nullable=False)
    nota = db.Column(db.Integer, nullable=False)
    criado_em = db.Column(db.DateTime, nullable=False, default=agora_utc)

    admin = db.relationship("Admin", back_populates="comentarios")
    cafe = db.relationship("Cafe", back_populates="comentarios")

    def __repr__(self) -> str:
        return f"<Comentario {self.id} cafe={self.cafe_id} admin={self.admin_id}>"
