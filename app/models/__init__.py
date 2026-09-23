"""Importa todos os modelos para que o SQLAlchemy os registre antes de criar as tabelas."""
from app.models.admin import Admin
from app.models.cafe import Cafe
from app.models.comentario import Comentario

__all__ = ["Admin", "Cafe", "Comentario"]
