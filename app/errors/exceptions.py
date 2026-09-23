"""Exceções de domínio.

As camadas de serviço lançam estas exceções (sem conhecer HTTP); o handler global
em `handlers.py` as converte em respostas JSON padronizadas.
"""


class ErroAplicacao(Exception):
    """Erro base da aplicação, com código HTTP e código de erro estável."""

    status_code = 500
    codigo = "erro_interno"

    def __init__(self, mensagem: str, detalhes: dict | None = None):
        super().__init__(mensagem)
        self.mensagem = mensagem
        self.detalhes = detalhes


class ValidacaoError(ErroAplicacao):
    """Dados de entrada inválidos (400/422)."""

    status_code = 422
    codigo = "validacao"


class RequisicaoInvalidaError(ErroAplicacao):
    """Requisição malformada, por exemplo corpo que não é JSON (400)."""

    status_code = 400
    codigo = "requisicao_invalida"


class NaoAutenticadoError(ErroAplicacao):
    """Credenciais ausentes ou inválidas (401)."""

    status_code = 401
    codigo = "nao_autenticado"


class AcessoNegadoError(ErroAplicacao):
    """Usuário autenticado sem permissão para o recurso (403)."""

    status_code = 403
    codigo = "acesso_negado"


class NaoEncontradoError(ErroAplicacao):
    """Recurso inexistente (404)."""

    status_code = 404
    codigo = "nao_encontrado"


class ConflitoError(ErroAplicacao):
    """Conflito com o estado atual, como e-mail duplicado (409)."""

    status_code = 409
    codigo = "conflito"


class FonteExternaIndisponivelError(ErroAplicacao):
    """A API externa falhou ou está fora do ar (502)."""

    status_code = 502
    codigo = "fonte_externa_indisponivel"
