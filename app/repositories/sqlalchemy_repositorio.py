"""Implementação genérica do repositório com SQLAlchemy.

Proteção contra SQL injection: todo acesso usa o ORM/expressões do SQLAlchemy,
que enviam os valores como parâmetros vinculados (bind parameters). Nomes de
colunas usados em filtro e ordenação vêm de listas permitidas (whitelist) e
nunca diretamente da entrada do usuário.
"""
from typing import Any

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError

from app.errors.exceptions import ConflitoError
from app.extensions import db
from app.repositories.base import RepositorioBase


class RepositorioSQLAlchemy(RepositorioBase):
    """CRUD reutilizável; as subclasses só declaram o modelo e os filtros permitidos."""

    modelo: type = None
    # Filtros por contém (texto, sem diferenciar maiúsculas) e por igualdade.
    filtros_contem: frozenset[str] = frozenset()
    filtros_igual: frozenset[str] = frozenset()
    colunas_ordenaveis: frozenset[str] = frozenset({"id"})

    def _aplicar_filtros(self, consulta, filtros: dict[str, Any]):
        for campo, valor in (filtros or {}).items():
            if valor is None:
                continue
            coluna = getattr(self.modelo, campo, None)
            if coluna is None:
                continue
            if campo in self.filtros_contem:
                # autoescape trata %, _ e \ do valor como texto literal.
                consulta = consulta.filter(func.lower(coluna).contains(str(valor).lower(), autoescape=True))
            elif campo in self.filtros_igual:
                consulta = consulta.filter(coluna == valor)
            # Campos fora das listas permitidas são ignorados.
        return consulta

    def list(self, filtros=None, ordenar_por="id", direcao="asc", pagina=None, por_pagina=20):
        consulta = self._aplicar_filtros(self.modelo.query, filtros or {})
        total = consulta.count()

        # Ordenação só por colunas da whitelist; qualquer outra cai no id.
        nome_coluna = ordenar_por if ordenar_por in self.colunas_ordenaveis else "id"
        coluna = getattr(self.modelo, nome_coluna)
        consulta = consulta.order_by(coluna.desc() if direcao == "desc" else coluna.asc())
        if nome_coluna != "id":
            consulta = consulta.order_by(self.modelo.id.asc())

        if pagina is not None:
            consulta = consulta.limit(por_pagina).offset((pagina - 1) * por_pagina)
        return consulta.all(), total

    def get(self, id_):
        return db.session.get(self.modelo, id_)

    @staticmethod
    def _confirmar() -> None:
        """Confirma a transação; violações de integridade (ex.: e-mail duplicado) viram ConflitoError."""
        try:
            db.session.commit()
        except IntegrityError as erro:
            db.session.rollback()
            raise ConflitoError("Operação viola uma regra de integridade dos dados.") from erro

    def criar(self, dados):
        entidade = self.modelo(**dados)
        db.session.add(entidade)
        self._confirmar()
        return entidade

    def atualizar(self, entidade, dados):
        for campo, valor in dados.items():
            setattr(entidade, campo, valor)
        self._confirmar()
        return entidade

    def remover(self, entidade):
        db.session.delete(entidade)
        db.session.commit()
