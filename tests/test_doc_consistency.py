"""PW-DOC-001 — guard doc/version claims against drift.

The lab module header once said "Schema v4" while SCHEMA_VERSION had moved to 5, and the product
header claimed the v0.2.0 wheel with "no orchestration" while it exports Guided Pull. These tests
fail if a documented schema number or capability claim drifts from the code again.
"""
import inspect
import re


def test_lab_header_schema_number_matches_implementation():
    from puckworks.product import lab
    m = re.search(r"Schema v(\d+)", inspect.getdoc(lab) or "")
    assert m, "lab module docstring must state its schema version as 'Schema vN'"
    assert int(m.group(1)) == lab.SCHEMA_VERSION, (
        "lab docstring 'Schema v%s' != SCHEMA_VERSION %s" % (m.group(1), lab.SCHEMA_VERSION))


def test_product_header_does_not_claim_orchestration_is_absent():
    import puckworks.product as product
    doc = inspect.getdoc(product) or ""
    # the module DOES export the Guided Pull orchestration; the header must not deny it
    assert "simulate_pull" in product.__all__
    assert "no orchestration" not in doc.lower()
    assert "v0.2.0 wheel does" not in doc      # stale specific-version claim removed
