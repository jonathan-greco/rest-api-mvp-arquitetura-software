"""Regras de negócio do Comentario."""
from app.errors.exceptions import NaoEncontradoError, ValidacaoError
from app.models import Comentario
from app.repositories.base import RepositorioBase


class ComentarioService:
    def __init__(
        self,
        repositorio: RepositorioBase,
        admin_repositorio: RepositorioBase,
        cafe_repositorio: RepositorioBase,
    ):
        self._repo = repositorio
        self._admins = admin_repositorio
        self._cafes = cafe_repositorio

    def list(self, filtros, ordenar_por, direcao, pagina, por_pagina):
        return self._repo.list(filtros, ordenar_por, direcao, pagina, por_pagina)

    def get(self, id_: int) -> Comentario:
        comentario = self._repo.get(id_)
        if comentario is None:
            raise NaoEncontradoError(f"Comentário {id_} não encontrado.")
        return comentario

    def criar(self, dados: dict) -> Comentario:
        # Comentário só pode apontar para admin e café que existem no nosso banco.
        erros = {}
        if self._admins.get(dados["admin_id"]) is None:
            erros["admin_id"] = ["Administrador não encontrado."]
        if self._cafes.get(dados["cafe_id"]) is None:
            erros["cafe_id"] = ["Café não encontrado no banco local."]
        if erros:
            raise ValidacaoError("Referência inválida.", erros)
        return self._repo.criar(dados)

    def atualizar(self, id_: int, dados: dict) -> Comentario:
        return self._repo.atualizar(self.get(id_), dados)

    def remover(self, id_: int) -> None:
        self._repo.remover(self.get(id_))
