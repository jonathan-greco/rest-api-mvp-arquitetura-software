"""Modelo de negócio Cafe.

Campos alinhados ao formato da API externa SampleAPIs Coffee
(https://api.sampleapis.com/coffee/hot e /iced): title, description, ingredients, image, id.
"""
from app.extensions import db


class Cafe(db.Model):
    """Café cadastrado no banco local (SQLite)."""

    __tablename__ = "cafe"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(120), nullable=False, index=True)  # SampleAPIs: title
    descricao = db.Column(db.Text, nullable=True)  # SampleAPIs: description
    # Ingredientes guardados como texto separado por vírgula (ex.: "Espresso, Leite vaporizado");
    # a API sempre expõe como lista (list[str]). SampleAPIs: ingredients
    ingredientes = db.Column(db.Text, nullable=True)
    imagem_url = db.Column(db.String(500), nullable=True)  # SampleAPIs: image

    # Ao excluir o café, seus comentários são removidos em cascata.
    comentarios = db.relationship(
        "Comentario", back_populates="cafe", cascade="all, delete-orphan", passive_deletes=True
    )

    def __repr__(self) -> str:
        return f"<Cafe {self.id} {self.nome!r}>"
