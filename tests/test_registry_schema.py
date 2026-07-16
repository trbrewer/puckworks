"""Registry schema v2 tests (WP2.1 / P1.2): the typed execution_role / provenance_class /
evidence_strength axes are AUTHORITATIVE and explicit (no name-prefix inference), immutable public
snapshots, an explicit loader, and enum validation."""
import json
from pathlib import Path

import pytest

import puckworks.models  # noqa: F401  (triggers registration of all components)
from puckworks import registry as R

_GOLDEN = Path(__file__).resolve().parent / "data" / "registry_metadata_golden.json"


def test_execution_role_derives_from_kind_not_name():
    # execution_role is a documented kind map (NOT name-prefix); provenance is no longer inferred
    assert R._derive_execution_role("runtime") == "runtime"
    assert R._derive_execution_role("synthesis") == "runtime"
    assert not hasattr(R, "_derive_provenance_class")     # name-prefix inference removed


def test_all_registered_components_have_valid_typed_axes():
    comps = R.components()
    assert len(comps) >= 25
    for c in comps:
        assert c.execution_role in R.EXECUTION_ROLES, (c.name, c.execution_role)
        assert c.provenance_class in R.PROVENANCE_CLASSES, (c.name, c.provenance_class)
        assert c.kind                                    # legacy field preserved (back-compat)


def test_metadata_matches_the_committed_golden():
    """The authoritative per-component metadata is locked — any change to a tier/role/provenance
    must be a deliberate golden update (and, for a tier, a ROADMAP §7.1 entry)."""
    got = {c.name: {"stage": c.stage, "execution_role": c.execution_role,
                    "provenance_class": c.provenance_class,
                    "evidence_strength": c.evidence_strength}
           for c in sorted(R.components(), key=lambda c: c.name)}
    golden = json.loads(_GOLDEN.read_text())
    assert got == golden, "registry metadata drifted from the golden; update it deliberately"


def test_schema_version_present():
    assert R.SCHEMA_VERSION == 2


def test_public_snapshots_are_immutable():
    c = R.get("cameron2020.extraction_bdf")
    assert isinstance(c.gates, tuple)                    # read-only gate collection
    c.provenance_class = "HACKED"                        # mutate the snapshot...
    assert R.get("cameron2020.extraction_bdf").provenance_class == "published_port"  # ...no effect


def test_finalize_registry_requires_provenance():
    from puckworks.registry import Component
    tmp = Component(name="__test_no_prov__", stage="flow", kind="runtime", paper="x")
    try:
        R.register(tmp)                                  # provenance_class deliberately unset
        assert R._REGISTRY["__test_no_prov__"].provenance_class is None
        with pytest.raises(ValueError, match="provenance_class .* not assigned"):
            R.finalize_registry()
    finally:
        R._REGISTRY.pop("__test_no_prov__", None)


def test_load_builtin_components_is_idempotent():
    n1 = R.load_builtin_components()
    n2 = R.load_builtin_components()
    assert n1 == n2 >= 25                                 # no double-registration


def test_synthesis_component_metadata():
    syn = R.get("brewer2026.coupled_kappa_t")
    assert syn.kind == "synthesis" and syn.execution_role == "runtime"
    assert syn.provenance_class == "project_synthesis"


def test_registry_is_fully_classified():
    assert R.validate_registry() == []
    for c in R.components():
        assert c.evidence_strength in R.EVIDENCE_STRENGTHS, (c.name, c.evidence_strength)


def test_register_rejects_duplicate_and_bad_enums():
    with pytest.raises(ValueError, match="duplicate"):
        R.register(R.Component(name="foster2025.machine_mode", stage="machine", kind="runtime",
                               paper="x"))
    bad = R.Component(name="__test_bad_enum__", stage="flow", kind="runtime", paper="x",
                      evidence_strength="totally_proven")
    with pytest.raises(ValueError, match="bad evidence_strength"):
        R.register(bad)
    R._REGISTRY.pop("__test_bad_enum__", None)
