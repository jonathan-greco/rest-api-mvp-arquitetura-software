"""Campos Marshmallow customizados com sanitização de entrada."""
import bleach
from marshmallow import fields


class TextoSeguro(fields.String):
    """Texto que passa por `strip`, remoção de caracteres de controle e de qualquer HTML.

    Protege contra XSS armazenado: tags são removidas e caracteres especiais
    (<, >, &) ficam escapados. Só aceita strings (números e listas são recusados).
    """

    def _deserialize(self, value, attr, data, **kwargs):
        texto = super()._deserialize(value, attr, data, **kwargs)
        # Remove caracteres de controle (exceto quebra de linha e tab).
        texto = "".join(c for c in texto if c.isprintable() or c in "\n\t")
        # Remove qualquer tag HTML (nenhuma é permitida).
        return bleach.clean(texto.strip(), tags=[], attributes={}, strip=True).strip()


class TextoMinusculo(TextoSeguro):
    """TextoSeguro convertido para minúsculas; usado em listas controladas (torra, moagem)."""

    def _deserialize(self, value, attr, data, **kwargs):
        return super()._deserialize(value, attr, data, **kwargs).lower()


class EmailNormalizado(fields.Email):
    """E-mail validado por regex e normalizado para minúsculas, sem espaços nas pontas."""

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, str):
            value = value.strip().lower()
        return super()._deserialize(value, attr, data, **kwargs)
