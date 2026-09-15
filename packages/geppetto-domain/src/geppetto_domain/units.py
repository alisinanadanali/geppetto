"""Kanonik birim tipleri (ADR-0002, ADR-0010; i18n.md §3).

Uzunluk tam sayı µm, alan tam sayı µm², para minor unit + ISO 4217, oran basis point.
Float, string ve bool bu tiplerde reddedilir (strict). Sınır: JavaScript güvenli tam sayısı
(2^53 − 1), çünkü değerler API üzerinden TypeScript `number`'a gider (ADR-0002).

Bu modül domain'dedir, contracts değil: domain contracts'ı import edemez (ADR-0001);
contracts bu tipleri `geppetto_contracts.types` üzerinden yeniden dışa aktarır.
"""

from __future__ import annotations

from typing import Annotated, Final

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StringConstraints

MAX_SAFE_INT: Final = 2**53 - 1
"""JavaScript `Number.MAX_SAFE_INTEGER`; API sınırında tam sayı kaybı olmaması için üst sınır."""

Micron = Annotated[StrictInt, Field(ge=-MAX_SAFE_INT, le=MAX_SAFE_INT)]
"""Uzunluk, µm. İşaretli (ofset/koordinat). 18 mm = 18000."""

PositiveMicron = Annotated[StrictInt, Field(gt=0, le=MAX_SAFE_INT)]
"""Sıfırdan büyük uzunluk, µm (parça/plaka ölçüsü, bant kalınlığı)."""

NonNegativeMicron = Annotated[StrictInt, Field(ge=0, le=MAX_SAFE_INT)]
"""Sıfır veya pozitif uzunluk, µm (trim, kerf, oversize)."""

MicronArea = Annotated[StrictInt, Field(ge=0, le=MAX_SAFE_INT)]
"""Alan, µm². 2800 × 2100 mm plaka = 5,88 × 10¹² µm²."""

BasisPoint = Annotated[StrictInt, Field(ge=-MAX_SAFE_INT, le=MAX_SAFE_INT)]
"""Oran, basis point. 2000 = %20."""

MinorAmount = Annotated[StrictInt, Field(ge=-MAX_SAFE_INT, le=MAX_SAFE_INT)]
"""Para tutarı, para biriminin minor unit'i (kuruş, cent)."""

CurrencyCode = Annotated[str, StringConstraints(strict=True, pattern=r"^[A-Z]{3}$")]
"""ISO 4217 alfabetik kod, büyük harf (`TRY`, `EUR`). Kod listesi doğrulanmaz; biçim doğrulanır."""


class Money(BaseModel):
    """Para değeri: minor unit tam sayı + ISO 4217 kodu. Değiştirilemez."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    minor: MinorAmount
    currency: CurrencyCode
