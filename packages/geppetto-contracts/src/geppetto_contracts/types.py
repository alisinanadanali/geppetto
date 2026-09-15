"""Ortak tipler (ADR-0002, ADR-0010; karar K1, 2026-09-15).

Tanımlar `geppetto_domain.units` ve `geppetto_domain.enums` içindedir; burada yalnızca yeniden
dışa aktarılır. Sebep: bağımlılık yönü `contracts → domain` (ADR-0001); domain bu tiplere
kendi varlıklarında ihtiyaç duyar ve contracts'ı import edemez. Tek kaynak domain'dir;
API ve adaptörler buradan import eder, iki yol aynı nesneyi verir.
"""

from geppetto_domain.enums import (
    DimensionBasis,
    EdgeRef,
    FaceRef,
    Grain,
    MaterialType,
    MovementType,
    Rotation,
)
from geppetto_domain.units import (
    MAX_SAFE_INT,
    BasisPoint,
    CurrencyCode,
    Micron,
    MicronArea,
    MinorAmount,
    Money,
    NonNegativeMicron,
    PositiveMicron,
)

__all__ = [
    "MAX_SAFE_INT",
    "BasisPoint",
    "CurrencyCode",
    "DimensionBasis",
    "EdgeRef",
    "FaceRef",
    "Grain",
    "MaterialType",
    "Micron",
    "MicronArea",
    "MinorAmount",
    "Money",
    "MovementType",
    "NonNegativeMicron",
    "PositiveMicron",
    "Rotation",
]
