"""Login do Admin e consulta dos próprios dados."""
from flask import Blueprint, current_app, g, jsonify

from app.extensions import limiter
from app.routes.decorators import admin_required
from app.routes.utils import container, get_json
from app.schemas.admin_schema import AdminSchema, LoginSchema

admin_auth_bp = Blueprint("admin_auth", __name__, url_prefix="/api/v1/admin")

_login_schema = LoginSchema()
_admin_schema = AdminSchema()


@admin_auth_bp.post("/auth/login")
# Limite mais rígido que o padrão: dificulta ataques de força bruta na senha.
@limiter.limit(lambda: current_app.config["RATELIMIT_LOGIN"])
def login():
    """Autentica o Admin e devolve um token JWT.
    ---
    tags: [Admin]
    parameters:
      - in: body
        name: body
        required: true
        schema:
          $ref: '#/definitions/Login'
    responses:
      200:
        description: Login realizado
        schema:
          $ref: '#/definitions/Token'
      401:
        description: Credenciais inválidas
        schema:
          $ref: '#/definitions/Erro'
      422:
        description: Dados inválidos
        schema:
          $ref: '#/definitions/Erro'
      429:
        description: Muitas tentativas de login
    """
    dados = _login_schema.load(get_json())
    token, _admin = container().auth_service.autenticar(dados["email"], dados["senha"])
    expira = int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds())
    return jsonify({"access_token": token, "token_type": "Bearer", "expira_em_segundos": expira})


@admin_auth_bp.get("/meu-status")
@admin_required
def meu_status():
    """Retorna os dados do Admin autenticado.
    ---
    tags: [Admin]
    security:
      - Bearer: []
    responses:
      200:
        description: Dados do admin
        schema:
          $ref: '#/definitions/Admin'
      401:
        description: Token ausente, inválido ou expirado
        schema:
          $ref: '#/definitions/Erro'
      403:
        description: Admin inativo
        schema:
          $ref: '#/definitions/Erro'
    """
    return jsonify(_admin_schema.dump(g.admin))
