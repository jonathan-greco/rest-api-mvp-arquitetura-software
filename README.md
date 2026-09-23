# API de Cafés — MVP de Arquitetura de Software Backend

API REST em **Python + Flask** com persistência em **SQLite (SQLAlchemy)**, documentação **Swagger (Flasgger)** e integração com um serviço externo, a **SampleAPIs Coffee** (<https://api.sampleapis.com/api-list/coffee>). O projeto foi organizado em camadas seguindo os princípios **SOLID** e possui validação de entrada e proteção contra SQL injection.

## Sumário

1. [Visão geral](#1-visão-geral)
2. [Tecnologias](#2-tecnologias)
3. [Arquitetura e SOLID](#3-arquitetura-e-solid)
4. [Modelo de dados](#4-modelo-de-dados)
5. [Endpoints](#5-endpoints)
6. [Integração com a SampleAPIs Coffee](#6-integração-com-a-sampleapis-coffee)
7. [Segurança](#7-segurança)
8. [Como executar](#8-como-executar)
9. [Estrutura de pastas](#9-estrutura-de-pastas)

---

## 1. Visão geral

A API gerencia quatro entidades: **Usuario**, **Cafe**, **Comentario** e **Admin**.

- O **público** consulta cafés (`GET`). A consulta combina o banco local (SQLite) com a SampleAPIs Coffee: os itens externos que não existem no banco local são **concatenados** ao resultado.
- O **Admin** (autenticado por token JWT) cria, consulta, altera e remove cafés (`POST`, `GET`, `PUT`, `DELETE`).
- **Usuários** fazem um cadastro simples (nome e e-mail) e escrevem **comentários** (com nota de 1 a 5) sobre os cafés do banco local.
- Os itens da SampleAPIs Coffee são **apenas exibidos** nas consultas: nunca são gravados no SQLite.

## 2. Tecnologias

| Item | Uso |
| --- | --- |
| Python 3.12 | Linguagem |
| Flask | Framework web (application factory + blueprints) |
| Flask-SQLAlchemy / SQLAlchemy | ORM e acesso ao SQLite |
| Marshmallow | Validação e serialização de dados |
| Flasgger | Swagger UI e especificação OpenAPI |
| requests (+ urllib3 Retry) | Cliente HTTP da SampleAPIs Coffee |
| Flask-JWT-Extended | Autenticação do Admin por JWT |
| Flask-Limiter | Rate limiting |
| Flask-CORS | CORS configurável |
| bleach | Sanitização de HTML em textos |
| Gunicorn | Servidor de produção (Docker) |

## 3. Arquitetura e SOLID

```mermaid
flowchart TD
    A[Routes / Blueprints<br/>HTTP + docstrings Swagger] --> B[Services<br/>regras de negócio]
    B --> C[Repositories<br/>acesso a dados]
    B --> D[FonteCafeExterna<br/>SampleCoffeeClient + CafeMapper]
    C --> E[(SQLite via SQLAlchemy)]
    A -.valida entrada.-> F[Schemas<br/>Marshmallow]
    D --> G[[API SampleAPIs Coffee]]
```

Cada camada só conhece a de baixo, por meio de abstrações:

| Princípio | Como foi aplicado |
| --- | --- |
| **S** — Responsabilidade única | Route só trata HTTP; Service só aplica regras; Repository só acessa o banco; Client só fala com a API externa; Schema só valida; Mapper só converte campos; `AuthService` só cuida de autenticação. |
| **O** — Aberto/fechado | Novas fontes externas entram como novas implementações de `FonteCafeExterna`, sem alterar o `CafeService`. Novos filtros/colunas se declaram nas subclasses de repositório. |
| **L** — Substituição de Liskov | Qualquer implementação de `RepositorioBase` pode substituir a do SQLAlchemy sem quebrar os services. |
| **I** — Segregação de interfaces | Interfaces pequenas: `RepositorioBase` (CRUD) e `FonteCafeExterna` (apenas leitura: `list` e `get`). |
| **D** — Inversão de dependência | Os services recebem repositórios e fonte externa no construtor. A montagem acontece em um único lugar, `app/container.py`. |

Outras decisões: *application factory* (`create_app`), configuração por variáveis de ambiente, exceções de domínio (`NaoEncontradoError`, `ConflitoError`, ...) convertidas em JSON padronizado por um handler global.

## 4. Modelo de dados

```mermaid
erDiagram
    USUARIO ||--o{ COMENTARIO : escreve
    CAFE ||--o{ COMENTARIO : recebe
    ADMIN {
        int id PK
        string nome
        string email UK
        string senha_hash
        bool ativo
        datetime criado_em
        datetime ultimo_login
    }
    USUARIO {
        int id PK
        string nome
        string email UK
        datetime criado_em
    }
    CAFE {
        int id PK
        string nome
        string descricao
        string ingredientes
        string imagem_url
    }
    COMENTARIO {
        int id PK
        int usuario_id FK
        int cafe_id FK
        string texto
        int nota
        datetime criado_em
    }
```

**Cafe** (campos em português; `id` autoincremento) — alinhado ao formato da SampleAPIs Coffee:

| Campo | Tipo | Regra |
| --- | --- | --- |
| nome | texto (2–120) | obrigatório |
| descricao | texto (até 2000) | opcional |
| ingredientes | lista de textos (até 20 itens, 120 caracteres cada); guardada no banco como texto separado por vírgula | opcional |
| imagem_url | URL http/https (até 500) | opcional |

> A tabela `cafe` mudou de estrutura (não tem mais `preco`, `regiao`, `peso`, `perfil_sabor`, `opcao_moagem` nem `nivel_torra`), porque a nova fonte externa não fornece esses dados. Veja a [seção 11](#11-decisões-de-projeto-e-limitações).

**Usuario:** `nome` e `e-mail` (único). **Comentario:** `usuario_id`, `cafe_id` (café do banco local), `texto` (1–1000) e `nota` (1–5). **Admin:** `nome`, `email` (único), `senha_hash`, `ativo`, `criado_em`, `ultimo_login`.

Ao excluir um usuário ou um café, os comentários relacionados são removidos em cascata.

## 5. Endpoints

A documentação interativa fica em **`/apidocs/`** (Swagger UI). Para rotas de Admin, use o botão **Authorize** e informe `Bearer <token>`.

| Recurso | Método e rota | Acesso | Descrição |
| --- | --- | --- | --- |
| Café | `GET /api/v1/cafes` | Público | Lista cafés: banco local + SampleAPIs Coffee |
| Café | `GET /api/v1/cafes/{id}` | Público | Busca um café (local; se não achar, SampleAPIs Coffee) |
| Admin | `POST /api/v1/admin/auth/login` | Público | Login, devolve o token JWT |
| Admin | `GET /api/v1/admin/me` | Admin | Dados do admin autenticado |
| Café | `POST /api/v1/admin/cafes` | Admin | Cria café |
| Café | `GET /api/v1/admin/cafes` e `/{id}` | Admin | Lista/busca cafés do banco local |
| Café | `PUT /api/v1/admin/cafes/{id}` | Admin | Substitui os dados do café |
| Café | `DELETE /api/v1/admin/cafes/{id}` | Admin | Remove o café (e seus comentários) |
| Usuário | `POST/GET /api/v1/usuarios`, `GET/PUT/DELETE /api/v1/usuarios/{id}` | Público | CRUD de usuários |
| Comentário | `POST/GET /api/v1/comentarios`, `GET/PUT/DELETE /api/v1/comentarios/{id}` | Público | CRUD de comentários (filtros `cafe_id`, `usuario_id`) |
| Healthcheck | `GET /api/v1/healthcheck` | Público | Verifica API e banco |

Regras gerais:

- **Listagens** aceitam `pagina`, `por_pagina` (máx. 100), `ordenar_por` (`id` ou `nome`) e `direcao` (`asc`/`desc`), e respondem `{"itens": [...], "total": N, "pagina": 1, "por_pagina": 20}`.
- **Códigos HTTP:** 200, 201, 204, 400 (corpo inválido), 401 (sem token/credenciais), 403 (sem permissão), 404, 409 (conflito, como e-mail duplicado), 413, 422 (validação) e 502 (SampleAPIs Coffee indisponível quando a consulta externa é indispensável).
- **Erros** seguem sempre o formato `{"erro": {"codigo": "...", "mensagem": "...", "detalhes": {...}}}`.
- **PUT** substitui o recurso: campos opcionais omitidos voltam a ficar vazios. No comentário, só `texto` e `nota` podem ser alterados.

## 6. Integração com a SampleAPIs Coffee

A fonte externa (<https://api.sampleapis.com/api-list/coffee>) expõe dois endpoints, **sem endpoint por id**:

- `GET https://api.sampleapis.com/coffee/hot` — cafés quentes
- `GET https://api.sampleapis.com/coffee/iced` — cafés gelados

Cada item vem no formato:

```json
{
  "title": "Latte",
  "description": "...",
  "ingredients": ["Espresso", "Steamed milk"],
  "image": "https://...",
  "id": 2
}
```

Este projeto **não diferencia** quente/gelado: toda consulta busca os dois endpoints e junta o resultado, conforme definido no escopo.

### Regra do `GET /api/v1/cafes`

1. Busca os cafés no SQLite (aplicando filtros e ordenação).
2. Consulta a SampleAPIs Coffee — `hot` e `iced` (timeout de 5 s e 1 nova tentativa cada).
3. Converte os itens externos com o **Mapper** e acrescenta apenas os que **não existem** no banco local. A comparação é pelo **nome normalizado** (minúsculas, sem acentos e sem espaços extras), porque os ids das duas bases não coincidem.
4. Cada item traz `origem` (`local` ou `externa`). Em conflito, o **dado local prevalece**. Itens externos vêm com `id: null` e o id da fonte em `id_externo`.
5. O campo `fonte_externa` informa o estado da consulta: `disponivel`, `indisponivel` (a API caiu: a resposta traz só dados locais, sem erro 500) ou `desativada` (`?incluir_externos=false`).

### Detalhe por id

`GET /api/v1/cafes/{id}` usa `origem=auto` por padrão: procura no banco local e, se não achar, consulta a SampleAPIs Coffee. Como os ids locais e externos são independentes, use `?origem=externa` com o `id_externo` para buscar diretamente um item da fonte, ou `?origem=local` para restringir ao banco.

> **Limitação conhecida:** como a fonte não expõe um endpoint por id nem diferencia hot/iced neste projeto, o mesmo id pode existir nos dois grupos (por exemplo, `id=2` em "hot" e `id=2` em "iced" são cafés diferentes). Nesse caso, `origem=externa` devolve o **primeiro encontrado** (a lista "hot" é buscada antes da "iced").

### Mapper: equivalência de campos

O `CafeMapper` (`app/clients/cafe_mapper.py`) concentra a correspondência entre os nossos campos (português) e os da SampleAPIs Coffee (inglês) no dicionário `EQUIVALENCIA_CAMPOS`:

| Campo local | Campo da SampleAPIs Coffee |
| --- | --- |
| nome | title |
| descricao | description |
| ingredientes | ingredients |
| imagem_url | image |

Se a fonte externa mudar um nome de campo, basta alterar o dicionário. A SampleAPIs Coffee só é acessada por leitura (`GET`); a escrita acontece apenas no nosso banco.

## 7. Segurança

| Ameaça | Proteção |
| --- | --- |
| **SQL injection** | Somente ORM/expressões do SQLAlchemy, com parâmetros vinculados; nenhuma SQL é montada por concatenação. Colunas de ordenação e filtro vêm de listas permitidas (whitelist) e curingas `%`/`_` viram texto literal. |
| Dados malformados | Schemas Marshmallow validam tipo (estrito), tamanho e formato; campos desconhecidos são recusados (evita *mass assignment*); ingredientes limitados em quantidade e tamanho. |
| XSS armazenado | Textos livres (nome, descrição, ingredientes) passam por `bleach` (tags HTML removidas) e caracteres de controle são descartados. Como `<`, `>` e `&` ficam escapados, clientes web devem exibir os textos como texto, não como HTML. |
| Payload abusivo | `MAX_CONTENT_LENGTH` (1 MB), corpo obrigatoriamente objeto JSON, URL de imagem restrita a http/https. |
| Força bruta | Rate limit padrão (100/min por IP) e mais rígido no login (5/min). |
| Enumeração de contas | Login responde sempre "Credenciais inválidas" e compara um hash mesmo quando o e-mail não existe (tempo constante). |
| Senhas e tokens | Senha só como hash (`werkzeug.security`); JWT com expiração (30 min) e segredo vindo do ambiente; admin desativado perde acesso mesmo com token válido. |
| Vazamento de informação | Handler global sem stack trace; detalhes só nos logs. |
| SSRF | URL da SampleAPIs Coffee fixa em configuração; o id repassado à API externa é convertido para inteiro. |
| Cabeçalhos e CORS | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`; CORS desligado por padrão e configurável por origem. |
| Container | Imagem slim, usuário sem privilégios e Gunicorn. |

## 8. Como executar

### Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste.

| Variável | Descrição | Padrão |
| --- | --- | --- |
| `APP_ENV` | `development` ou `production` (exige os três segredos abaixo) | `development` |
| `JWT_SECRET_KEY` | Segredo dos tokens JWT | aleatório por processo em desenvolvimento |
| `ADMIN_EMAIL` / `ADMIN_SENHA` | Admin criado automaticamente (seed). Senha com 8+ caracteres, letras e números | nenhum admin é criado se ausentes |
| `ADMIN_NOME` | Nome do admin do seed | `Administrador` |
| `DATABASE_URL` | URL do banco | `sqlite` em `instance/cafes.db` |
| `SAMPLECOFFEE_URL`, `SAMPLECOFFEE_TIMEOUT`, `SAMPLECOFFEE_RETRIES` | Integração externa (base; `/hot` e `/iced` são anexados automaticamente) | `https://api.sampleapis.com/coffee`, 5 s, 1 |
| `JWT_EXPIRA_MINUTOS` | Validade do token | 30 |
| `RATELIMIT_DEFAULT`, `RATELIMIT_LOGIN` | Limites de requisições | `100 per minute`, `5 per minute` |
| `CORS_ORIGINS` | Origens permitidas, separadas por vírgula | vazio (desligado) |

> **Se você já tem um `instance/cafes.db` de uma versão anterior**, apague-o antes de subir a API: a tabela `cafe` mudou de colunas e o projeto não usa migrações (cria as tabelas do zero com `db.create_all()`).

### Localmente

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python run.py
```

A API sobe em <http://127.0.0.1:5000> e o Swagger em <http://127.0.0.1:5000/apidocs/>. As tabelas e o admin inicial são criados automaticamente.

### Com Docker

```bash
docker build -t cafe-api .

docker run -d --name cafe-api -p 5000:5000 \
  -e JWT_SECRET_KEY="trocar por uma chave secreta" \
  -e ADMIN_EMAIL="admin@teste.com.br" \
  -e ADMIN_SENHA="SenhaForte123" \
  -v cafe-data:/app/instance \
  cafe-api
```

Ou, com um arquivo `.env`: `docker run -d -p 5000:5000 --env-file .env -v cafe-data:/app/instance cafe-api`.

O volume `cafe-data` guarda o arquivo SQLite, então os dados sobrevivem à remoção do container. Em `APP_ENV=production` (padrão da imagem) a aplicação não inicia sem `JWT_SECRET_KEY`, `ADMIN_EMAIL` e `ADMIN_SENHA`. Logs: `docker logs cafe-api`.

## 9. Estrutura de pastas

```text
rest-api-mvp-arquitetura-software/
├── app/
│   ├── __init__.py            # application factory (create_app)
│   ├── config.py              # configuração por variáveis de ambiente
│   ├── container.py           # montagem das dependências (injeção)
│   ├── extensions.py          # db, jwt, limiter, swagger
│   ├── swagger_docs.py        # definições compartilhadas do Swagger
│   ├── models/                # Usuario, Cafe, Comentario, Admin (SQLAlchemy)
│   ├── schemas/                # validação e serialização (Marshmallow)
│   ├── repositories/           # RepositorioBase + implementação SQLAlchemy
│   ├── services/               # regras de negócio
│   ├── clients/                # FonteCafeExterna, SampleCoffeeClient e CafeMapper
│   ├── routes/                 # blueprints com docstrings Swagger
│   ├── errors/                 # exceções de domínio e handlers
│   └── utils/                  # utilitários (normalização de texto)
├── instance/                  # banco SQLite (volume no Docker)
├── run.py                     # ponto de entrada
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .env.example
└── README.md
```
