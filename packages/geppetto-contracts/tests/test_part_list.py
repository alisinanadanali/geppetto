"""PartListDocument v1 şema testleri (ADR-0009, ADR-0012; import-profiles.md §3; todo 2.3, 2.4)."""

import json
import os
from datetime import UTC, datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from geppetto_contracts.api.errors import ErrorDetail
from geppetto_contracts.error_codes import ErrorCode
from geppetto_contracts.part_list import (
    EdgeBandRef,
    EdgeBands,
    PartListDocument,
    PartListRow,
    PartListSource,
)
from geppetto_contracts.types import MAX_SAFE_INT, DimensionBasis, Grain, Rotation

SNAPSHOT = Path(__file__).parent / "snapshots" / "part_list_v1.schema.json"


def _row(**overrides: Any) -> dict[str, Any]:
    row: dict[str, Any] = {
        "row_index": 0,
        "label": "Raf",
        "material_ref": "Suntalam 18 Beyaz",
        "length_um": 800000,
        "width_um": 500000,
        "qty": 2,
        "edges": {"L1": {"material_ref": "PVC 0.8 Beyaz"}, "L2": {"material_ref": "PVC 0.8 Beyaz"}},
    }
    row.update(overrides)
    return row


def _document(**overrides: Any) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "schema_version": "1",
        "dimension_basis": "FINISHED",
        "unit_note": "MM",
        "source": {
            "profile_id": "0192f0c4-6f7e-7a3b-9c1d-2e4f5a6b7c8d",
            "file_name": "liste.csv",
            "file_hash": "sha256:abc",
            "imported_at": "2026-09-15T10:00:00Z",
        },
        "rows": [_row()],
    }
    doc.update(overrides)
    return doc


# --- geçerli belge -------------------------------------------------------------------------


def test_valid_document_parses() -> None:
    doc = PartListDocument.model_validate(_document())
    row = doc.rows[0]
    assert doc.dimension_basis is DimensionBasis.FINISHED
    assert row.edges.L1 is not None
    assert row.edges.L1.material_ref == "PVC 0.8 Beyaz"
    assert row.edges.L1.material_id is None
    assert row.edges.W1 is None
    assert row.rotation is None and row.warnings == []


def test_row_warnings_carry_catalog_codes() -> None:
    warning = {"code": "IMPORT_EDGE_COUNT_AMBIGUOUS", "params": {"row_index": 0, "edge_count": 3}}
    doc = PartListDocument.model_validate(_document(rows=[_row(warnings=[warning])]))
    assert doc.rows[0].warnings[0].code is ErrorCode.IMPORT_EDGE_COUNT_AMBIGUOUS


# --- dimension_basis: zorunlu, varsayılan yok (ADR-0009) ------------------------------------


def test_dimension_basis_missing_is_rejected() -> None:
    doc = _document()
    del doc["dimension_basis"]
    with pytest.raises(ValidationError) as exc:
        PartListDocument.model_validate(doc)
    assert exc.value.errors()[0]["loc"] == ("dimension_basis",)
    assert exc.value.errors()[0]["type"] == "missing"


@pytest.mark.parametrize("value", [None, "", "finished", "Finished", "BOTH", 1, True])
def test_dimension_basis_invalid_is_rejected(value: object) -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(dimension_basis=value))


def test_dimension_basis_has_no_default_in_schema() -> None:
    schema = PartListDocument.model_json_schema()
    assert "dimension_basis" in schema["required"]
    assert "default" not in schema["properties"]["dimension_basis"]


# --- µm tam sayı zorunluluğu (ADR-0002) -----------------------------------------------------


@pytest.mark.parametrize("field", ["length_um", "width_um", "thickness_um"])
@pytest.mark.parametrize("value", [18000.0, 18000.5, "18000", True, 0, -1, MAX_SAFE_INT + 1])
def test_length_fields_require_positive_safe_int(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(**{field: value})]))


def test_float_micron_rejected_in_json_too() -> None:
    raw = json.dumps(_document(rows=[_row(length_um=800000.0)]))
    with pytest.raises(ValidationError):
        PartListDocument.model_validate_json(raw)


@pytest.mark.parametrize("value", [0, -1, 1.0, "2", True])
def test_qty_requires_positive_int(value: object) -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(qty=value)]))


# --- yapı ----------------------------------------------------------------------------------


def test_schema_version_other_than_1_rejected() -> None:
    for value in ("2", 1, None):
        with pytest.raises(ValidationError):
            PartListDocument.model_validate(_document(schema_version=value))


def test_unknown_fields_rejected() -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(raw_length_um=1))
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(quantity=2)]))


def test_edges_only_accept_l1_l2_w1_w2() -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(
            _document(rows=[_row(edges={"L3": {"material_ref": "PVC"}})])
        )
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(edges={"L1": {"material_ref": ""}})]))


def test_rotation_and_grain_values() -> None:
    doc = PartListDocument.model_validate(
        _document(rows=[_row(rotation="ROT_180", grain="ALONG_LENGTH")])
    )
    assert doc.rows[0].rotation is Rotation.ROT_180
    assert doc.rows[0].grain is Grain.ALONG_LENGTH
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(rotation="ROT_45")]))


def test_warning_with_unknown_code_or_wrong_params_rejected() -> None:
    for warning in (
        {"code": "IMPORT_GUESSED", "params": {}},
        {"code": "IMPORT_EDGES_MISSING", "params": {}},
    ):
        with pytest.raises(ValidationError):
            PartListDocument.model_validate(_document(rows=[_row(warnings=[warning])]))


def test_row_index_must_be_unique() -> None:
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(_document(rows=[_row(), _row(label="Yan")]))


@pytest.mark.parametrize("imported_at", ["2026-09-15T10:00:00", "2026-09-15T13:00:00+03:00"])
def test_imported_at_must_be_utc(imported_at: str) -> None:
    doc = _document()
    doc["source"]["imported_at"] = imported_at
    with pytest.raises(ValidationError):
        PartListDocument.model_validate(doc)


def test_document_is_frozen() -> None:
    doc = PartListDocument.model_validate(_document())
    with pytest.raises(ValidationError):
        doc.dimension_basis = DimensionBasis.RAW  # type: ignore[misc]


# --- round-trip (Hypothesis) ---------------------------------------------------------------

_text = st.text(min_size=1, max_size=20)
_um = st.integers(min_value=1, max_value=MAX_SAFE_INT)
_edge = st.none() | st.builds(EdgeBandRef, material_ref=_text, material_id=st.none() | st.uuids())


@st.composite
def documents(draw: st.DrawFn) -> PartListDocument:
    count = draw(st.integers(min_value=0, max_value=5))
    rows = [
        PartListRow(
            row_index=i,
            label=draw(st.text(max_size=20)),
            material_ref=draw(st.text(max_size=20)),
            material_id=draw(st.none() | st.uuids()),
            length_um=draw(_um),
            width_um=draw(_um),
            thickness_um=draw(st.none() | _um),
            qty=draw(st.integers(min_value=1, max_value=10_000)),
            edges=EdgeBands(L1=draw(_edge), L2=draw(_edge), W1=draw(_edge), W2=draw(_edge)),
            rotation=draw(st.none() | st.sampled_from(Rotation)),
            grain=draw(st.none() | st.sampled_from(Grain)),
            project_ref=draw(st.none() | _text),
            notes=draw(st.none() | _text),
            warnings=draw(
                st.lists(
                    st.just(
                        ErrorDetail(code=ErrorCode.IMPORT_EDGES_MISSING, params={"row_index": i})
                    ),
                    max_size=1,
                )
            ),
        )
        for i in range(count)
    ]
    return PartListDocument(
        schema_version="1",
        dimension_basis=draw(st.sampled_from(DimensionBasis)),
        unit_note=draw(st.text(max_size=10)),
        source=PartListSource(
            profile_id=draw(st.uuids()),
            file_name=draw(_text),
            file_hash=draw(_text),
            imported_at=draw(
                st.datetimes(
                    min_value=datetime(2000, 1, 1),
                    max_value=datetime(2100, 1, 1),
                    timezones=st.just(UTC),
                )
            ),
        ),
        rows=rows,
    )


@given(documents())
def test_json_round_trip(doc: PartListDocument) -> None:
    assert PartListDocument.model_validate_json(doc.model_dump_json()) == doc


def test_zero_offset_non_utc_timezone_is_accepted() -> None:
    doc = _document()
    doc["source"]["imported_at"] = datetime(2026, 9, 15, tzinfo=timezone(timedelta(0)))
    source = PartListDocument.model_validate(doc).source
    assert source.imported_at == datetime(2026, 9, 15, tzinfo=UTC)
    assert source.profile_id == UUID("0192f0c4-6f7e-7a3b-9c1d-2e4f5a6b7c8d")


# --- JSON şema snapshot --------------------------------------------------------------------


def test_json_schema_snapshot() -> None:
    """Şema değişikliği sözleşme değişikliğidir; bilinçli güncellenir.

    Güncelleme: `UPDATE_SNAPSHOTS=1 uv run pytest packages/geppetto-contracts`.
    """
    current = PartListDocument.model_json_schema()
    if os.environ.get("UPDATE_SNAPSHOTS") == "1":
        SNAPSHOT.parent.mkdir(exist_ok=True)
        SNAPSHOT.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", "utf-8")
    assert json.loads(SNAPSHOT.read_text(encoding="utf-8")) == current
