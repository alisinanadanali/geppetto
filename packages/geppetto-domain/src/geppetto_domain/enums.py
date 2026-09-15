"""Domain enum'ları (glossary.md; ADR-0003, ADR-0006, ADR-0008, ADR-0009).

Değerler `SCREAMING_SNAKE` ve büyük/küçük harf duyarlıdır; etiketler web `glossary:` çevirisidir
(ADR-0010). Veritabanında PostgreSQL enum değil `text` + check constraint (data-model.md).

Burada yalnızca bölüm 2'de gereken enum'lar vardır; diğerleri (`OrderStatus`, `CutJobStatus` …)
kullanan bölümde eklenir. Contracts bunları `geppetto_contracts.types` ile dışa aktarır.
"""

from __future__ import annotations

from enum import StrEnum


class MaterialType(StrEnum):
    """Malzeme tipi; oluşturulduktan sonra değişmez (material-model.md §1)."""

    SHEET = "SHEET"
    EDGE_BAND = "EDGE_BAND"
    HARDWARE = "HARDWARE"
    LINEAR = "LINEAR"
    VENEER = "VENEER"
    CONSUMABLE = "CONSUMABLE"


class Rotation(StrEnum):
    """Yerleşimde izin verilen dönüşler (ADR-0006)."""

    NONE = "NONE"
    ROT_180 = "ROT_180"
    ROT_90 = "ROT_90"
    ANY = "ANY"


class Grain(StrEnum):
    """Parça damar yönü (ADR-0006). `NONE` dışındaki değerler 90° dönüşü yasaklar."""

    NONE = "NONE"
    ALONG_LENGTH = "ALONG_LENGTH"
    ALONG_WIDTH = "ALONG_WIDTH"


class EdgeRef(StrEnum):
    """Parça kenarı (ADR-0006). L1: Y=0, L2: Y=width, W1: X=0, W2: X=length.

    L kenarları genişliği, W kenarları uzunluğu kısaltır (dimensions.md §2).
    Kenara vurulan bandın referansı bu enum değil, `EdgeBandRef` nesnesidir.
    """

    L1 = "L1"
    L2 = "L2"
    W1 = "W1"
    W2 = "W2"


class FaceRef(StrEnum):
    """Parça yüzü (ADR-0006). FACE1 = görünen yüz."""

    FACE1 = "FACE1"
    FACE2 = "FACE2"


class MovementType(StrEnum):
    """Stok hareketi tipi (ADR-0003). İşaret ve anlam ADR tablosundadır."""

    RECEIPT = "RECEIPT"
    RESERVE = "RESERVE"
    RELEASE = "RELEASE"
    CONSUME = "CONSUME"
    OFFCUT_IN = "OFFCUT_IN"
    SCRAP = "SCRAP"
    ADJUST = "ADJUST"


class DimensionBasis(StrEnum):
    """İthal edilen ölçünün esası (ADR-0009). Varsayılanı yoktur; kullanıcı onaylar."""

    FINISHED = "FINISHED"
    RAW = "RAW"
