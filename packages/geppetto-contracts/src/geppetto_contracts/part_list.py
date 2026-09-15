"""PartListDocument v1 + PartListRow (ADR-0009, ADR-0012; import-profiles.md §3).

Her ithalatın (CSV/XLSX/DXF + `ImportProfile`) ortak çıktısı. Önizleme-düzeltme ekranı bu belgeyi
gösterir; kullanıcı onayı olmadan `Part` yazılmaz.

Kurallar:
- `dimension_basis` **zorunlu, varsayılan yok**, `null` kabul edilmez (ADR-0009).
- Uzunluklar tam sayı µm; float ve string reddedilir (ADR-0002).
- Kenar bandı dört ayrı kenar (`EdgeBands`); her kenar `EdgeBandRef | None` (ADR-0006, karar K2).
- Bilinmeyen alan reddedilir (`extra="forbid"`); şema değişikliği yeni `schema_version` ister.
- İş kuralı (ham ölçü türetme, rotation/grain tutarlılığı) burada değil, domain'dedir.
"""

from __future__ import annotations

from typing import Literal, Self
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    StrictInt,
    field_validator,
    model_validator,
)

from geppetto_contracts.api.errors import ErrorDetail
from geppetto_contracts.types import DimensionBasis, Grain, PositiveMicron, Rotation

_MODEL_CONFIG = ConfigDict(frozen=True, extra="forbid")


class EdgeBandRef(BaseModel):
    """Bir kenara vurulan bant: kaynaktaki ad/kod ve eşlendiyse malzeme kimliği."""

    model_config = _MODEL_CONFIG

    material_ref: str = Field(min_length=1)
    material_id: UUID | None = None


class EdgeBands(BaseModel):
    """Dört kenarın bant ataması. Alan adları `EdgeRef` değerleridir; bantsız kenar `None`."""

    model_config = _MODEL_CONFIG

    L1: EdgeBandRef | None = None
    L2: EdgeBandRef | None = None
    W1: EdgeBandRef | None = None
    W2: EdgeBandRef | None = None


class PartListSource(BaseModel):
    """Belgenin kaynağı (izlenebilirlik)."""

    model_config = _MODEL_CONFIG

    profile_id: UUID
    file_name: str = Field(min_length=1)
    file_hash: str = Field(min_length=1)
    imported_at: AwareDatetime

    @field_validator("imported_at")
    @classmethod
    def _utc_only(cls, value: AwareDatetime) -> AwareDatetime:
        offset = value.utcoffset()
        if offset is None or offset.total_seconds() != 0:
            msg = "imported_at UTC olmalı (ADR-0010)"
            raise ValueError(msg)
        return value


class PartListRow(BaseModel):
    """Kaynak listedeki tek satır. Ölçüler `dimension_basis`'e göre bitmiş veya ham."""

    model_config = _MODEL_CONFIG

    row_index: StrictInt = Field(ge=0)
    label: str
    material_ref: str
    material_id: UUID | None = None
    length_um: PositiveMicron
    width_um: PositiveMicron
    thickness_um: PositiveMicron | None = None
    qty: StrictInt = Field(gt=0)
    edges: EdgeBands = Field(default_factory=EdgeBands)
    rotation: Rotation | None = None
    grain: Grain | None = None
    project_ref: str | None = None
    notes: str | None = None
    warnings: list[ErrorDetail] = Field(default_factory=list)


class PartListDocument(BaseModel):
    """İthalat belgesi, şema sürümü 1."""

    model_config = _MODEL_CONFIG

    schema_version: Literal["1"]
    dimension_basis: DimensionBasis
    unit_note: str
    source: PartListSource
    rows: list[PartListRow]

    @model_validator(mode="after")
    def _row_index_unique(self) -> Self:
        indexes = [row.row_index for row in self.rows]
        if len(indexes) != len(set(indexes)):
            msg = "rows[].row_index tekil olmalı"
            raise ValueError(msg)
        return self
