"""P1.5 — the supported public API surface. Any change to __all__ must be deliberate (a change
here is a semantic-versioning event per docs/API.md)."""
import puckworks

_EXPECTED_PUBLIC = {
    "__version__",
    "contracts", "registry", "validate", "product",
    "Component", "components", "get", "load_builtin_components",
    "evaluate_all_gates", "GateStatus", "GateResult", "GateSuiteResult",
}


def test_public_api_is_exactly_the_supported_set():
    assert set(puckworks.__all__) == _EXPECTED_PUBLIC        # deliberate change only


def test_every_public_symbol_is_accessible():
    for name in puckworks.__all__:
        assert hasattr(puckworks, name), name


def test_supported_surface_works():
    puckworks.load_builtin_components()
    comps = puckworks.components()
    assert len(comps) >= 25 and all(isinstance(c, puckworks.Component) for c in comps)
    assert puckworks.get(comps[0].name).name == comps[0].name
    assert puckworks.GateStatus.PASS.value == "PASS"
    assert puckworks.validate.bar_gauge_to_pa(9.0) == 9.0e5   # public units helper


def test_internal_modules_are_not_advertised_as_public():
    # research/release internals may be importable but must NOT be in the supported surface
    for internal in ("harness", "analysis", "paper3", "paper_a", "paper_b", "figures", "lib",
                     "viz", "inventory", "release", "statusdoc"):
        assert internal not in puckworks.__all__


def test_versioned_schemas_expose_a_schema_version():
    from puckworks import contracts, registry, validate
    from puckworks.gate_runner import SCHEMA_VERSION as gate_schema
    assert contracts.SCHEMA_VERSION and registry.SCHEMA_VERSION
    assert validate.TRACE_SCHEMA_VERSION and gate_schema
