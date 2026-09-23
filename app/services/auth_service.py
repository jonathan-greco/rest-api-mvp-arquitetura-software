"""Autenticação do Admin: login, geração de token e criação do usuário admin"""
import logging
import re

from flask import current_app
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash, generate_password_hash

from app.errors.exceptions import NaoAutenticadoError, ValidacaoError
from app.models import Admin
from app.models.usuario import agora_utc
from app.repositories.repositorios import AdminRepositorio

logger = logging.getLogger(__name__)

# Hash fictício usado quando o e-mail não existe, para o tempo de resposta não revelar contas.
_HASH_FICTICIO = generate_password_hash("senha-ficticia-para-tempo-constante")


def validar_senha(senha: str) -> None:
    """Exige mínimo de 8 caracteres, com ao menos uma letra e um número."""
    if len(senha) < 8 or not re.search(r"[A-Za-z]", senha) or not re.search(r"\d", senha):
        raise ValidacaoError(
            "A senha do admin deve ter no mínimo 8 caracteres, com letras e números."
        )


class AuthService:
    def __init__(self, admin_repositorio: AdminRepositorio):
        self._repo = admin_repositorio

    def autenticar(self, email: str, senha: str) -> tuple[str, Admin]:
        """Valida as credenciais. Falhas geram sempre a mesma mensagem."""
        admin = self._repo.buscar_por_email(email)
        # Sempre compara um hash para manter o tempo de resposta constante.
        hash_comparado = admin.senha_hash if admin else _HASH_FICTICIO
        senha_confere = check_password_hash(hash_comparado, senha)

        if admin is None or not senha_confere or not admin.ativo:
            raise NaoAutenticadoError("Credenciais inválidas.")

        self._repo.atualizar(admin, {"ultimo_login": agora_utc()})
        token = create_access_token(identity=str(admin.id), additional_claims={"perfil": "admin"})
        return token, admin

    def garantir_admin_inicial(self, nome: str, email: str | None, senha: str | None) -> None:
        """Cria o admin inicial se ainda não existir.

        Em desenvolvimento, sem ADMIN_EMAIL/ADMIN_SENHA, nenhum admin é criado
        """
        if not email or not senha:
            logger.warning("ADMIN_EMAIL/ADMIN_SENHA não informados: nenhum admin foi criado.")
            return
        email = email.strip().lower()
        if self._repo.buscar_por_email(email) is not None:
            return
        validar_senha(senha)
        self._repo.criar({
            "nome": nome,
            "email": email,
            "senha_hash": generate_password_hash(senha),
            "ativo": True,
        })
        logger.info("Admin inicial criado: %s", email)
