"""Registry schema v2 tests (WP2.1): the typed execution_role / provenance_class /
evidence_strength axes, back-fill migration from the legacy `kind`, and enum validation."""
import pytest

import puckworks.models  # noqa: F401  (triggers registration of all components)
from puckworks import registry as R


def test_kind_migration_derivations():
    assert R._derive_execution_role("runtime") == "runtime"
    assert R._derive_execution_role("calibration") == "calibration"
    assert R._derive_execution_role("synthesis") == "runtime"      # synthesis still runs
    assert R._derive_provenance_class("brewer2026.x", "runtime") == "project_model"
    assert R._derive_provenance_class("sourcing2026.g1", "calibration") == "reference_only"
    assert R._derive_provenance_class("foster2025.machine_mode", "runtime") == "published_port"
    assert R._derive_provenance_class("anything", "synthesis") == "project_synthesis"


def test_all_registered_components_have_valid_typed_axes():
    comps = R.components()
    assert len(comps) >= 25
    for c in comps:
        assert c.execution_role in R.EXECUTION_ROLES, (c.name, c.execution_role)
        assert c.provenance_class in R.PROVENANCE_CLASSES, (c.name, c.provenance_class)
        assert c.kind                                    # legacy field preserved (back-compat)


def test_synthesis_component_migrated():
    syn = R.get("brewer2026.coupled_kappa_t")
    assert syn.kind == "synthesis"
    assert syn.execution_role == "runtime"
    assert syn.provenance_class == "project_synthesis"


def test_registry_is_fully_classified():
    # every component now carries a card-driven evidence_strength -> validate_registry clean.
    assert R.validate_registry() == []
    for c in R.components():
        assert c.evidence_strength in R.EVIDENCE_STRENGTHS, (c.name, c.evidence_strength)


def test_register_rejects_duplicate_and_bad_enums():
    dup = R.Component(name="foster2025.machine_mode", stage="machine", kind="runtime",
                      paper="x")
    with pytest.raises(ValueError, match="duplicate"):
        R.register(dup)
    bad = R.Component(name="__test_bad_enum__", stage="flow", kind="runtime", paper="x",
                      evidence_strength="totally_proven")
    with pytest.raises(AssertionError):
        R.register(bad)
    R._REGISTRY.pop("__test_bad_enum__", None)           # keep the global registry clean


def test_explicit_axes_are_not_overwritten_by_migration():
    c = R.Component(name="__test_adapter__", stage="observables", kind="runtime", paper="x",
                    execution_role="observational_adapter", provenance_class="project_model",
                    evidence_strength="code_verification")
    try:
        R.register(c)
        got = R.get("__test_adapter__")
        assert got.execution_role == "observational_adapter"     # not overwritten to 'runtime'
        assert got.evidence_strength == "code_verification"
    finally:
        R._REGISTRY.pop("__test_adapter__", None)
