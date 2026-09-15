"""Tek hata kodu kataloğu (ADR-0010; i18n.md §2).

Backend metin döndürmez, kod döndürür: `{"code": ..., "params": {...}, "field": ...}`.
Çeviriler `apps/web/src/i18n/{tr,en}/errors.json` içindedir; backend çeviri taşımaz.

Kurallar:
- Kod `SCREAMING_SNAKE`; ilk kelime domain alanı (`ALLOWED_PREFIXES`).
- Her kodun `CATALOG` girdisi vardır: `params` anahtarları ve `severity`.
  `ERROR` işlemi engeller; `WARNING` önizlemede gösterilir ve kabul edilebilir
  (import-profiles.md §6).
- Param değerleri JSON skaler: `str | int | bool | None`. Float yok; uzunluk `_um` tam sayı
  (ADR-0002).
- Kullanılmayan kod eklenmez (lessons L-005; karar K4). Boş önek serbesttir; kod, onu üreten
  özellik yazılırken eklenir.
- Kod silmek veya yeniden adlandırmak API sözleşme değişikliğidir; snapshot testi bilinçli
  güncelleme ister.

| Kod | Sev. | Params | Kaynak |
|---|---|---|---|
| PART_EXCEEDS_SHEET | ERROR | part_label, sheet_length_um | i18n.md §2 |
| PART_RAW_DIMENSION_NON_POSITIVE | ERROR | part_label, raw_length_um, raw_width_um | ADR-0009 |
| PART_ROTATION_CONFLICTS_GRAIN | ERROR | part_label, rotation, grain | ADR-0006 |
| PART_FINISHED_ASSUMED_FROM_RAW | WARNING | part_label | dimensions.md §5 |
| IMPORT_DIMENSION_BASIS_REQUIRED | ERROR | — | ADR-0012 (K4) |
| IMPORT_ROW_INVALID | ERROR | row_index | import-profiles.md (K4) |
| IMPORT_MATERIAL_UNMAPPED | ERROR | row_index, material_ref | import-profiles.md (K4) |
| IMPORT_EDGE_COUNT_AMBIGUOUS | WARNING | row_index, edge_count | import-profiles.md §4 |
| IMPORT_EDGES_MISSING | WARNING | row_index | import-profiles.md §4 |
| IMPORT_NON_RECTANGULAR_OUTLINE | ERROR | row_index | dxf-conventions.md §4 |
| IMPORT_UNKNOWN_LAYER | WARNING | layer | dxf-conventions.md §4 |
| SOLVER_OVERLAP | ERROR | sheet_index | ADR-0016 I1 |
| SOLVER_OUT_OF_BOUNDS | ERROR | sheet_index | ADR-0016 I2 |
| SOLVER_KERF_MISSING | ERROR | sheet_index | ADR-0016 I3 |
| SOLVER_NOT_GUILLOTINE | ERROR | sheet_index | ADR-0016 I4 |
| SOLVER_ROTATION_VIOLATION | ERROR | sheet_index | ADR-0016 I5 |
| SOLVER_PART_COUNT_MISMATCH | ERROR | expected, actual | ADR-0016 I6 |
| SOLVER_AREA_CONSERVATION | ERROR | sheet_index | ADR-0016 I7 |
| SOLVER_NONDETERMINISTIC | ERROR | seed | ADR-0016 I8 |
| MATERIAL_TYPE_IMMUTABLE | ERROR | current_type, requested_type | material-model.md §1 |
| MATERIAL_CURRENCY_MISMATCH | WARNING | material_code, currency, base_currency | ADR-0010 |

K4 işaretli üç kod dokümanda geçmez; şema doğrulaması ve önizleme için eklendi.
Param adları ilk sürümdür; üreten kod (bölüm 3–6) yazılırken netleşir ve tabloyla birlikte
güncellenir.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Final

ALLOWED_PREFIXES: Final[tuple[str, ...]] = (
    "PART_",
    "STOCK_",
    "IMPORT_",
    "SOLVER_",
    "AUTH_",
    "TENANT_",
    "MATERIAL_",
    "MACHINE_",
    "EXPORT_",
)


class Severity(StrEnum):
    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class CodeSpec:
    """Bir hata kodunun sözleşmesi: beklenen `params` anahtarları ve ciddiyeti."""

    params: tuple[str, ...]
    severity: Severity


class ErrorCode(StrEnum):
    # PART_
    PART_EXCEEDS_SHEET = "PART_EXCEEDS_SHEET"
    PART_RAW_DIMENSION_NON_POSITIVE = "PART_RAW_DIMENSION_NON_POSITIVE"
    PART_ROTATION_CONFLICTS_GRAIN = "PART_ROTATION_CONFLICTS_GRAIN"
    PART_FINISHED_ASSUMED_FROM_RAW = "PART_FINISHED_ASSUMED_FROM_RAW"
    # IMPORT_
    IMPORT_DIMENSION_BASIS_REQUIRED = "IMPORT_DIMENSION_BASIS_REQUIRED"
    IMPORT_ROW_INVALID = "IMPORT_ROW_INVALID"
    IMPORT_MATERIAL_UNMAPPED = "IMPORT_MATERIAL_UNMAPPED"
    IMPORT_EDGE_COUNT_AMBIGUOUS = "IMPORT_EDGE_COUNT_AMBIGUOUS"
    IMPORT_EDGES_MISSING = "IMPORT_EDGES_MISSING"
    IMPORT_NON_RECTANGULAR_OUTLINE = "IMPORT_NON_RECTANGULAR_OUTLINE"
    IMPORT_UNKNOWN_LAYER = "IMPORT_UNKNOWN_LAYER"
    # SOLVER_
    SOLVER_OVERLAP = "SOLVER_OVERLAP"
    SOLVER_OUT_OF_BOUNDS = "SOLVER_OUT_OF_BOUNDS"
    SOLVER_KERF_MISSING = "SOLVER_KERF_MISSING"
    SOLVER_NOT_GUILLOTINE = "SOLVER_NOT_GUILLOTINE"
    SOLVER_ROTATION_VIOLATION = "SOLVER_ROTATION_VIOLATION"
    SOLVER_PART_COUNT_MISMATCH = "SOLVER_PART_COUNT_MISMATCH"
    SOLVER_AREA_CONSERVATION = "SOLVER_AREA_CONSERVATION"
    SOLVER_NONDETERMINISTIC = "SOLVER_NONDETERMINISTIC"
    # MATERIAL_
    MATERIAL_TYPE_IMMUTABLE = "MATERIAL_TYPE_IMMUTABLE"
    MATERIAL_CURRENCY_MISMATCH = "MATERIAL_CURRENCY_MISMATCH"


_E = Severity.ERROR
_W = Severity.WARNING

CATALOG: Final[Mapping[ErrorCode, CodeSpec]] = MappingProxyType(
    {
        ErrorCode.PART_EXCEEDS_SHEET: CodeSpec(("part_label", "sheet_length_um"), _E),
        ErrorCode.PART_RAW_DIMENSION_NON_POSITIVE: CodeSpec(
            ("part_label", "raw_length_um", "raw_width_um"), _E
        ),
        ErrorCode.PART_ROTATION_CONFLICTS_GRAIN: CodeSpec(("part_label", "rotation", "grain"), _E),
        ErrorCode.PART_FINISHED_ASSUMED_FROM_RAW: CodeSpec(("part_label",), _W),
        ErrorCode.IMPORT_DIMENSION_BASIS_REQUIRED: CodeSpec((), _E),
        ErrorCode.IMPORT_ROW_INVALID: CodeSpec(("row_index",), _E),
        ErrorCode.IMPORT_MATERIAL_UNMAPPED: CodeSpec(("row_index", "material_ref"), _E),
        ErrorCode.IMPORT_EDGE_COUNT_AMBIGUOUS: CodeSpec(("row_index", "edge_count"), _W),
        ErrorCode.IMPORT_EDGES_MISSING: CodeSpec(("row_index",), _W),
        ErrorCode.IMPORT_NON_RECTANGULAR_OUTLINE: CodeSpec(("row_index",), _E),
        ErrorCode.IMPORT_UNKNOWN_LAYER: CodeSpec(("layer",), _W),
        ErrorCode.SOLVER_OVERLAP: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_OUT_OF_BOUNDS: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_KERF_MISSING: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_NOT_GUILLOTINE: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_ROTATION_VIOLATION: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_PART_COUNT_MISMATCH: CodeSpec(("expected", "actual"), _E),
        ErrorCode.SOLVER_AREA_CONSERVATION: CodeSpec(("sheet_index",), _E),
        ErrorCode.SOLVER_NONDETERMINISTIC: CodeSpec(("seed",), _E),
        ErrorCode.MATERIAL_TYPE_IMMUTABLE: CodeSpec(("current_type", "requested_type"), _E),
        ErrorCode.MATERIAL_CURRENCY_MISMATCH: CodeSpec(
            ("material_code", "currency", "base_currency"), _W
        ),
    }
)
