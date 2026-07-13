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
    assert counts["jfe"]["abstract_words"] == 237
    assert counts["jfe"]["highlight_count"] == 5
    assert counts["aps_dfd_2026"]["body_plus_funding_characters"] == 1944
