"""Ponto único de montagem das dependências (composition root).

É o único lugar que conhece as classes concretas: as demais camadas recebem
abstrações por injeção no construtor (Inversão de Dependência).
"""
from dataclasses import dataclass

from app.clients.fonte_externa import FonteCafeExterna
from app.clients.sample_coffee_client import SampleCoffeeClient
from app.repositories.repositorios import (
    AdminRepositorio,
    CafeRepositorio,
    ComentarioRepositorio,
    UsuarioRepositorio,
)
from app.services.auth_service import AuthService
from app.services.cafe_service import CafeService
from app.services.comentario_service import ComentarioService
from app.services.usuario_service import UsuarioService


@dataclass
class Container:
    admin_repositorio: AdminRepositorio
    auth_service: AuthService
    cafe_service: CafeService
    usuario_service: UsuarioService
    comentario_service: ComentarioService


def montar_container(config, fonte_externa: FonteCafeExterna | None = None) -> Container:
    """Cria repositórios, cliente externo e services já conectados entre si."""
    cafes = CafeRepositorio()
    usuarios = UsuarioRepositorio()
    comentarios = ComentarioRepositorio()
    admins = AdminRepositorio()

    fonte = fonte_externa or SampleCoffeeClient(
        base_url=config["SAMPLECOFFEE_URL"],
        timeout=config["SAMPLECOFFEE_TIMEOUT"],
        tentativas=config["SAMPLECOFFEE_RETRIES"],
    )

    return Container(
        admin_repositorio=admins,
        auth_service=AuthService(admins),
        cafe_service=CafeService(cafes, fonte),
        usuario_service=UsuarioService(usuarios),
        comentario_service=ComentarioService(comentarios, usuarios, cafes),
    )
