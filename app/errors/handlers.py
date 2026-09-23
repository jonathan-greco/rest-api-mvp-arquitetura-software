"""Handlers globais de erro: toda falha vira JSON padronizado, sem stack trace."""
import logging

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors.exceptions import ErroAplicacao
from app.extensions import jwt

logger = logging.getLogger(__name__)


def _resposta_erro(status: int, codigo: str, mensagem: str, detalhes: dict | None = None):
    """Monta o corpo de erro padrão: {"erro": {"codigo", "mensagem", "detalhes"}}."""
    corpo = {"erro": {"codigo": codigo, "mensagem": mensagem}}
    if detalhes:
        corpo["erro"]["detalhes"] = detalhes
    return jsonify(corpo), status


def registrar_handlers(app: Flask) -> None:
    """Registra os handlers de erro na aplicação."""

    @app.errorhandler(ErroAplicacao)
    def tratar_erro_aplicacao(erro: ErroAplicacao):
        return _resposta_erro(erro.status_code, erro.codigo, erro.mensagem, erro.detalhes)

    @app.errorhandler(ValidationError)
    def tratar_erro_validacao(erro: ValidationError):
        # Erros de schema Marshmallow
        return _resposta_erro(422, "validacao", "Dados de entrada inválidos.", erro.messages)

    @app.errorhandler(HTTPException)
    def tratar_erro_http(erro: HTTPException):
        # 404, 405, 413, 415, 429 etc. gerados pelo Flask.
        return _resposta_erro(erro.code or 500, "http_" + str(erro.code), erro.description)

    @app.errorhandler(Exception)
    def tratar_erro_inesperado(erro: Exception):
        # Detalhes vão para o log
        logger.exception("Erro inesperado: %s", erro)
        return _resposta_erro(500, "erro_interno", "Erro interno do servidor.")

    # Erros de JWT
    @jwt.unauthorized_loader
    def token_ausente(_motivo: str):
        return _resposta_erro(401, "nao_autenticado", "Token de acesso ausente.")

    @jwt.invalid_token_loader
    def token_invalido(_motivo: str):
        return _resposta_erro(401, "nao_autenticado", "Token de acesso inválido.")

    @jwt.expired_token_loader
    def token_expirado(_cabecalho: dict, _dados: dict):
        return _resposta_erro(401, "nao_autenticado", "Token de acesso expirado.")
