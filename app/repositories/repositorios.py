"""Repositórios concretos de cada entidade."""
from app.models import Admin, Cafe, Comentario
from app.repositories.sqlalchemy_repositorio import RepositorioSQLAlchemy


class CafeRepositorio(RepositorioSQLAlchemy):
    modelo = Cafe
    filtros_contem = frozenset({"nome"})
    colunas_ordenaveis = frozenset({"id", "nome"})


class ComentarioRepositorio(RepositorioSQLAlchemy):
    modelo = Comentario
    filtros_igual = frozenset({"cafe_id", "admin_id"})
    colunas_ordenaveis = frozenset({"id", "nota", "criado_em", "cafe_id"})


class AdminRepositorio(RepositorioSQLAlchemy):
    modelo = Admin

    def buscar_por_email(self, email: str) -> Admin | None:
        return Admin.query.filter_by(email=email).first()
