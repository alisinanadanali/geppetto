"""Kanonik birim tipleri: µm tam sayı zorunluluğu ve Money (ADR-0002, ADR-0010; todo 2.4)."""

import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from geppetto_domain.enums import DimensionBasis, EdgeRef
from geppetto_domain.units import (
    MAX_SAFE_INT,
    Micron,
    Money,
    NonNegativeMicron,
    PositiveMicron,
)

MICRON = TypeAdapter(Micron)
POSITIVE = TypeAdapter(PositiveMicron)
NON_NEGATIVE = TypeAdapter(NonNegativeMicron)


@pytest.mark.parametrize("value", [0, 18000, -4000, MAX_SAFE_INT, -MAX_SAFE_INT])
def test_micron_accepts_int(value: int) -> None:
    assert MICRON.validate_python(value) == value
    assert MICRON.validate_json(str(value)) == value


@pytest.mark.parametrize("value", [18.0, 18000.5, "18000", True, None])
def test_micron_rejects_non_int_python(value: object) -> None:
    with pytest.raises(ValidationError):
        MICRON.validate_python(value)


@pytest.mark.parametrize("raw", ["18000.0", "18.5", '"18000"', "true", "null"])
def test_micron_rejects_non_int_json(raw: str) -> None:
    with pytest.raises(ValidationError):
        MICRON.validate_json(raw)


@pytest.mark.parametrize("value", [MAX_SAFE_INT + 1, -MAX_SAFE_INT - 1])
def test_micron_rejects_unsafe_integer(value: int) -> None:
    with pytest.raises(ValidationError):
        MICRON.validate_python(value)


def test_positive_and_non_negative_bounds() -> None:
    with pytest.raises(ValidationError):
        POSITIVE.validate_python(0)
    assert NON_NEGATIVE.validate_python(0) == 0
    with pytest.raises(ValidationError):
        NON_NEGATIVE.validate_python(-1)


def test_money_valid_and_frozen() -> None:
    money = Money(minor=125050, currency="TRY")
    assert Money.model_validate_json('{"minor": 125050, "currency": "TRY"}') == money
    with pytest.raises(ValidationError):
        money.minor = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    "payload",
    [
        {"minor": 12.5, "currency": "TRY"},
        {"minor": "1250", "currency": "TRY"},
        {"minor": 1250, "currency": "try"},
        {"minor": 1250, "currency": "TL"},
        {"minor": 1250, "currency": "TRYY"},
        {"minor": 1250},
        {"minor": 1250, "currency": "TRY", "rate": 1},
    ],
)
def test_money_rejects_invalid(payload: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        Money.model_validate(payload)


def test_enums_are_case_sensitive() -> None:
    class Holder(BaseModel):
        basis: DimensionBasis
        edge: EdgeRef

    assert Holder.model_validate({"basis": "RAW", "edge": "W2"}).edge is EdgeRef.W2
    for payload in ({"basis": "raw", "edge": "W2"}, {"basis": "RAW", "edge": "w2"}):
        with pytest.raises(ValidationError):
            Holder.model_validate(payload)
