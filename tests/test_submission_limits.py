from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_validator():
    path = Path(__file__).resolve().parents[1] / "tools/validate_submission_limits.py"
    spec = importlib.util.spec_from_file_location("validate_submission_limits", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_submission_text_is_within_declared_limits() -> None:
    validator = _load_validator()
    ok, failures, counts = validator.validate()
    assert ok, failures
    # Third review P0-1/MC1: the abstract was rewritten (313 -> 238 words) and the Highlights
    # reduced from five repository-facing bullets to four accessible ones. Both are now GENERATED
    # from `docs/submission/paper_a_front_matter.yaml`, so the expected values are read from that
    # single source rather than duplicated here -- duplicating them is what let the package drift
    # from the manuscript in the first place.
    import yaml
    fm = yaml.safe_load(
        (Path(__file__).resolve().parents[1]
         / "docs/submission/paper_a_front_matter.yaml").read_text(encoding="utf-8"))
    assert counts["jfe"]["abstract_words"] == len(" ".join(fm["abstract"].split()).split())
    assert counts["jfe"]["highlight_count"] == len(fm["highlights"])
    assert counts["aps_dfd_2026"]["body_plus_funding_characters"] == 1944
