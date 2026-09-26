"""Application factory da API de Cafés."""
import logging
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.config import Config
from app.container import montar_container
from app.errors.handlers import registrar_handlers
from app.extensions import db, jwt, limiter, swagger
from app.routes import registrar_rotas


@event.listens_for(Engine, "connect")
def _ativar_chaves_estrangeiras_sqlite(conexao, _registro):
    """SQLite não aplica chaves estrangeiras por padrão; ativa para valer o ON DELETE CASCADE."""
    if conexao.__class__.__module__.startswith("sqlite3"):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def create_app(sobrescrever_config: dict | None = None, fonte_externa=None) -> Flask:
    """Cria e configura a aplicação.

    :param sobrescrever_config: valores que substituem a configuração (útil em execuções controladas).
    :param fonte_externa: implementação alternativa de FonteCafeExterna (injeção de dependência).
    """
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    Config.validar()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config.update(sobrescrever_config or {})

    # Banco SQLite padrão em instance/cafes.db (pasta montada como volume no Docker).
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + (Path(app.instance_path) / "cafes.db").as_posix()

    app.url_map.strict_slashes = False
    app.json.ensure_ascii = False  # acentos legíveis nas respostas
    app.json.sort_keys = False

    # Extensões.
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    swagger.init_app(app)
    if app.config["CORS_ORIGINS"]:
        CORS(app, resources={r"/api/*": {"origins": ["http://localhost:8080", "http://localhost:5173"]}})

    registrar_handlers(app)
    registrar_rotas(app)

    @app.after_request
    def cabecalhos_de_seguranca(resposta):
        """Cabeçalhos básicos contra sniffing de conteúdo e clickjacking."""
        resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        resposta.headers.setdefault("X-Frame-Options", "DENY")
        resposta.headers.setdefault("Referrer-Policy", "no-referrer")
        return resposta

    # Injeção de dependências e preparação do banco.
    app.extensions["container"] = montar_container(app.config, fonte_externa)
    with app.app_context():
        db.create_all()
        app.extensions["container"].auth_service.garantir_admin_inicial(
            app.config["ADMIN_NOME"], app.config["ADMIN_EMAIL"], app.config["ADMIN_SENHA"]
        )
    return app
