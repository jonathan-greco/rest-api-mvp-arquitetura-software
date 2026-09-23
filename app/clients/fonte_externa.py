"""Interface de uma fonte externa de cafés (somente leitura).

Novas fontes (outra API de cafés, por exemplo) entram como novas implementações
desta interface, sem alterar o CafeService (princípio Aberto/Fechado).
"""
from abc import ABC, abstractmethod


class FonteCafeExterna(ABC):
    """Contrato mínimo: métodos list e get, com cafés já convertidos para o formato local."""

    @abstractmethod
    def list(self) -> list[dict]:
        """Retorna todos os cafés externos no formato local (campos em português).

        Lança FonteExternaIndisponivelError se a fonte falhar.
        """

    @abstractmethod
    def get(self, id_externo: int) -> dict | None:
        """Retorna um café externo pelo id da fonte, ou None se não existir."""
