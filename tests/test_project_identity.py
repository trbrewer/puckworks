"""Project-identity regression guard (Workstream 1): the tracked tree carries no former corporate
contact/affiliation, and CITATION.cff stays valid.

Deterministic + offline: it enumerates tracked files via ``git ls-files`` (so untracked build/output
and ``.git`` are naturally excluded), reads each text file, and rejects the old maintainer email and
the corporate "Synthetik" brand — case-insensitively. The ordinary scientific word ``synthetic`` is
explicitly preserved (it must NOT be rejected). This module names the forbidden strings on purpose, so
it excludes itself from the scan.
"""
import re
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
OLD_EMAIL = "brewer@synthetik-technologies.com"
NEW_EMAIL = "t_r_brewer@hotmail.com"
# corporate brand + old email — NOT the scientific word 'synthetic' (ends in 'c', not 'k')
_FORBIDDEN = re.compile(r"brewer@synthetik-technologies\.com|synthetik", re.I)
_SYNTHETIC = re.compile(r"\bsynthetic\b", re.I)
_THIS = Path(__file__).name


def _tracked_text_files():
    files = subprocess.check_output(["git", "-C", str(_ROOT), "ls-files"], text=True).splitlines()
    out = []
    for f in files:
        p = _ROOT / f
        try:
            raw = p.read_bytes()
        except OSError:
            continue
        if b"\x00" in raw[:4096]:          # skip binary
            continue
        out.append((f, raw.decode("utf-8", errors="replace")))
    return out


def test_no_old_email_or_corporate_brand_in_tracked_tree():
    offenders = []
    for f, text in _tracked_text_files():
        if Path(f).name == _THIS:          # this guard names the forbidden strings on purpose
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if _FORBIDDEN.search(line):
                offenders.append(f"{f}:{i}: {line.strip()[:160]}")
    assert not offenders, ("former corporate contact/brand present in the tracked tree:\n"
                           + "\n".join(offenders))


def test_scientific_synthetic_is_preserved_and_never_flagged():
    # the guard must NOT reject the scientific word 'synthetic'
    for phrase in ("synthetic dataset", "synthetic puck", "synthetic observation",
                   "synthetic pack", "a synthetic provenance test"):
        assert not _FORBIDDEN.search(phrase), f"'synthetic' wrongly flagged: {phrase}"
    # and it is still genuinely present in the tree (we did not scrub scientific terminology)
    hits = sum(1 for _, t in _tracked_text_files() if _SYNTHETIC.search(t))
    assert hits > 0, "scientific 'synthetic' terminology unexpectedly absent"


def test_citation_carries_new_contact_not_old():
    # yaml-free (runs even on the core-only min-deps lane): the contact metadata is correct
    text = (_ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert NEW_EMAIL in text, f"CITATION.cff must carry {NEW_EMAIL}"
    assert OLD_EMAIL not in text


def test_citation_is_valid_yaml_when_available():
    # structural validation via the dev/radar pyyaml extra; skipped when pyyaml is absent
    # (pyyaml is not a core runtime dependency)
    import pytest
    yaml = pytest.importorskip("yaml")
    data = yaml.safe_load((_ROOT / "CITATION.cff").read_text(encoding="utf-8"))
    assert str(data.get("cff-version", "")).strip(), "CITATION.cff missing cff-version"
    emails = [a.get("email") for a in data.get("authors", [])]
    assert NEW_EMAIL in emails, f"CITATION.cff author email is not {NEW_EMAIL}"
    assert OLD_EMAIL not in emails


def test_independence_statement_present_without_naming_former_company():
    # collapse whitespace so a wrapped statement still matches
    readme = re.sub(r"\s+", " ", (_ROOT / "README.md").read_text(encoding="utf-8").lower())
    assert "independently developed" in readme
    assert "not affiliated with or sponsored by any employer or company" in readme
    assert "synthetik" not in readme                      # the former company is not named
