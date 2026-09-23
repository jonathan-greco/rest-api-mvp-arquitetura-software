"""Instâncias das extensões Flask, criadas sem app e ligadas na application factory."""
from flasgger import Swagger
from flask import request
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

from app.swagger_docs import SWAGGER_CONFIG, SWAGGER_TEMPLATE

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
swagger = Swagger(config=SWAGGER_CONFIG, template=SWAGGER_TEMPLATE)


@limiter.request_filter
def _isentar_documentacao() -> bool:
    """A Swagger UI faz muitas requisições de arquivos estáticos: não entram no rate limit."""
    return request.path.startswith(("/swagger", "/apidocs", "/apispec", "/flasgger_static"))
