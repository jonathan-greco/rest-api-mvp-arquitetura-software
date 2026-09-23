"""Ponto único de montagem das dependências (composition root).

É o único lugar que conhece as classes concretas: as demais camadas recebem
abstrações por injeção no construtor (Inversão de Dependência).
"""
from dataclasses import dataclass

from app.clients.fonte_externa import FonteCafeExterna
from app.clients.sample_coffee_client import SampleCoffeeClient
from app.repositories.repositorios import AdminRepositorio, CafeRepositorio, ComentarioRepositorio
from app.services.auth_service import AuthService
from app.services.cafe_service import CafeService
from app.services.comentario_service import ComentarioService


@dataclass
class Container:
    admin_repositorio: AdminRepositorio
    auth_service: AuthService
    cafe_service: CafeService
    comentario_service: ComentarioService


def montar_container(config, fonte_externa: FonteCafeExterna | None = None) -> Container:
    """Cria repositórios, cliente externo e services já conectados entre si."""
    cafes = CafeRepositorio()
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
        comentario_service=ComentarioService(comentarios, admins, cafes),
    )
