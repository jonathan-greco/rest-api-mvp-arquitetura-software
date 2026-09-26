"""Configuração e definições compartilhadas do Swagger (Flasgger / OpenAPI 2.0).

As descrições de cada endpoint ficam nos docstrings das rotas (arquivos em app/routes).
Aqui ficam os modelos reutilizados ($ref) e a segurança por Bearer token.
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

_ERRO = {"$ref": "#/definitions/Erro"}

SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "API Café Explorer",
        "author": "Jonathan Greco Leite",
        "description": (
            "MVP de API REST (Flask + SQLAlchemy + SQLite) com CRUD de Café e Comentário, "
            "gerenciados na própria coleção de cada um (escrita exige login de Admin). O GET "
            "público de cafés combina o banco local com a API externa SampleAPIs Coffee "
            "(https://api.sampleapis.com/coffee).\n\n"
            "**Login:** faça `POST /api/v1/admin/auth/login`, copie o token e clique em "
            "*Authorize* informando `Bearer <token>`.\n\n"
            "**Desenvolvedor:** `Jonathan Greco Leite`."
        ),
        "version": "1.0.0",
    },
    "basePath": "/",
    "schemes": ["http", "https"],
    "consumes": ["application/json"],
    "produces": ["application/json"],
    "tags": [
        {"name": "Cafés", "description": "Consulta pública (GET); escrita (POST/PUT/DELETE) requer login de Admin"},
        {"name": "Admin", "description": "Login e dados do Admin autenticado"},
        {"name": "Comentários", "description": "Comentários do Admin sobre cafés (criação exige login)"},
        {"name": "Healthcheck", "description": "Verificação do serviço"},
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Token JWT do admin. Formato: `Bearer <token>`.",
        }
    },
    "definitions": {
        "Erro": {
            "type": "object",
            "properties": {
                "erro": {
                    "type": "object",
                    "properties": {
                        "codigo": {"type": "string", "example": "validacao"},
                        "mensagem": {"type": "string", "example": "Dados de entrada inválidos."},
                        "detalhes": {"type": "object", "example": {"nome": ["Length must be between 2 and 120."]}},
                    },
                }
            },
        },
        "CafeEntrada": {
            "type": "object",
            "required": ["nome"],
            "properties": {
                "nome": {"type": "string", "example": "Latte"},
                "descricao": {
                    "type": "string",
                    "example": "Bebida popular feita com espresso e leite vaporizado.",
                },
                "ingredientes": {
                    "type": "array",
                    "items": {"type": "string"},
                    "example": ["Espresso", "Leite vaporizado"],
                },
                "imagem_url": {"type": "string", "example": "https://exemplo.com/latte.jpg"},
            },
        },
        "Cafe": {
            "type": "object",
            "properties": {
                "id": {"type": "integer", "description": "Id local (null em itens externos)", "example": 1},
                "id_externo": {"type": "integer", "description": "Id na SampleAPIs Coffee (null em itens locais)"},
                "origem": {"type": "string", "enum": ["local", "externa"]},
                "nome": {"type": "string"},
                "descricao": {"type": "string"},
                "ingredientes": {"type": "array", "items": {"type": "string"}},
                "imagem_url": {"type": "string"},
            },
        },
        "ListaCafes": {
            "type": "object",
            "properties": {
                "itens": {"type": "array", "items": {"$ref": "#/definitions/Cafe"}},
                "total": {"type": "integer"},
                "pagina": {"type": "integer"},
                "por_pagina": {"type": "integer"},
                "fonte_externa": {
                    "type": "string",
                    "enum": ["disponivel", "indisponivel", "desativada"],
                    "description": "Estado da consulta à SampleAPIs Coffee",
                },
            },
        },
        "ComentarioEntrada": {
            "type": "object",
            "required": ["cafe_id", "texto", "nota"],
            "properties": {
                "cafe_id": {"type": "integer", "description": "Id de um café do banco local", "example": 1},
                "texto": {"type": "string", "example": "Excelente aroma e sabor equilibrado."},
                "nota": {"type": "integer", "minimum": 1, "maximum": 5, "example": 5},
            },
        },
        "ComentarioAtualizacao": {
            "type": "object",
            "required": ["texto", "nota"],
            "properties": {
                "texto": {"type": "string", "example": "Mudei de ideia: ótimo custo-benefício."},
                "nota": {"type": "integer", "minimum": 1, "maximum": 5, "example": 4},
            },
        },
        "Comentario": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "admin_id": {"type": "integer", "description": "Id do Admin autor (preenchido a partir do token)"},
                "cafe_id": {"type": "integer"},
                "texto": {"type": "string"},
                "nota": {"type": "integer"},
                "criado_em": {"type": "string", "format": "date-time"},
            },
        },
        "ListaComentarios": {
            "type": "object",
            "properties": {
                "itens": {"type": "array", "items": {"$ref": "#/definitions/Comentario"}},
                "total": {"type": "integer"},
                "pagina": {"type": "integer"},
                "por_pagina": {"type": "integer"},
            },
        },
        "Login": {
            "type": "object",
            "required": ["email", "senha"],
            "properties": {
                "email": {"type": "string", "example": "admin@exemplo.com"},
                "senha": {"type": "string", "example": "SenhaForte123"},
            },
        },
        "Token": {
            "type": "object",
            "properties": {
                "access_token": {"type": "string"},
                "token_type": {"type": "string", "example": "Bearer"},
                "expira_em_segundos": {"type": "integer", "example": 1800},
            },
        },
        "Admin": {
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "nome": {"type": "string"},
                "email": {"type": "string"},
                "ativo": {"type": "boolean"},
                "criado_em": {"type": "string", "format": "date-time"},
                "ultimo_login": {"type": "string", "format": "date-time"},
            },
        },
    },
}
