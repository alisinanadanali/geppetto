"""Hata kodu kataloğu ve hata zarfı (ADR-0010; i18n.md §2; todo 2.1, 2.4)."""

import json
import os
import re
from pathlib import Path

import pytest
from pydantic import ValidationError

from geppetto_contracts.api.errors import ErrorDetail, ErrorResponse
from geppetto_contracts.error_codes import ALLOWED_PREFIXES, CATALOG, ErrorCode, Severity

SNAPSHOT = Path(__file__).parent / "snapshots" / "error_codes.json"
CODE_PATTERN = re.compile(r"^[A-Z][A-Z0-9]*(_[A-Z0-9]+)+$")


def test_codes_are_screaming_snake_with_allowed_prefix() -> None:
    for code in ErrorCode:
        assert code.name == code.value
        assert CODE_PATTERN.fullmatch(code.value), code
        assert code.value.startswith(ALLOWED_PREFIXES), code


def test_prefix_list_matches_i18n_doc() -> None:
    assert ALLOWED_PREFIXES == (
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


def test_catalog_covers_every_code_exactly() -> None:
    assert set(CATALOG) == set(ErrorCode)
    for code, spec in CATALOG.items():
        assert len(spec.params) == len(set(spec.params)), code
        assert all(re.fullmatch(r"[a-z][a-z0-9_]*", p) for p in spec.params), code


def test_catalog_is_read_only() -> None:
    with pytest.raises(TypeError):
        CATALOG[ErrorCode.SOLVER_OVERLAP] = CATALOG[ErrorCode.SOLVER_KERF_MISSING]  # type: ignore[index]


def _catalog_as_json() -> dict[str, dict[str, object]]:
    return {
        code.value: {"params": list(spec.params), "severity": spec.severity.value}
        for code, spec in sorted(CATALOG.items())
    }


def test_catalog_snapshot() -> None:
    """Kod eklemek/silmek/değiştirmek API sözleşmesidir; snapshot bilinçli güncellenir.

    Güncelleme: `UPDATE_SNAPSHOTS=1 uv run pytest packages/geppetto-contracts`.
    """
    current = _catalog_as_json()
    if os.environ.get("UPDATE_SNAPSHOTS") == "1":
        SNAPSHOT.parent.mkdir(exist_ok=True)
        SNAPSHOT.write_text(json.dumps(current, indent=2) + "\n", encoding="utf-8")
    assert json.loads(SNAPSHOT.read_text(encoding="utf-8")) == current


def test_error_detail_example_from_i18n_doc() -> None:
    raw = (
        '{"code": "PART_EXCEEDS_SHEET", '
        '"params": {"part_label": "Yan-1", "sheet_length_um": 2800000}, '
        '"field": "rows[3].length_um"}'
    )
    detail = ErrorDetail.model_validate_json(raw)
    assert detail.code is ErrorCode.PART_EXCEEDS_SHEET
    assert detail.params["sheet_length_um"] == 2800000


@pytest.mark.parametrize(
    "params",
    [
        {"part_label": "Yan-1"},
        {"part_label": "Yan-1", "sheet_length_um": 2800000, "extra": 1},
        {"part_label": "Yan-1", "sheet_length_um": 2800.0},
        {"part_label": "Yan-1", "sheet_length_um": [2800000]},
    ],
)
def test_error_detail_rejects_params_not_matching_catalog(params: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        ErrorDetail.model_validate({"code": "PART_EXCEEDS_SHEET", "params": params})


def test_error_detail_rejects_unknown_code_and_text_fields() -> None:
    with pytest.raises(ValidationError):
        ErrorDetail.model_validate({"code": "PART_SOMETHING_INVENTED", "params": {}})
    with pytest.raises(ValidationError):
        ErrorDetail.model_validate(
            {"code": "IMPORT_DIMENSION_BASIS_REQUIRED", "params": {}, "detail": "metin"}
        )


def test_error_response_with_details() -> None:
    first = ErrorDetail(code=ErrorCode.IMPORT_ROW_INVALID, params={"row_index": 3})
    response = ErrorResponse(
        code=first.code,
        params=first.params,
        details=[first, ErrorDetail(code=ErrorCode.IMPORT_DIMENSION_BASIS_REQUIRED)],
    )
    assert ErrorResponse.model_validate_json(response.model_dump_json()) == response


def test_warning_codes_are_the_documented_ones() -> None:
    warnings = {code for code, spec in CATALOG.items() if spec.severity is Severity.WARNING}
    assert warnings == {
        ErrorCode.PART_FINISHED_ASSUMED_FROM_RAW,
        ErrorCode.IMPORT_EDGE_COUNT_AMBIGUOUS,
        ErrorCode.IMPORT_EDGES_MISSING,
        ErrorCode.IMPORT_UNKNOWN_LAYER,
        ErrorCode.MATERIAL_CURRENCY_MISMATCH,
    }
