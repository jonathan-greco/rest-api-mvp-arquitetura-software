"""Cliente HTTP da API externa SampleAPIs Coffee (https://api.sampleapis.com/coffee).

A fonte expõe dois endpoints de LISTA, sem endpoint por id:
- GET /coffee/hot   (cafés quentes)
- GET /coffee/iced  (cafés gelados)

Este projeto não diferencia quente/gelado: `list()` busca os dois e devolve tudo junto.
Como não existe um endpoint por id, `get()` também busca as duas listas e procura o item
nelas (não há garantia de id único entre hot e iced: em caso de colisão, o primeiro
encontrado — sempre "hot" primeiro — é o devolvido).

Usa timeout e novas tentativas limitadas: se a API externa estiver lenta ou fora do ar,
a nossa API não trava e o service decide como degradar (responder só com dados locais).
"""
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from app.clients.cafe_mapper import CafeMapper
from app.clients.fonte_externa import FonteCafeExterna
from app.errors.exceptions import FonteExternaIndisponivelError

logger = logging.getLogger(__name__)

# A fonte não diferencia consulta por tipo neste projeto; os dois tipos disponíveis na API.
TIPOS_BEBIDA = ("hot", "iced")


class SampleCoffeeClient(FonteCafeExterna):
    """Implementação de FonteCafeExterna para a SampleAPIs Coffee (somente GET)."""

    def __init__(self, base_url: str, timeout: int = 5, tentativas: int = 1):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        # Sessão reutiliza conexões; Retry refaz a chamada em falhas transitórias.
        self._sessao = requests.Session()
        retry = Retry(
            total=tentativas,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504),
            allowed_methods=("GET",),
        )
        self._sessao.mount("https://", HTTPAdapter(max_retries=retry))
        self._sessao.mount("http://", HTTPAdapter(max_retries=retry))

    def _get_tipo(self, tipo: str) -> list:
        """Busca a lista de um tipo (hot/iced); falha vira FonteExternaIndisponivelError."""
        url = f"{self._base_url}/{tipo}"
        try:
            resposta = self._sessao.get(url, timeout=self._timeout, headers={"Accept": "application/json"})
            resposta.raise_for_status()
            payload = resposta.json()
            return payload if isinstance(payload, list) else []
        except (requests.RequestException, ValueError) as erro:
            # ValueError cobre JSON inválido. O detalhe técnico vai só para o log.
            logger.warning("Falha ao consultar a SampleAPIs Coffee (%s): %s", url, erro)
            raise FonteExternaIndisponivelError("API externa SampleAPIs Coffee indisponível.") from erro

    def _listar_bruto(self) -> list[dict]:
        """Concatena hot + iced; falha em qualquer um dos dois marca a fonte como indisponível."""
        itens = []
        for tipo in TIPOS_BEBIDA:
            itens.extend(self._get_tipo(tipo))
        return itens

    def list(self) -> list[dict]:
        cafes = []
        for item in self._listar_bruto():
            try:
                cafes.append(CafeMapper.para_local(item))
            except ValueError:
                logger.warning("Item externo ignorado por formato inesperado: %r", item)
        return cafes

    def get(self, id_externo: int) -> dict | None:
        # Não há endpoint por id na fonte: busca nas duas listas e procura o item.
        for item in self._listar_bruto():
            if item.get("id") == id_externo:
                try:
                    return CafeMapper.para_local(item)
                except ValueError:
                    return None
        return None
