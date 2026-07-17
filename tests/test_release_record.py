"""Strict semantic validation of the public-release display record + keyed durable-evidence check.

`docs/status/public_release.json` is a projection of release facts consumed by the README pulse and
the Colab quickstart. These tests pin its *semantic* schema (duplicate keys, strict-int versions,
real RFC 3339 timestamps, tag/version/URL binding, safe basenames, hash/count strictness) and prove
it agrees, field for field, with the tracked release-verification report.
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


def test_registry_status_is_github_only(record):
    assert record["registry_status"] == "github_only"


def test_canonical_urls(record):
    assert RR.canonical_wheel_url(record).endswith("v0.2.0/puckworks-0.2.0-py3-none-any.whl")
    assert RR.canonical_sdist_url(record).endswith("v0.2.0/puckworks-0.2.0.tar.gz")
    assert RR.canonical_wheel_url(record).startswith("https://")


# ── duplicate-key rejection ─────────────────────────────────────────────────────────
def test_duplicate_json_keys_rejected_before_validation():
    with pytest.raises(RR.DuplicateKeyError):
        RR.loads('{"schema_version":1,"schema_version":2,"version":"0.2.0"}')


# ── strict scalar rejection ─────────────────────────────────────────────────────────
@pytest.mark.parametrize("field,value,needle", [
    ("schema_version", True, "schema_version"),
    ("schema_version", 1.0, "schema_version"),
    ("schema_version", "1", "schema_version"),
    ("schema_version", None, "schema_version"),
    ("version", "0.2", "version is malformed"),
    ("tag", "0.2.0", "tag must equal"),
    ("published_at", "2026-13-40T25:61:61Z", "published_at"),
    ("published_at", "2026-02-30T10:00:00Z", "published_at"),
    ("published_at", "2026-07-17T10:00:00", "published_at"),   # no offset
    ("published_at", 12345, "non-empty string"),
    ("source_commit", "abc123", "source_commit"),
    ("source_commit", "0A" + "b" * 38, "source_commit"),
    ("annotated_tag_object", "xyz", "annotated_tag_object"),
    ("wheel_sha256", "deadbeef", "wheel_sha256"),
    ("sdist_sha256", "z" * 64, "sdist_sha256"),
    ("manually_attached_asset_count", -1, "manually_attached_asset_count"),
    ("manually_attached_asset_count", True, "manually_attached_asset_count"),
    ("registry_status", "npm", "registry_status"),
])
def test_malformed_scalars_rejected(record, field, value, needle):
    bad = copy.deepcopy(record)
    bad[field] = value
    problems = RR.validate(bad)
    assert any(needle in p for p in problems), f"{field}={value!r} not rejected; got {problems}"


# ── URL / repository binding ────────────────────────────────────────────────────────
@pytest.mark.parametrize("url", [
    "http://github.com/trbrewer/puckworks/releases/tag/v0.2.0",       # not https
    "https://github.com.evil.com/trbrewer/puckworks/releases/tag/v0.2.0",  # lookalike host
    "https://github.com/someoneelse/puckworks/releases/tag/v0.2.0",   # unrelated repo
    "https://github.com/trbrewer/puckworks/releases/v0.2.0",          # missing /tag/
    "https://user@github.com/trbrewer/puckworks/releases/tag/v0.2.0",  # user-info
    "https://github.com/trbrewer/puckworks/releases/tag/v0.2.0?x=1",   # query trick
])
def test_release_url_must_be_this_repo_tag(record, url):
    bad = copy.deepcopy(record)
    bad["release_url"] = url
    assert any("release_url must be exactly" in p for p in RR.validate(bad))


# ── filename safety + version binding ───────────────────────────────────────────────
@pytest.mark.parametrize("field,value", [
    ("wheel_filename", "../evil.whl"),
    ("wheel_filename", "sub/dir.whl"),
    ("wheel_filename", "puckworks-9.9.9-py3-none-any.whl"),   # version mismatch
    ("sdist_filename", "puckworks-0.2.0.tar.gz?a=1"),
    ("sdist_filename", "puckworks-9.9.9.tar.gz"),
])
def test_unsafe_or_mismatched_filenames_rejected(record, field, value):
    bad = copy.deepcopy(record)
    bad[field] = value
    assert RR.validate(bad), f"{field}={value!r} should be rejected"


# ── field-set policy ────────────────────────────────────────────────────────────────
def test_missing_field_rejected(record):
    bad = copy.deepcopy(record)
    del bad["wheel_sha256"]
    assert any("missing field" in p for p in RR.validate(bad))


def test_unknown_field_rejected_but_x_extension_allowed(record):
    bad = copy.deepcopy(record)
    bad["surprise"] = 1
    assert any("unknown unsupported field" in p for p in RR.validate(bad))
    ok = copy.deepcopy(record)
    ok["x_extra"] = "documented extension"
    assert RR.validate(ok) == []


# ── keyed durable-evidence cross-check (3B) ─────────────────────────────────────────
def test_record_matches_durable_evidence_by_key(record):
    ev = RR.parse_evidence_report(EVIDENCE.read_text(encoding="utf-8"))
    assert RR.cross_check(record, ev) == []


def test_swapped_wheel_sdist_hashes_are_caught_by_keyed_check(record):
    """Swapping wheel/sdist hashes must fail even though both values still appear in the file."""
    ev = RR.parse_evidence_report(EVIDENCE.read_text(encoding="utf-8"))
    swapped = copy.deepcopy(record)
    swapped["wheel_sha256"], swapped["sdist_sha256"] = record["sdist_sha256"], record["wheel_sha256"]
    problems = RR.cross_check(swapped, ev)
    assert any("wheel_sha256 disagrees" in p for p in problems)
    assert any("sdist_sha256 disagrees" in p for p in problems)


def test_evidence_parser_rejects_conflicting_labels():
    bad = "| package version | 0.2.0 |\n| package version | 9.9.9 |\n"
    with pytest.raises(ValueError):
        RR.parse_evidence_report(bad)


def test_load_validated_raises_on_bad(tmp_path):
    p = tmp_path / "bad.json"
    p.write_text('{"schema_version": 1}', encoding="utf-8")
    with pytest.raises(ValueError):
        RR.load_validated(p)
