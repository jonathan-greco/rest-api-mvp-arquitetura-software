"""Schemas de validação e serialização do Cafe.

Campos alinhados ao formato da API externa SampleAPIs Coffee: nome (title), descricao
(description), ingredientes (ingredients, lista) e imagem_url (image).
"""
import bleach
from marshmallow import RAISE, Schema, ValidationError, fields, validate

from app.schemas.base import ListagemBaseSchema
from app.schemas.campos import TextoSeguro

COLUNAS_ORDENAVEIS = ["id", "nome"]

_MAX_ITENS = 20
_MAX_TAMANHO_ITEM = 120


class IngredientesField(fields.Field):
    """Ingredientes: lista de strings na API, guardados como texto (vírgula) no banco.

    - Entrada (load): recebe uma lista de strings, sanitiza cada item (como TextoSeguro)
      e devolve um único texto separado por vírgula, pronto para a coluna do modelo.
    - Saída (dump): lê o texto salvo e devolve de volta como lista, no mesmo formato da
      SampleAPIs Coffee (["Espresso", "Steamed milk"]).
    """

    def _serialize(self, value, attr, obj, **kwargs):
        if not value:
            return []
        return [parte.strip() for parte in str(value).split(",") if parte.strip()]

    def _deserialize(self, value, attr, data, **kwargs):
        if not isinstance(value, list):
            raise ValidationError("Deve ser uma lista de textos.")
        if len(value) > _MAX_ITENS:
            raise ValidationError(f"No máximo {_MAX_ITENS} ingredientes.")
        itens = []
        for item in value:
            if not isinstance(item, str):
                raise ValidationError("Cada ingrediente deve ser um texto.")
            texto = bleach.clean(item.strip(), tags=[], attributes={}, strip=True).strip()
            if not texto:
                continue
            if len(texto) > _MAX_TAMANHO_ITEM:
                raise ValidationError(f"Cada ingrediente deve ter no máximo {_MAX_TAMANHO_ITEM} caracteres.")
            itens.append(texto)
        return ", ".join(itens) or None


class CafeSchema(Schema):
    """Entrada (POST/PUT) e saída de um café local."""

    class Meta:
        unknown = RAISE  # campos não previstos geram erro (evita mass assignment)

    id = fields.Int(dump_only=True)
    nome = TextoSeguro(required=True, validate=validate.Length(min=2, max=120))
    descricao = TextoSeguro(load_default=None, allow_none=True, validate=validate.Length(max=2000))
    ingredientes = IngredientesField(load_default=None)
    # Apenas http/https, com tamanho máximo; o validador de URL recusa espaços e tags.
    imagem_url = fields.Url(
        schemes={"http", "https"},
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=500),
    )


class CafeListagemSchema(ListagemBaseSchema):
    """Filtros e ordenação do GET de cafés (área Admin, apenas banco local)."""

    nome = TextoSeguro(validate=validate.Length(max=120))
    ordenar_por = fields.Str(load_default="id", validate=validate.OneOf(COLUNAS_ORDENAVEIS))


class CafePublicoListagemSchema(CafeListagemSchema):
    """Igual ao anterior, com a opção de desligar a consulta à API externa."""

    incluir_externos = fields.Bool(load_default=True)


class CafeConsultaSchema(Schema):
    """Parâmetros do GET de um café por id."""

    class Meta:
        unknown = RAISE

    origem = fields.Str(load_default="auto", validate=validate.OneOf(["auto", "local", "externa"]))
