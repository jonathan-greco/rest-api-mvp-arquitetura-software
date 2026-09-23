"""Decorator que protege rotas exclusivas do Admin."""
from functools import wraps

from flask import g
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request

from app.errors.exceptions import AcessoNegadoError
from app.routes.utils import container


def admin_required(funcao):
    """Exige token JWT válido de um Admin ativo (401 sem token, 403 sem permissão).

    Além de validar o token, consultan o banco um admin desativado ou removido perde
    o acesso imediatamente, mesmo com token ainda não expirado.
    """

    @wraps(funcao)
    def envolver(*args, **kwargs):
        verify_jwt_in_request()  # lança erros tratados em errors/handlers.py (401)
        if get_jwt().get("perfil") != "admin":
            raise AcessoNegadoError("Acesso restrito para administradores.")
        admin = container().admin_repositorio.get(int(get_jwt_identity()))
        if admin is None or not admin.ativo:
            raise AcessoNegadoError("Administrador não encontrado.")
        g.admin = admin  # disponível para a rota
        return funcao(*args, **kwargs)

    return envolver
