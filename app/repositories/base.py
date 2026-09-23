"""Contrato (interface) dos repositórios.

Os services dependem desta abstração, não do SQLAlchemy (Inversão de Dependência)
"""
from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class RepositorioBase(ABC, Generic[T]):
    """CRUD genérico de uma entidade."""

    @abstractmethod
    def list(
        self,
        filtros: dict[str, Any] | None = None,
        ordenar_por: str = "id",
        direcao: str = "asc",
        pagina: int | None = None,
        por_pagina: int = 20,
    ) -> tuple[list[T], int]:
        """Retorna (itens da página, total). Com `pagina=None`, retorna todos os itens."""

    @abstractmethod
    def get(self, id_: int) -> T | None:
        """Retorna a entidade pelo id ou None."""

    @abstractmethod
    def criar(self, dados: dict[str, Any]) -> T:
        """Cria e persiste uma entidade."""

    @abstractmethod
    def atualizar(self, entidade: T, dados: dict[str, Any]) -> T:
        """Atualiza os campos informados e persiste."""

    @abstractmethod
    def remover(self, entidade: T) -> None:
        """Remove a entidade."""
