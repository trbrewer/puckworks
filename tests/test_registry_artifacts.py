"""Paper 3 generated-artifact reconciliation (WP2.4).

The committed Paper 3 registry artifacts must be producer-generated and never hand-edited:
generation is deterministic, the committed files must be up to date, and Table 1 / Appendix A
/ counts must reconcile with the live registry.
"""
import json

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import registry_artifacts as gen


def test_generation_is_deterministic():
    assert gen.generate() == gen.generate()


def test_committed_artifacts_are_not_stale():
    # regenerating from the live registry must match what is committed on disk -> a registry
    # change without regeneration fails CI (no hand-edited or stale tables).
    stale = gen.verify()
    assert stale == [], "stale Paper 3 artifacts (run `python -m puckworks.paper3.registry_artifacts --write`): %r" % stale


def test_export_reconciles_with_live_registry():
    arts = gen.generate()
    export = json.loads(arts["registry_export.json"])
    comps = R.components()
    assert export["n_components"] == len(comps)
    assert {c["id"] for c in export["components"]} == {c.name for c in comps}
    # every exported component carries the typed axes
    for row in export["components"]:
        assert row["execution_role"] in R.EXECUTION_ROLES
        assert row["provenance_class"] in R.PROVENANCE_CLASSES
    # the content hash embedded in the export is self-consistent
    body = {k: export[k] for k in export if k != "content_sha256"}
    assert gen._sha(json.dumps(body, sort_keys=True, ensure_ascii=False)) == export["content_sha256"]


def test_table1_and_counts_match_registry():
    arts = gen.generate()
    counts = json.loads(arts["registry_counts.json"])
    comps = R.components()
    assert counts["n_components"] == len(comps)
    assert sum(counts["by_stage"].values()) == len(comps)
    assert sum(counts["by_execution_role"].values()) == len(comps)
    # Table 1 total row equals the component count
    assert ("| **Total** |" in arts["table1_registry_overview.md"])
    assert ("| %d |" % len(comps)) in arts["table1_registry_overview.md"]


def test_measurement_dictionary_render_reconciles(tmp_path):
    from puckworks.data.visualizer_store import MEASUREMENT_DICTIONARY
    arts = gen.generate()
    dj = json.loads(arts["measurement_dictionary.json"])
    assert dj["n_channels"] == len(MEASUREMENT_DICTIONARY)
    assert set(dj["channels"]) == set(MEASUREMENT_DICTIONARY)
    # the native (ambiguous) flow channels are marked non-SI in the render
    assert "flow_reported__native" in arts["measurement_dictionary.md"]
    assert "— (native)" in arts["measurement_dictionary.md"]


def test_appendix_a_has_no_manual_rows():
    # Appendix A is exactly the generated catalog; a committed file differing from the
    # producer output is caught by test_committed_artifacts_are_not_stale. Here we assert the
    # generated Appendix contains one row per registered component id.
    md = gen.generate()["appendixA_component_catalog.md"]
    for c in R.components():
        assert ("`%s`" % c.name) in md
