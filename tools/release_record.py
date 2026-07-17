#!/usr/bin/env python3
"""Strict loader/validator for the public-release display record (docs/status/public_release.json).

This record is a compact, machine-readable **projection of durable release facts** for
public-experience tooling (the README project-pulse and the Colab quickstart). It is NOT a
project-status authority — current project work is governed by ``docs/status/current.json`` and the
generated ``STATE_OF_TRUTH.md``; historical release verification is governed by
``docs/reproducibility/RELEASE_VERIFICATION_v0.2.0.md``.

Validation is **semantic, not merely syntactic**: it rejects duplicate JSON keys, non-integer /
bool schema versions, impossible RFC 3339 timestamps, tag/version disagreement, a release URL that
is not this repo's tag URL, unsafe artifact basenames, malformed hashes/counts, and unknown fields
(only documented ``x_`` extensions are permitted).

Commands:
    python tools/release_record.py               # strict offline validation of the shipped record
    python tools/release_record.py --verify-live  # + verify against the live GitHub release + PyPI
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

SCHEMA_VERSION = 1
OWNER = "trbrewer"
REPO = "puckworks"

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_VERSION = re.compile(r"^\d+\.\d+\.\d+([.-][0-9A-Za-z.]+)?$")
_RFC3339 = re.compile(r"^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}:\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})$")
_REGISTRY_STATES = ("github_only", "pypi", "test_pypi", "other")

REQUIRED_FIELDS = (
    "schema_version", "version", "tag", "release_url", "published_at", "source_commit",
    "annotated_tag_object", "wheel_filename", "wheel_sha256", "sdist_filename", "sdist_sha256",
    "manually_attached_asset_count", "registry_status",
)
OPTIONAL_FIELDS = ("note",)


class DuplicateKeyError(ValueError):
    pass


def _no_dupes(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            raise DuplicateKeyError(f"duplicate JSON key: {k!r}")
        seen[k] = v
    return seen


def loads(text: str) -> dict:
    """Authoritative load: rejects duplicate object keys."""
    return json.loads(text, object_pairs_hook=_no_dupes)


def load(path: str | Path) -> dict:
    return loads(Path(path).read_text(encoding="utf-8"))


def _is_strict_int(v) -> bool:
    return isinstance(v, int) and not isinstance(v, bool)


def _valid_rfc3339(v) -> bool:
    if not isinstance(v, str) or not _RFC3339.match(v):
        return False
    try:
        datetime.fromisoformat(v.replace("Z", "+00:00"))   # rejects impossible dates/times
        return True
    except ValueError:
        return False


def _safe_basename(name) -> bool:
    if not isinstance(name, str) or not name:
        return False
    if "/" in name or "\\" in name or name in (".", "..") or ".." in name:
        return False
    if "?" in name or "#" in name:
        return False
    return all(0x20 <= ord(c) != 0x7F for c in name)


def validate(record: dict) -> list[str]:
    """Return a list of problem strings ([] if the record is valid)."""
    problems: list[str] = []
    if not isinstance(record, dict):
        return ["record is not a JSON object"]

    allowed = set(REQUIRED_FIELDS) | set(OPTIONAL_FIELDS)
    for k in record:
        if k not in allowed and not k.startswith("x_"):
            problems.append(f"unknown unsupported field: {k!r} (only documented x_ extensions allowed)")
    for f in REQUIRED_FIELDS:
        if f not in record:
            problems.append(f"missing field: {f!r}")
    if problems:
        return problems

    if not _is_strict_int(record["schema_version"]) or record["schema_version"] != SCHEMA_VERSION:
        problems.append(f"schema_version must be the integer {SCHEMA_VERSION} (no bool/float/str)")
    for f in ("version", "tag", "release_url", "published_at", "source_commit",
              "annotated_tag_object", "wheel_filename", "wheel_sha256", "sdist_filename",
              "sdist_sha256", "registry_status"):
        if not isinstance(record[f], str) or not record[f]:
            problems.append(f"{f} must be a non-empty string")
    if "note" in record and (not isinstance(record["note"], str) or not record["note"]
                             or len(record["note"]) > 2000):
        problems.append("note must be a bounded non-empty string")
    if problems:
        return problems

    version, tag = record["version"], record["tag"]
    if not _VERSION.match(version):
        problems.append("version is malformed")
    if tag != "v" + version:
        problems.append(f"tag must equal 'v'+version (expected v{version}, got {tag!r})")
    expected_url = f"https://github.com/{OWNER}/{REPO}/releases/tag/{tag}"
    if record["release_url"] != expected_url:
        problems.append(f"release_url must be exactly {expected_url!r}")
    if not _valid_rfc3339(record["published_at"]):
        problems.append("published_at must be a real RFC 3339 timestamp with an explicit offset")
    if not _HEX40.match(record["source_commit"]):
        problems.append("source_commit must be 40 lowercase hex chars")
    if not _HEX40.match(record["annotated_tag_object"]):
        problems.append("annotated_tag_object must be 40 lowercase hex chars")
    for f in ("wheel_sha256", "sdist_sha256"):
        if not _SHA256.match(record[f]):
            problems.append(f"{f} must be 64 lowercase hex chars")
    # bind artifact identity to the version (documented naming scheme)
    if not _safe_basename(record["wheel_filename"]):
        problems.append("wheel_filename must be a safe basename")
    elif record["wheel_filename"] != f"puckworks-{version}-py3-none-any.whl":
        problems.append(f"wheel_filename must be puckworks-{version}-py3-none-any.whl")
    if not _safe_basename(record["sdist_filename"]):
        problems.append("sdist_filename must be a safe basename")
    elif record["sdist_filename"] != f"puckworks-{version}.tar.gz":
        problems.append(f"sdist_filename must be puckworks-{version}.tar.gz")
    if not _is_strict_int(record["manually_attached_asset_count"]) or record["manually_attached_asset_count"] < 0:
        problems.append("manually_attached_asset_count must be a non-negative integer")
    if record["registry_status"] not in _REGISTRY_STATES:
        problems.append(f"registry_status must be one of {_REGISTRY_STATES}")
    return problems


def load_validated(path: str | Path) -> dict:
    record = load(path)
    problems = validate(record)
    if problems:
        raise ValueError("invalid public_release.json:\n  " + "\n  ".join(problems))
    return record


def canonical_wheel_url(record: dict) -> str:
    base = record["release_url"].rsplit("/tag/", 1)[0]
    return f"{base}/download/{record['tag']}/{record['wheel_filename']}"


def canonical_sdist_url(record: dict) -> str:
    base = record["release_url"].rsplit("/tag/", 1)[0]
    return f"{base}/download/{record['tag']}/{record['sdist_filename']}"


# ─────────────────────────── durable-evidence keyed cross-check (3B) ───────────────
_EVIDENCE_LABELS = {
    "version": r"package version",
    "tag": r"annotated tag",
    "published_at": r"published at",
    "source_commit": r"peeled source commit",
    "annotated_tag_object": r"tag-object hash",
}


def parse_evidence_report(text: str) -> dict:
    """Parse the labelled fields of RELEASE_VERIFICATION_v0.2.0.md into a dict, rejecting
    conflicting repeated labels. Table rows look like `| <label> | <value> |`."""
    out: dict[str, str] = {}
    for line in text.splitlines():
        m = re.match(r"^\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*$", line)
        if not m:
            continue
        label = re.sub(r"[`*]", "", m.group(1)).strip().lower()
        value = re.sub(r"[`*]", "", m.group(2)).strip()
        for key, pat in _EVIDENCE_LABELS.items():
            if re.fullmatch(pat, label):
                if key in out and out[key] != value:
                    raise ValueError(f"conflicting evidence for {key}: {out[key]!r} vs {value!r}")
                out[key] = value
    # Artifact rows (| `name` | ... | `sha` | ...). Collect EVERY candidate wheel/sdist row with its
    # own-row SHA — never first-match — then require exactly one canonical row of each kind.
    wheel_rows: list[tuple[str, str]] = []
    sdist_rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        cells = [re.sub(r"[`*]", "", c).strip() for c in line.split("|")]
        shas = [c for c in cells if _SHA256.fullmatch(c)]
        for cell in cells:
            if cell.endswith(".whl"):
                if len(shas) != 1:
                    raise ValueError(f"wheel row has {len(shas)} SHA-256 values (need exactly 1): {cell}")
                wheel_rows.append((cell, shas[0]))
            elif cell.endswith(".tar.gz") and cell.startswith("puckworks-") and "paper3" not in cell:
                if len(shas) != 1:
                    raise ValueError(f"sdist row has {len(shas)} SHA-256 values (need exactly 1): {cell}")
                sdist_rows.append((cell, shas[0]))

    def _one(rows, kind):
        uniq = set(rows)
        if not uniq:
            raise ValueError(f"missing {kind} artifact evidence")
        if len(uniq) > 1:
            raise ValueError(f"ambiguous/duplicate conflicting {kind} rows: {sorted(uniq)}")
        return next(iter(uniq))

    out["wheel_filename"], out["wheel_sha256"] = _one(wheel_rows, "wheel")
    out["sdist_filename"], out["sdist_sha256"] = _one(sdist_rows, "sdist")
    return out


def cross_check(record: dict, evidence: dict) -> list[str]:
    """Compare the record to keyed durable evidence — field by field, not substring presence."""
    problems = []
    mapping = {
        "version": record["version"], "tag": record["tag"],
        "published_at": record["published_at"], "source_commit": record["source_commit"],
        "annotated_tag_object": record["annotated_tag_object"],
        "wheel_filename": record["wheel_filename"], "wheel_sha256": record["wheel_sha256"],
        "sdist_filename": record["sdist_filename"], "sdist_sha256": record["sdist_sha256"],
    }
    for key, value in mapping.items():
        if key not in evidence:
            problems.append(f"evidence missing labelled field: {key}")
        elif evidence[key] != value:
            problems.append(f"{key} disagrees: record={value!r} evidence={evidence[key]!r}")
    return problems


# ─────────────────────────── live verification (3C) ──────────────────────────────
def _stream_sha256(url: str, *, timeout: float = 60.0, max_bytes: int = 64 * 1024 * 1024):
    """Stream a URL to a temp file, hashing while streaming. Returns (sha256, size). Cleans up."""
    import hashlib
    import tempfile

    h = hashlib.sha256()
    size = 0
    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "puckworks-release-verify/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            while True:
                chunk = resp.read(1 << 20)
                if not chunk:
                    break
                size += len(chunk)
                if size > max_bytes:
                    raise ValueError(f"artifact exceeds {max_bytes} bytes")
                h.update(chunk)
                tmp.write(chunk)
        return h.hexdigest(), size
    finally:
        tmp.close()
        Path(tmp.name).unlink(missing_ok=True)


def classify_pypi_absence(status: int | None, category: str) -> tuple[bool, str]:
    """FAIL-CLOSED registry check. Returns (affirmatively_absent, disposition).
    ONLY an observed HTTP 404 is 'absent'; HTTP 200 is 'present'; any other status, redirect, or
    transport/parse failure is 'indeterminate' (never treated as absence)."""
    if category == "absent" and status == 404:
        return True, "absent_404"
    if status == 200 or category == "present":
        return False, "present_200"
    return False, f"indeterminate_{category}"


def _pypi_probe(repo: str, *, opener=None, timeout: float = 15.0) -> tuple[int | None, str]:
    """Probe PyPI. Returns (status|None, category). 200->present, 404->absent, else fail-closed."""

    opener = opener or urllib.request.urlopen
    url = f"https://pypi.org/pypi/{repo}/json"
    req = urllib.request.Request(url, headers={"User-Agent": "puckworks-release-verify/1.0"})
    try:
        with opener(req, timeout=timeout) as r:
            code = getattr(r, "status", None) or r.getcode()
        return code, ("present" if code == 200 else f"unexpected_{code}")
    except urllib.error.HTTPError as e:
        return e.code, ("absent" if e.code == 404 else f"http_{e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return None, f"transport_{type(e).__name__}"
    except Exception as e:                                    # parse/other — still fail-closed
        return None, f"error_{type(e).__name__}"


def _gh_json(path: str, *, opener=None, timeout: float = 30.0) -> dict:

    opener = opener or urllib.request.urlopen
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "puckworks-release-verify/1.0",
                                               "Accept": "application/vnd.github+json"})
    with opener(req, timeout=timeout) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8") if isinstance(data, bytes) else data)


def _canon_ts(ts: str) -> str:
    from datetime import datetime
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().isoformat()
    except (ValueError, AttributeError):
        return ts


def verify_live(path: str | Path, *, gh_json=_gh_json, stream=_stream_sha256,
                pypi_probe=_pypi_probe) -> dict:
    """Strictly load + cross-check the record, then bind it to the LIVE GitHub release, the git tag
    object, the asset inventory, streamed artifact hashes, and a fail-closed PyPI check. Returns a
    deterministic evidence dict; raises on any failure. Fetchers are injectable for offline tests."""
    record = load_validated(path)
    problems: list[str] = []

    # 1. release identity
    rel = gh_json(f"releases/tags/{record['tag']}")
    if rel.get("tag_name") != record["tag"]:
        problems.append("release tag_name mismatch")
    if rel.get("html_url") != record["release_url"]:
        problems.append(f"release html_url mismatch: {rel.get('html_url')!r}")
    if bool(rel.get("draft")):
        problems.append("release is draft")
    if bool(rel.get("prerelease")):
        problems.append("release is prerelease")
    if _canon_ts(rel.get("published_at", "")) != _canon_ts(record["published_at"]):
        problems.append("release published_at mismatch")

    # 2. git tag object identity (reject lightweight; bind annotated object + peeled commit)
    ref = gh_json(f"git/ref/tags/{record['tag']}")
    obj = ref.get("object", {})
    if obj.get("type") != "tag":
        problems.append("tag ref is not an annotated tag object (lightweight tag)")
    elif obj.get("sha") != record["annotated_tag_object"]:
        problems.append("annotated_tag_object SHA mismatch")
    else:
        tagobj = gh_json(f"git/tags/{obj['sha']}")
        tgt = tagobj.get("object", {})
        if tgt.get("type") != "commit":
            problems.append("annotated tag does not peel to a commit")
        elif tgt.get("sha") != record["source_commit"]:
            problems.append("source_commit (peeled tag) mismatch")

    # 3. asset identity
    asset_names = [a["name"] for a in rel.get("assets", [])]
    if len(asset_names) != len(set(asset_names)):
        problems.append("duplicate asset filenames in the release")
    if len(asset_names) != record["manually_attached_asset_count"]:
        problems.append(f"asset count {len(asset_names)} != recorded {record['manually_attached_asset_count']}")
    sizes = {a["name"]: a.get("size") for a in rel.get("assets", [])}
    for fn in (record["wheel_filename"], record["sdist_filename"]):
        if fn not in asset_names:
            problems.append(f"expected asset missing from release: {fn}")

    wheel_sha, wheel_size = stream(canonical_wheel_url(record))
    sdist_sha, sdist_size = stream(canonical_sdist_url(record))
    if wheel_sha != record["wheel_sha256"]:
        problems.append("live wheel SHA-256 mismatch")
    if sdist_sha != record["sdist_sha256"]:
        problems.append("live sdist SHA-256 mismatch")
    if sizes.get(record["wheel_filename"]) not in (None, wheel_size):
        problems.append("wheel reported-size != streamed-size")
    if sizes.get(record["sdist_filename"]) not in (None, sdist_size):
        problems.append("sdist reported-size != streamed-size")

    # 4. registry identity — fail-closed
    pypi_status, pypi_cat = pypi_probe(REPO)
    absent, pypi_disposition = classify_pypi_absence(pypi_status, pypi_cat)
    if record["registry_status"] == "github_only" and not absent:
        problems.append(f"registry_status=github_only requires an affirmative PyPI 404; got {pypi_disposition}")

    evidence = {
        "tag": record["tag"], "release_url": record["release_url"],
        "wheel_filename": record["wheel_filename"], "wheel_sha256": wheel_sha, "wheel_size": wheel_size,
        "sdist_filename": record["sdist_filename"], "sdist_sha256": sdist_sha, "sdist_size": sdist_size,
        "release_asset_count": len(asset_names), "annotated_tag_object": record["annotated_tag_object"],
        "source_commit": record["source_commit"], "pypi_status": pypi_status,
        "pypi_disposition": pypi_disposition, "problems": problems, "verified": not problems,
    }
    if problems:
        raise ValueError("live release verification failed:\n  " + "\n  ".join(problems)
                         + "\n" + json.dumps(evidence, indent=2, sort_keys=True))
    return evidence


def verify_all(path: str | Path, evidence_report_path: str | Path, *, live: bool = False,
               **live_kw) -> dict:
    """Composite: (1) strict schema validation, (2) keyed durable-evidence cross-check, (3) optional
    live verification. Fails (raises) on any layer. Never returns verified without the cross-check."""
    record = load_validated(path)                      # layer 1 (raises on invalid)
    evidence = parse_evidence_report(Path(evidence_report_path).read_text(encoding="utf-8"))
    xproblems = cross_check(record, evidence)          # layer 2
    if xproblems:
        raise ValueError("durable-evidence cross-check failed:\n  " + "\n  ".join(xproblems))
    result = {"schema": "ok", "cross_check": "ok", "layers": ["schema", "cross_check"]}
    if live:
        result["live"] = verify_live(path, **live_kw)  # layer 3 (raises on mismatch)
        result["layers"].append("live")
    return result


if __name__ == "__main__":
    import sys

    _root = Path(__file__).resolve().parents[1]
    p = str(_root / "docs" / "status" / "public_release.json")
    evid = str(_root / "docs" / "reproducibility" / "RELEASE_VERIFICATION_v0.2.0.md")
    known = {"--verify-live", "--verify-all", "--help", "-h"}
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a not in known]
    if unknown:
        print(f"unknown option(s): {unknown}", file=sys.stderr)
        raise SystemExit(2)
    try:
        if "--verify-all" in sys.argv:
            # schema -> keyed durable cross-check -> live verification (all layers, fail on any)
            res = verify_all(p, evid, live=True)
            print(json.dumps(res, indent=2, sort_keys=True))
        elif "--verify-live" in sys.argv:
            print(json.dumps(verify_live(p), indent=2, sort_keys=True))
        else:
            # default: schema + keyed durable-evidence cross-check (offline, no network)
            verify_all(p, evid, live=False)
            print(f"public_release.json OK (schema + durable cross-check): {load(p)['tag']}")
    except (ValueError, DuplicateKeyError) as exc:
        print("VERIFICATION FAILED:", exc, file=sys.stderr)
        raise SystemExit(1)
