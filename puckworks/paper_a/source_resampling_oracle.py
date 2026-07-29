"""An independent, source-derived expectation for every resampling partition.

Round-9 P1-3. The round-8 artefact checker carried this comment:

    # Membership must match a design rebuilt from the source, not merely be internally
    # consistent — otherwise a wrong partition that hashes itself still passes.

and then did not do that. It compared hard-coded cluster counts and the primary scheme's size
distribution, while `validate_resampling_design` compared the membership against *its own hash*.
Two scientifically wrong partitions were demonstrated to pass:

  * swapping the ``5CQA`` observations between samples ``A12`` and ``A13`` — which breaks the
    declared "one cluster per sample record, carrying its three co-measured solutes" scheme;
  * swapping ``A19|5CQA`` and ``A20|5CQA`` in the primary scheme — placing observations under the
    wrong (T, p) condition.

Both preserve the observation set, the cluster count, the size distribution, and a refreshed
self-hash. A self-hash proves only that nobody edited the artefact without rehashing it. It cannot
tell you the partition is *right*, and clustered percentile ranges depend entirely on which
outcomes move together.

So this module reconstructs the expected partition from `bioactives.csv` and nothing else. It is
**deliberately a second implementation**:

  * it parses the CSV with `csv.DictReader`, not the production loader;
  * it does not call ``cluster_key_of``, ``stratum_key_of``, ``cluster_membership``,
    ``scheme_design`` or ``resampling_design``;
  * it never reads artefact membership while building the expectation.

That duplication is the point. If the production grouping code and this oracle share a bug they
can no longer certify each other, because they do not share any code.
"""

from __future__ import annotations

import csv
import hashlib
import json
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[2]
SOURCE_CSV = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

#: The named solutes the benchmark scores, in the order the corpus manifest declares them.
SOLUTES = ("caffeine", "trigonelline", "5CQA")
VARIETIES = ("Arabica", "Robusta")
HELD_OUT_GRINDS = ("C", "F")

REQUIRED_COLUMNS = ("sample", "variety", "T_degC", "p_bar", "granulometry", "on_grid")

#: Scheme order and the census each partition must produce, stated independently of the artefact.
#: These are documented expectations, not the oracle's authority — the authority is the exact
#: membership comparison. They exist so a structural regression is named rather than merely diffed.
EXPECTED_CENSUS = {
    "cond_in_variety":         {"n_clusters": 26, "sizes": {3: 8, 6: 18},  "n_strata": 2},
    "sample_in_variety_grind": {"n_clusters": 44, "sizes": {3: 44},        "n_strata": 4},
    "cond_in_group":           {"n_clusters": 78, "sizes": {1: 24, 2: 54}, "n_strata": 6},
    "group":                   {"n_clusters": 6,  "sizes": {22: 6},        "n_strata": 1},
}
SCHEME_ORDER = ("cond_in_variety", "sample_in_variety_grind", "cond_in_group", "group")


def _num(text: str) -> str:
    """Canonical condition coordinate, so `9` and `9.0` cannot become two clusters."""
    return "%g" % float(text)


def read_source_records(path: pathlib.Path = SOURCE_CSV) -> list[dict]:
    """Parse the held-out coarse/fine sample records straight out of the CSV.

    The file's first line is a provenance comment, so comment lines are skipped rather than
    assumed absent.
    """
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines()
             if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
    if missing:
        raise ValueError("source CSV lacks required columns %r" % (missing,))

    out = []
    for row in reader:
        if row["variety"] not in VARIETIES or row["granulometry"] not in HELD_OUT_GRINDS:
            continue
        out.append({
            "sample_id": row["sample"].strip(),
            "variety": row["variety"].strip(),
            "grind": row["granulometry"].strip(),
            "temperature": _num(row["T_degC"]),
            "pressure": _num(row["p_bar"]),
            "on_grid": row["on_grid"].strip() == "True",
        })

    ids = [r["sample_id"] for r in out]
    if len(set(ids)) != len(ids):
        raise ValueError("held-out source records contain duplicate sample ids")
    for r in out:
        if not r["sample_id"] or "|" in r["sample_id"]:
            raise ValueError("sample id %r is empty or contains the observation delimiter"
                             % r["sample_id"])
    return out


def observation_ids(record: dict) -> list[str]:
    """The three canonical observation ids a sample record contributes."""
    return ["%s|%s" % (record["sample_id"], s) for s in SOLUTES]


def _cluster_defs(scheme: str, record: dict):
    """(stratum_id, cluster_id, observation_ids) contributions of one record under ``scheme``.

    Written out per scheme, from the scheme's scientific definition, rather than routed through a
    shared key-builder — the production code already has one of those.
    """
    sid, var, grind = record["sample_id"], record["variety"], record["grind"]
    T, p = record["temperature"], record["pressure"]

    if scheme == "cond_in_variety":
        yield var, "%s|%s|%s" % (var, T, p), observation_ids(record)
    elif scheme == "sample_in_variety_grind":
        yield "%s|%s" % (var, grind), sid, observation_ids(record)
    elif scheme == "cond_in_group":
        for solute in SOLUTES:
            yield ("%s|%s" % (var, solute),
                   "%s|%s|%s|%s" % (var, solute, T, p),
                   ["%s|%s" % (sid, solute)])
    elif scheme == "group":
        for solute in SOLUTES:
            yield "", "%s|%s" % (var, solute), ["%s|%s" % (sid, solute)]
    else:
        raise ValueError("unknown scheme %r" % scheme)


def expected_scheme(records, scheme: str) -> dict:
    """The canonical expected partition for one scheme, built only from source records."""
    clusters: dict[tuple, dict] = {}
    for rec in records:
        for stratum, cluster_id, obs in _cluster_defs(scheme, rec):
            key = (stratum, cluster_id)
            entry = clusters.setdefault(key, {"stratum_id": stratum, "cluster_id": cluster_id,
                                              "sample_ids": set(), "grinds": set(),
                                              "observation_ids": []})
            entry["sample_ids"].add(rec["sample_id"])
            entry["grinds"].add(rec["grind"])
            entry["observation_ids"].extend(obs)

    out = []
    for key in sorted(clusters):
        e = clusters[key]
        out.append({"stratum_id": e["stratum_id"], "cluster_id": e["cluster_id"],
                    "sample_ids": sorted(e["sample_ids"]), "grinds": sorted(e["grinds"]),
                    "observation_ids": sorted(e["observation_ids"])})

    sizes: dict[int, int] = {}
    for c in out:
        sizes[len(c["observation_ids"])] = sizes.get(len(c["observation_ids"]), 0) + 1
    return {
        "scheme": scheme,
        "clusters": out,
        "n_clusters": len(out),
        "n_strata": len({c["stratum_id"] for c in out}),
        "cluster_size_distribution": dict(sorted(sizes.items())),
        "n_observations": sum(len(c["observation_ids"]) for c in out),
    }


def expected_design(records=None) -> dict:
    """The expected partition for every declared scheme."""
    records = read_source_records() if records is None else records
    return {name: expected_scheme(records, name) for name in SCHEME_ORDER}


def canonical_hash(scheme_obj: dict) -> str:
    payload = json.dumps([[c["stratum_id"], c["cluster_id"], c["observation_ids"]]
                          for c in scheme_obj["clusters"]],
                         ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _normalise_artifact_scheme(scheme_obj: dict) -> list[dict]:
    """Put an artefact scheme into the oracle's canonical shape for comparison."""
    out = []
    for c in scheme_obj.get("membership") or []:
        out.append({"stratum_id": str(c.get("stratum", "")),
                    "cluster_id": str(c.get("cluster_id", "")),
                    "sample_ids": sorted(c.get("sample_ids") or []),
                    "grinds": sorted(c.get("grinds") or []),
                    "observation_ids": sorted(c.get("observation_ids") or [])})
    return sorted(out, key=lambda c: (c["stratum_id"], c["cluster_id"]))


def compare_design(artifact_design: dict, records=None) -> list[str]:
    """Compare an artefact's resampling design with the source-derived expectation.

    Returns a list of problems naming the scheme and the exact mismatch. Empty means the artefact's
    partition *is* the partition the source data implies, cluster by cluster.
    """
    problems: list[str] = []
    expected = expected_design(records)
    schemes = (artifact_design or {}).get("schemes") or {}

    for name in SCHEME_ORDER:
        exp = expected[name]
        got_obj = schemes.get(name)
        if not isinstance(got_obj, dict):
            problems.append("scheme %r is missing from the artefact's resampling design" % name)
            continue

        # Structural census, derived from the source rather than hard-coded as the oracle.
        census = EXPECTED_CENSUS[name]
        if exp["n_clusters"] != census["n_clusters"] or \
                exp["cluster_size_distribution"] != census["sizes"]:
            problems.append("scheme %r: the SOURCE no longer produces the documented census "
                            "(%d clusters %r vs documented %d %r) — adjudicate the data change "
                            "before touching the artefact"
                            % (name, exp["n_clusters"], exp["cluster_size_distribution"],
                               census["n_clusters"], census["sizes"]))

        got = _normalise_artifact_scheme(got_obj)
        if len(got) != exp["n_clusters"]:
            problems.append("scheme %r: artefact has %d clusters, the source implies %d"
                            % (name, len(got), exp["n_clusters"]))

        exp_by_id = {c["cluster_id"]: c for c in exp["clusters"]}
        got_by_id = {c["cluster_id"]: c for c in got}
        for missing in sorted(set(exp_by_id) - set(got_by_id)):
            problems.append("scheme %r: artefact is missing cluster %r" % (name, missing))
        for extra in sorted(set(got_by_id) - set(exp_by_id)):
            problems.append("scheme %r: artefact has undeclared cluster %r" % (name, extra))

        for cid in sorted(set(exp_by_id) & set(got_by_id)):
            e, g = exp_by_id[cid], got_by_id[cid]
            if e["observation_ids"] != g["observation_ids"]:
                problems.append(
                    "scheme %r cluster %r: membership differs from the source. source=%r "
                    "artefact=%r — a clustered range depends on which outcomes move together, so "
                    "this is a scientific defect, not a bookkeeping one"
                    % (name, cid, e["observation_ids"], g["observation_ids"]))
            if e["stratum_id"] != g["stratum_id"]:
                problems.append("scheme %r cluster %r: stratum is %r, the source implies %r"
                                % (name, cid, g["stratum_id"], e["stratum_id"]))
            if e["sample_ids"] != g["sample_ids"]:
                problems.append("scheme %r cluster %r: sample ids are %r, the source implies %r"
                                % (name, cid, g["sample_ids"], e["sample_ids"]))
    return problems


def source_observation_ids(records=None) -> list[str]:
    records = read_source_records() if records is None else records
    ids = sorted(o for r in records for o in observation_ids(r))
    if len(set(ids)) != len(ids):
        raise ValueError("source observation ids are not unique")
    return ids
