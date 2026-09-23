"""Endpoint de healthcheck: verifica a aplicação e a conexão com o banco."""
from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db

healthcheck_bp = Blueprint("healthcheck", __name__, url_prefix="/api/v1")


@healthcheck_bp.get("/healthcheck")
def healthcheck():
    """Verifica se a API e o banco de dados estão funcionando.
    ---
    tags: [Healthcheck]
    responses:
      200:
        description: Serviço saudável
        schema:
          type: object
          properties:
            status: {type: string, example: ok}
            banco: {type: string, example: ok}
      503:
        description: Banco de dados indisponível
    """
    try:
        db.session.execute(text("SELECT 1"))  # consulta fixa, sem entrada do usuário
        return jsonify({"status": "ok", "banco": "ok"})
    except Exception:  # noqa: BLE001 - qualquer falha de banco significa "não saudável"
        return jsonify({"status": "erro", "banco": "indisponivel"}), 503
