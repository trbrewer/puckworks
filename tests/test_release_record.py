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
# The durable verification record and the release facts are derived from the SHIPPED record version,
# so this suite follows the release transition (v0.2.0 -> v0.3.0 -> ...) without hard-coded versions.
_SHIPPED = RR.load(RECORD_PATH)
VERSION = _SHIPPED["version"]
EVIDENCE = _ROOT / "docs" / "reproducibility" / f"RELEASE_VERIFICATION_v{VERSION}.md"


@pytest.fixture
def record():
    return RR.load(RECORD_PATH)


def test_shipped_record_is_valid(record):
    assert RR.validate(record) == []


def test_durable_evidence_record_exists_for_shipped_version():
    assert EVIDENCE.exists(), f"missing durable verification record for v{VERSION}: {EVIDENCE}"


def test_registry_status_is_github_only(record):
    assert record["registry_status"] == "github_only"


def test_canonical_urls(record):
    # derived from record fields, not literal version strings
    assert RR.canonical_wheel_url(record).endswith(f"{record['tag']}/{record['wheel_filename']}")
    assert RR.canonical_sdist_url(record).endswith(f"{record['tag']}/{record['sdist_filename']}")
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


# ══════════════════════════════════════════════════════════════════════════════════
# 2A/2B/2C/2D remediation: fail-closed PyPI, full live identity, composite, dup rows
# ══════════════════════════════════════════════════════════════════════════════════


def _fake_gh(record, overrides=None):
    overrides = overrides or {}
    n = record["manually_attached_asset_count"]
    assets = [{"name": record["wheel_filename"], "size": 100},
              {"name": record["sdist_filename"], "size": 200}]
    assets += [{"name": f"asset{i}.txt", "size": 1} for i in range(n - 2)]
    rel = {"tag_name": record["tag"], "html_url": record["release_url"], "draft": False,
           "prerelease": False, "published_at": record["published_at"], "assets": assets}
    rel.update(overrides.get("rel", {}))
    ref = overrides.get("ref", {"object": {"type": "tag", "sha": record["annotated_tag_object"]}})
    tagobj = overrides.get("tagobj", {"object": {"type": "commit", "sha": record["source_commit"]}})

    def gh(path):
        if path.startswith("releases/tags/"):
            return rel
        if path.startswith("git/ref/tags/"):
            return ref
        if path.startswith("git/tags/"):
            return tagobj
        raise KeyError(path)
    return gh


def _fake_stream(record, wheel_sha=None, sdist_sha=None, wheel_size=100, sdist_size=200):
    def stream(url):
        if url.endswith(".whl"):
            return (wheel_sha or record["wheel_sha256"], wheel_size)
        return (sdist_sha or record["sdist_sha256"], sdist_size)
    return stream


def _fake_pypi(status=404, cat="absent"):
    return lambda repo: (status, cat)


# ── 2A fail-closed PyPI ──────────────────────────────────────────────────────────
@pytest.mark.parametrize("status,cat,absent", [
    (404, "absent", True),
    (200, "present", False),
    (403, "http_403", False),
    (429, "http_429", False),
    (500, "http_500", False),
    (None, "transport_URLError", False),
    (None, "transport_TimeoutError", False),
    (None, "error_JSONDecodeError", False),
    (301, "unexpected_301", False),
])
def test_pypi_classifier_fail_closed(status, cat, absent):
    got_absent, _disp = RR.classify_pypi_absence(status, cat)
    assert got_absent is absent


def test_verify_live_fails_closed_when_pypi_uncertain(record):
    gh = _fake_gh(record)
    for status, cat in [(None, "transport_URLError"), (500, "http_500"), (200, "present")]:
        with pytest.raises(ValueError, match="affirmative PyPI 404"):
            RR.verify_live(RECORD_PATH, gh_json=gh, stream=_fake_stream(record),
                           pypi_probe=_fake_pypi(status, cat))


def test_verify_live_passes_only_on_affirmative_404(record):
    ev = RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record), stream=_fake_stream(record),
                        pypi_probe=_fake_pypi(404, "absent"))
    assert ev["verified"] and ev["pypi_disposition"] == "absent_404"


# ── 2B live identity binding ─────────────────────────────────────────────────────
@pytest.mark.parametrize("overrides,needle", [
    ({"rel": {"html_url": "https://github.com/trbrewer/puckworks/releases/tag/v9"}}, "html_url"),
    ({"rel": {"published_at": "2000-01-01T00:00:00Z"}}, "published_at"),
    ({"rel": {"draft": True}}, "draft"),
    ({"rel": {"prerelease": True}}, "prerelease"),
    ({"ref": {"object": {"type": "commit", "sha": "0" * 40}}}, "lightweight"),
    ({"ref": {"object": {"type": "tag", "sha": "0" * 40}}}, "annotated_tag_object"),
    ({"tagobj": {"object": {"type": "tag", "sha": "0" * 40}}}, "peel to a commit"),
    ({"tagobj": {"object": {"type": "commit", "sha": "0" * 40}}}, "source_commit"),
])
def test_verify_live_binds_identity(record, overrides, needle):
    with pytest.raises(ValueError, match=needle):
        RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record, overrides),
                       stream=_fake_stream(record), pypi_probe=_fake_pypi())


def test_verify_live_catches_asset_and_hash_faults(record):
    # missing expected asset
    ov = {"rel": {"assets": [{"name": "other.txt", "size": 1}] * record["manually_attached_asset_count"]}}
    with pytest.raises(ValueError, match="missing from release"):
        RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record, ov), stream=_fake_stream(record),
                       pypi_probe=_fake_pypi())
    # wheel hash mismatch
    with pytest.raises(ValueError, match="wheel SHA-256 mismatch"):
        RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record),
                       stream=_fake_stream(record, wheel_sha="0" * 64), pypi_probe=_fake_pypi())
    # reported size vs streamed size
    with pytest.raises(ValueError, match="reported-size"):
        RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record),
                       stream=_fake_stream(record, wheel_size=999), pypi_probe=_fake_pypi())


def test_verify_live_duplicate_asset_name(record):
    dup = [{"name": record["wheel_filename"], "size": 100}] * record["manually_attached_asset_count"]
    with pytest.raises(ValueError, match="duplicate asset"):
        RR.verify_live(RECORD_PATH, gh_json=_fake_gh(record, {"rel": {"assets": dup}}),
                       stream=_fake_stream(record), pypi_probe=_fake_pypi())


# ── 2C composite ─────────────────────────────────────────────────────────────────
def test_verify_all_offline_passes(record):
    res = RR.verify_all(RECORD_PATH, EVIDENCE, live=False)
    assert res["layers"] == ["schema", "cross_check"]


def test_verify_all_fails_on_conflicting_durable_evidence(tmp_path):
    bad = tmp_path / "ev.md"
    bad.write_text("| package version | 9.9.9 |\n"
                   "| `puckworks-0.2.0-py3-none-any.whl` | " + "a" * 64 + " |\n"
                   "| `puckworks-0.2.0.tar.gz` | " + "b" * 64 + " |\n", encoding="utf-8")
    with pytest.raises(ValueError):
        RR.verify_all(RECORD_PATH, bad, live=False)


def test_verify_all_live_fails_when_live_fails(record):
    with pytest.raises(ValueError):
        RR.verify_all(RECORD_PATH, EVIDENCE, live=True, gh_json=_fake_gh(record),
                      stream=_fake_stream(record), pypi_probe=_fake_pypi(500, "http_500"))


# ── 2D duplicate/ambiguous artifact rows ─────────────────────────────────────────
def test_parser_rejects_duplicate_conflicting_wheel_rows():
    txt = ("| `puckworks-0.2.0-py3-none-any.whl` | " + "a" * 64 + " |\n"
           "| `puckworks-0.2.0-py3-none-any.whl` | " + "b" * 64 + " |\n"
           "| `puckworks-0.2.0.tar.gz` | " + "c" * 64 + " |\n")
    with pytest.raises(ValueError, match="ambiguous/duplicate"):
        RR.parse_evidence_report(txt)


def test_parser_rejects_multiple_shas_in_one_row():
    txt = ("| `puckworks-0.2.0-py3-none-any.whl` | " + "a" * 64 + " | " + "b" * 64 + " |\n")
    with pytest.raises(ValueError, match="exactly 1"):
        RR.parse_evidence_report(txt)


def test_parser_requires_both_artifacts():
    with pytest.raises(ValueError, match="missing sdist"):
        RR.parse_evidence_report("| `puckworks-0.2.0-py3-none-any.whl` | " + "a" * 64 + " |\n")
