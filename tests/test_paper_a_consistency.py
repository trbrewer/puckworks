"""Tests for the Paper A manuscript-consistency verifier (Paper 1 review MC1).

Offline + deterministic. Confirms the verifier passes on the current tree (the JFE conversion is in
sync with the canonical working draft) and that each drift it is meant to catch actually fails it.
"""
import importlib
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
PC = importlib.import_module("tools.paper_a_consistency")


def test_verify_passes_on_current_tree():
    # After the 2026-07-24 mechanical sync, the conversion carries no retired phrase and all corrected ones.
    assert PC.check_paper_a() == []


def test_banned_phrases_are_absent_from_the_canonical_draft():
    # Config sanity: every banned phrase must be genuinely retired (absent from the source of truth),
    # otherwise the guard gives false confidence.
    canonical = PC.CANONICAL.read_text(encoding="utf-8").lower()
    for phrase, _why in PC.BANNED_IN_CONVERSION:
        assert phrase.lower() not in canonical, f"banned phrase «{phrase}» is present in the canonical draft"


def test_required_phrases_present_in_canonical_draft():
    canonical = PC.CANONICAL.read_text(encoding="utf-8").lower()
    for phrase, _why in PC.REQUIRED_IN_CONVERSION:
        assert phrase.lower() in canonical, f"required phrase «{phrase}» missing from the canonical draft"


def test_drift_is_caught(tmp_path, monkeypatch):
    # Reintroducing a retired phrase into the conversion must fail the check.
    good = PC.CONVERSION.read_text(encoding="utf-8")
    drifted = good + "\n\nThe fitted rate gives an identifiability ratio that means the rate is identified.\n"
    fake = tmp_path / "conv.md"
    fake.write_text(drifted, encoding="utf-8")
    monkeypatch.setattr(PC, "CONVERSION", fake)
    problems = PC.check_paper_a()
    assert any("identifiability ratio" in p for p in problems)


def test_missing_corrected_phrase_is_caught(tmp_path, monkeypatch):
    # Dropping a corrected phrase from the conversion must fail the check.
    stripped = PC.CONVERSION.read_text(encoding="utf-8").replace("profile range ratio", "profile something")
    fake = tmp_path / "conv.md"
    fake.write_text(stripped, encoding="utf-8")
    monkeypatch.setattr(PC, "CONVERSION", fake)
    problems = PC.check_paper_a()
    assert any("profile range ratio" in p for p in problems)
