"""Funções utilitárias de texto."""
import unicodedata


def normalizar_texto(valor: object) -> str:
    """Normaliza um texto para comparação: minúsculas, sem acentos e sem espaços extras.

    Usado para comparar nomes de cafés locais e externos
    """
    if valor is None:
        return ""
    texto = unicodedata.normalize("NFKD", str(valor))
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return " ".join(texto.lower().split())
