"""Regras de negócio do Cafe, incluindo a combinação (merge) com a API externa SampleAPIs Coffee."""
import logging

from app.clients.cafe_mapper import ORIGEM_EXTERNA, ORIGEM_LOCAL
from app.clients.fonte_externa import FonteCafeExterna
from app.errors.exceptions import FonteExternaIndisponivelError, NaoEncontradoError
from app.models import Cafe
from app.repositories.base import RepositorioBase
from app.schemas.cafe_schema import CafeSchema
from app.utils.texto import normalizar_texto

logger = logging.getLogger(__name__)

# Estados informados na resposta pública sobre a consulta à API externa.
FONTE_DISPONIVEL = "disponivel"
FONTE_INDISPONIVEL = "indisponivel"
FONTE_DESATIVADA = "desativada"


class CafeService:
    """Casos de uso de café. Depende de abstrações (repositório e fonte externa) injetadas."""

    def __init__(self, repositorio: RepositorioBase, fonte_externa: FonteCafeExterna):
        self._repo = repositorio
        self._fonte_externa = fonte_externa
        self._schema = CafeSchema()

    # ------------------------------------------------------------------ Escrita (exige Admin nas rotas)
    def get_local(self, id_: int) -> Cafe:
        cafe = self._repo.get(id_)
        if cafe is None:
            raise NaoEncontradoError(f"Café {id_} não encontrado.")
        return cafe

    def criar(self, dados: dict) -> Cafe:
        return self._repo.criar(dados)

    def atualizar(self, id_: int, dados: dict) -> Cafe:
        return self._repo.atualizar(self.get_local(id_), dados)

    def remover(self, id_: int) -> None:
        self._repo.remover(self.get_local(id_))

    # ------------------------------------------------------------------ Público (local + externo)
    def list_publico(self, filtros, ordenar_por, direcao, pagina, por_pagina, incluir_externos=True):
        """Lista cafés locais e, quando existirem, concatena os da SampleAPIs Coffee que faltam no banco.

        Regras:
        - o dado local prevalece: item externo com o mesmo nome (normalizado) de um local é descartado;
        - se a API externa falhar, a resposta contém só os dados locais (`fonte_externa`= indisponivel);
        - itens externos são marcados com origem="externa" e id=None (o id deles vai em id_externo);
        - a fonte expõe cafés quentes e gelados em endpoints separados; aqui os dois são buscados
          juntos, sem distinção (regra definida no escopo do projeto).
        """
        locais_filtrados, _ = self._repo.list(filtros, ordenar_por, direcao)
        itens = [self._serializar_local(c) for c in locais_filtrados]

        fonte = FONTE_DESATIVADA
        if incluir_externos:
            try:
                externos = self._fonte_externa.list()
                fonte = FONTE_DISPONIVEL
            except FonteExternaIndisponivelError:
                externos, fonte = [], FONTE_INDISPONIVEL

            # Compara com TODOS os cafés locais (não só os filtrados) para não duplicar.
            todos_locais, _ = self._repo.list()
            nomes_locais = {normalizar_texto(c.nome) for c in todos_locais}
            for externo in externos:
                if normalizar_texto(externo["nome"]) in nomes_locais:
                    continue
                if self._corresponde_filtros(externo, filtros):
                    itens.append(externo)

        itens = self._ordenar(itens, ordenar_por, direcao)
        total = len(itens)
        inicio = (pagina - 1) * por_pagina
        return {
            "itens": itens[inicio:inicio + por_pagina],
            "total": total,
            "pagina": pagina,
            "por_pagina": por_pagina,
            "fonte_externa": fonte,
        }

    def get_publico(self, id_: int, origem: str = "auto") -> dict:
        """Busca um café. origem: local | externa | auto (local e, se não achar, externa).

        Na origem externa, como a fonte não tem endpoint por id, a busca varre as listas
        hot e iced; em caso de colisão de id entre elas, o primeiro encontrado é devolvido.
        """
        if origem in ("auto", "local"):
            cafe = self._repo.get(id_)
            if cafe is not None:
                return self._serializar_local(cafe)
            if origem == "local":
                raise NaoEncontradoError(f"Café {id_} não encontrado no banco local.")

        # origem externa (ou fallback do modo auto). Falha externa vira 502.
        externo = self._fonte_externa.get(id_)
        if externo is None:
            raise NaoEncontradoError(f"Café {id_} não encontrado.")
        return externo

    # ------------------------------------------------------------------ Auxiliares
    def _serializar_local(self, cafe: Cafe) -> dict:
        dado = self._schema.dump(cafe)
        dado["id_externo"] = None
        dado["origem"] = ORIGEM_LOCAL
        return dado

    @staticmethod
    def _corresponde_filtros(cafe: dict, filtros: dict) -> bool:
        """Aplica em memória, nos itens externos, os mesmos filtros usados no banco."""
        if filtros.get("nome") and normalizar_texto(filtros["nome"]) not in normalizar_texto(cafe.get("nome")):
            return False
        return True

    @staticmethod
    def _ordenar(itens: list[dict], ordenar_por: str, direcao: str) -> list[dict]:
        """Ordena a lista combinada; valores ausentes (ex.: id dos externos) ficam no fim."""
        com_valor = [i for i in itens if i.get(ordenar_por) is not None]
        sem_valor = [i for i in itens if i.get(ordenar_por) is None]
        com_valor.sort(
            key=lambda i: normalizar_texto(i[ordenar_por]) if isinstance(i[ordenar_por], str) else i[ordenar_por],
            reverse=(direcao == "desc"),
        )
        def _chave_sem_valor(item: dict) -> tuple:
            id_externo = item.get("id_externo") or 0
            # Defesa extra: se algum id_externo escapar da normalização do Mapper e vier
            # como texto, convertemos para int aqui também (ou 0 se não for possível),
            # para nunca comparar str com int e quebrar o sort.
            if not isinstance(id_externo, int):
                try:
                    id_externo = int(str(id_externo).strip())
                except (TypeError, ValueError):
                    id_externo = 0
            return (item.get("origem") != ORIGEM_EXTERNA, id_externo)

        sem_valor.sort(key=_chave_sem_valor)
        return com_valor + sem_valor
