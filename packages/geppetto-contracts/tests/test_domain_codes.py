"""Domain hata sabitleri contracts kataloğunda olmalı (karar K3, 2026-09-15).

Domain contracts'ı import edemez (ADR-0001); kodlarını `geppetto_domain.errors` içinde
modül düzeyi `str` sabiti olarak tutar. Bu test yazım hatasının sessiz kalmasını engeller.
"""

import pytest

import geppetto_domain.errors as domain_errors
from geppetto_contracts.error_codes import ALLOWED_PREFIXES, ErrorCode


def _domain_code_constants() -> dict[str, str]:
    return {
        name: value
        for name, value in vars(domain_errors).items()
        if name.isupper() and name.startswith(ALLOWED_PREFIXES) and isinstance(value, str)
    }


def _check(constants: dict[str, str]) -> None:
    for name, value in constants.items():
        assert name == value, f"{name} sabitinin değeri adıyla aynı olmalı"
        assert value in ErrorCode.__members__, f"{value} contracts kataloğunda yok"


def test_domain_code_constants_exist_in_catalog() -> None:
    constants = _domain_code_constants()
    if not constants:
        pytest.skip("geppetto_domain.errors henüz kod sabiti içermiyor (todo bölüm 3)")
    _check(constants)


def test_checker_catches_typo(monkeypatch: pytest.MonkeyPatch) -> None:
    """Denetimin kendisi çalışıyor mu: katalogda olmayan ve adıyla uyuşmayan sabit yakalanır."""
    monkeypatch.setattr(
        domain_errors, "PART_RAW_DIM_NON_POSITIVE", "PART_RAW_DIM_NON_POSITIVE", raising=False
    )
    with pytest.raises(AssertionError, match="kataloğunda yok"):
        _check(_domain_code_constants())
    monkeypatch.delattr(domain_errors, "PART_RAW_DIM_NON_POSITIVE")
    monkeypatch.setattr(domain_errors, "PART_EXCEEDS_SHEET", "PART_EXCEEDS_SHEETS", raising=False)
    with pytest.raises(AssertionError, match="adıyla aynı"):
        _check(_domain_code_constants())
