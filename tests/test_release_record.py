"""Strict validation of the public-release display record and its consistency with durable evidence.

`docs/status/public_release.json` is a projection of release facts consumed by the README pulse and
the Colab quickstart. These tests pin its schema and prove it agrees, field for field, with the
tracked release-verification report (`docs/reproducibility/RELEASE_VERIFICATION_v0.2.0.md`).
"""
import copy
import sys
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "tools"))
import release_record as RR  # noqa: E402

RECORD_PATH = _ROOT / "docs" / "status" / "public_release.json"
EVIDENCE = _ROOT / "docs" / "reproducibility" / "RELEASE_VERIFICATION_v0.2.0.md"


@pytest.fixture
def record():
    return RR.load(RECORD_PATH)


def test_shipped_record_is_valid(record):
    assert RR.validate(record) == []


def test_registry_status_is_github_only_not_pypi(record):
    assert record["registry_status"] == "github_only"


def test_record_matches_durable_verification_report(record):
    """Every identity-bearing field must appear verbatim in the durable evidence report."""
    text = EVIDENCE.read_text(encoding="utf-8")
    for field in ("version", "tag", "published_at", "source_commit", "annotated_tag_object",
                  "wheel_filename", "wheel_sha256", "sdist_filename", "sdist_sha256"):
        value = str(record[field])
        assert value in text, f"public_release.json {field}={value!r} not found in {EVIDENCE.name}"


def test_canonical_wheel_url_derives_from_release_url(record):
    url = RR.canonical_wheel_url(record)
    assert url == ("https://github.com/trbrewer/puckworks/releases/download/"
                   "v0.2.0/puckworks-0.2.0-py3-none-any.whl")
    assert url.startswith("https://")


# ── malformed-record rejection ────────────────────────────────────────────────────
def test_missing_field_rejected(record):
    bad = copy.deepcopy(record); del bad["wheel_sha256"]
    assert any("missing field" in p for p in RR.validate(bad))


def test_unknown_field_rejected(record):
    bad = copy.deepcopy(record); bad["surprise"] = 1
    assert any("unknown unsupported field" in p for p in RR.validate(bad))


@pytest.mark.parametrize("field,value,needle", [
    ("schema_version", "1", "schema_version"),          # wrong scalar type (str for int)
    ("manually_attached_asset_count", True, "manually_attached_asset_count"),  # bool-as-int
    ("manually_attached_asset_count", -1, "manually_attached_asset_count"),
    ("version", "0.2", "version is malformed"),
    ("source_commit", "abc123", "source_commit"),
    ("source_commit", "0A" + "b" * 38, "source_commit"),   # uppercase -> not lowercase hex
    ("annotated_tag_object", "xyz", "annotated_tag_object"),
    ("wheel_sha256", "deadbeef", "wheel_sha256"),
    ("sdist_sha256", "z" * 64, "sdist_sha256"),
    ("release_url", "http://example.com", "release_url must be HTTPS"),
    ("published_at", "2026-07-17 01:08:00", "published_at"),   # no offset / wrong format
    ("registry_status", "npm", "registry_status must be one of"),
])
def test_malformed_scalars_rejected(record, field, value, needle):
    bad = copy.deepcopy(record); bad[field] = value
    problems = RR.validate(bad)
    assert any(needle in p for p in problems), f"{field}={value!r} not rejected; got {problems}"


def test_load_validated_raises_on_bad(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"schema_version": 1}', encoding="utf-8")
    with pytest.raises(ValueError):
        RR.load_validated(p)
