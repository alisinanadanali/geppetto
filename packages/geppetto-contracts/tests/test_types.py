"""`geppetto_contracts.types` domain tiplerini kopyalamaz, aynı nesneyi verir (karar K1)."""

import geppetto_contracts.types as contract_types
import geppetto_domain.enums as domain_enums
import geppetto_domain.units as domain_units


def test_reexports_are_identical_objects() -> None:
    for name in contract_types.__all__:
        source = getattr(domain_enums, name, None) or getattr(domain_units, name)
        assert getattr(contract_types, name) is source, name


def test_todo_2_2_types_are_exported() -> None:
    required = {
        "Micron",
        "Money",
        "MaterialType",
        "Rotation",
        "Grain",
        "EdgeRef",
        "FaceRef",
        "MovementType",
        "DimensionBasis",
    }
    assert required <= set(contract_types.__all__)
