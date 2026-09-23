"""Regras de negócio do Usuario."""
from app.errors.exceptions import ConflitoError, NaoEncontradoError
from app.models import Usuario
from app.repositories.repositorios import UsuarioRepositorio


class UsuarioService:
    def __init__(self, repositorio: UsuarioRepositorio):
        self._repo = repositorio

    def list(self, ordenar_por, direcao, pagina, por_pagina):
        return self._repo.list({}, ordenar_por, direcao, pagina, por_pagina)

    def get(self, id_: int) -> Usuario:
        usuario = self._repo.get(id_)
        if usuario is None:
            raise NaoEncontradoError(f"Usuário {id_} não encontrado.")
        return usuario

    def criar(self, dados: dict) -> Usuario:
        self._garantir_email_livre(dados["email"])
        return self._repo.criar(dados)

    def atualizar(self, id_: int, dados: dict) -> Usuario:
        usuario = self.get(id_)
        self._garantir_email_livre(dados["email"], ignorar_id=id_)
        return self._repo.atualizar(usuario, dados)

    def remover(self, id_: int) -> None:
        self._repo.remover(self.get(id_))

    def _garantir_email_livre(self, email: str, ignorar_id: int | None = None) -> None:
        """E-mail é único; a checagem antecipada dá uma mensagem clara (o banco também garante)."""
        existente = self._repo.buscar_por_email(email)
        if existente is not None and existente.id != ignorar_id:
            raise ConflitoError("Já existe um usuário com este e-mail.")
