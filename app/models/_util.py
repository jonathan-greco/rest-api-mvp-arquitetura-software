"""Utilitários compartilhados entre os modelos de negócio."""
from datetime import datetime, timezone


def agora_utc() -> datetime:
    """Data/hora atual em UTC, usada como valor padrão de campos criado_em."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
