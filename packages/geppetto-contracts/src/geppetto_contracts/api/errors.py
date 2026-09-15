"""Hata cevabı zarfı (ADR-0010; i18n.md §2).

```json
{"code": "PART_EXCEEDS_SHEET", "params": {"part_label": "Yan-1", "sheet_length_um": 2800000},
 "field": "rows[3].length_um"}
```

`params` anahtarları `CATALOG`'daki sözleşmeyle birebir eşleşmek zorundadır. Pydantic
`ValidationError` → `ErrorResponse` çevirisi API katmanındadır (bölüm 5).
"""

from __future__ import annotations

from typing import Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    StrictStr,
    model_validator,
)

from geppetto_contracts.error_codes import CATALOG, ErrorCode

ParamValue = StrictStr | StrictInt | StrictBool | None
"""Param değeri JSON skaler; float yok (ADR-0002)."""


class ErrorDetail(BaseModel):
    """Tek hata veya uyarı: kod, parametreler, opsiyonel alan yolu."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: ErrorCode
    params: dict[str, ParamValue] = Field(default_factory=dict)
    field: str | None = None

    @model_validator(mode="after")
    def _params_match_catalog(self) -> Self:
        expected = set(CATALOG[self.code].params)
        actual = set(self.params)
        if actual != expected:
            missing = sorted(expected - actual)
            extra = sorted(actual - expected)
            msg = f"{self.code}: params uyuşmuyor; eksik={missing} fazla={extra}"
            raise ValueError(msg)
        return self


class ErrorResponse(ErrorDetail):
    """HTTP hata gövdesi. Birden çok alan hatasında ilki üst düzeyde, tümü `details` içinde."""

    details: list[ErrorDetail] = Field(default_factory=list)
