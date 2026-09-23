"""Configuração da aplicação, lida de variáveis de ambiente.

Nenhum segredo fica escrito no código: a chave JWT e as credenciais do
administrador inicial vêm sempre do ambiente (ou do arquivo .env em desenvolvimento).
"""
import os
import secrets
from datetime import timedelta

from dotenv import load_dotenv

# Carrega o arquivo .env (se existir) para as variáveis de ambiente.
load_dotenv()


def _read_int(nome: str, padrao: int) -> int:
    """Lê uma variável de ambiente inteira, usando o padrão se ausente ou inválida."""
    try:
        return int(os.getenv(nome, padrao))
    except (TypeError, ValueError):
        return padrao


class Config:
    """Configuração base, com valores padrão seguros."""

    # "production" exige que os segredos sejam informados explicitamente.
    APP_ENV = os.getenv("APP_ENV", "development").lower()
    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    # Banco: se DATABASE_URL não for informada, a fábrica usa instance/cafes.db.
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Limita o tamanho do corpo da requisição (proteção contra payload abusivo).
    MAX_CONTENT_LENGTH = _read_int("MAX_CONTENT_LENGTH", 1024 * 1024)  # 1 MB

    # Autenticação do Admin (JWT).
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=_read_int("JWT_EXPIRA_MINUTOS", 30))

    # Administrador inicial criado automaticamente.
    ADMIN_NOME = os.getenv("ADMIN_NOME", "Administrador")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_SENHA = os.getenv("ADMIN_SENHA")

    # API externa SampleAPIs Coffee
    # A fonte expõe /hot e /iced
    # Este projeto não diferencia os dois (busca sempre os dois).
    SAMPLECOFFEE_URL = os.getenv("SAMPLECOFFEE_URL", "https://api.sampleapis.com/coffee")
    SAMPLECOFFEE_TIMEOUT = _read_int("SAMPLECOFFEE_TIMEOUT", 5)  # segundos
    SAMPLECOFFEE_RETRIES = _read_int("SAMPLECOFFEE_RETRIES", 1)

    # Rate limiting (Flask-Limiter).
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per minute")
    RATELIMIT_LOGIN = os.getenv("RATELIMIT_LOGIN", "5 per minute")
    RATELIMIT_STORAGE_URI = os.getenv("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_HEADERS_ENABLED = True

    # CORS: lista de origens permitidas separadas por vírgula. Vazio = CORS desligado.
    CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

    @classmethod
    def validar(cls) -> None:
        """Valida a configuração; em produção, segredos obrigatórios ausentes impedem o start."""
        if cls.APP_ENV == "production":
            ausentes = [
                nome
                for nome in ("JWT_SECRET_KEY", "ADMIN_EMAIL", "ADMIN_SENHA")
                if not getattr(cls, nome)
            ]
            if ausentes:
                raise RuntimeError(
                    "Variáveis de ambiente obrigatórias em produção: " + ", ".join(ausentes)
                )
        if not cls.JWT_SECRET_KEY:
            # Desenvolvimento: chave aleatória por processo (tokens expiram ao reiniciar).
            cls.JWT_SECRET_KEY = secrets.token_hex(32)
