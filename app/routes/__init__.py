"""Registro dos blueprints (grupos de rotas) da aplicação."""
from flask import Flask


def registrar_rotas(app: Flask) -> None:
    """Importa e registra todos os blueprints"""
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.admin_cafes import admin_cafes_bp
    from app.routes.cafes import cafes_bp
    from app.routes.comentarios import comentarios_bp
    from app.routes.healthcheck import healthcheck_bp
    from app.routes.usuarios import usuarios_bp

    for blueprint in (healthcheck_bp, cafes_bp, admin_auth_bp, admin_cafes_bp, usuarios_bp, comentarios_bp):
        app.register_blueprint(blueprint)
