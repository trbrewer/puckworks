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
import math
import pathlib

_REPO = pathlib.Path(__file__).resolve().parents[2]
SOURCE_CSV = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

#: The named solutes the benchmark scores, mapped to the SOURCE COLUMN each one is measured in, in
#: the order the corpus manifest declares them.
#:
#: Round-10 (second review) P1-2. The oracle used to declare only the solute names and emit three
#: observation ids for every retained record unconditionally, which made "three observations per
#: sample" an axiom rather than a property of the data. The reviewer deleted `CF`, `TR` and `5CQA`
#: from a copy of the CSV entirely and this module still certified 44 records and 132 named-solute
#: observations without raising. The production corpus manifest shared the same assumption, so it was
#: a common-mode failure: two independent grouping implementations resting on one unverified premise.
#:
#: Declared here independently, and deliberately NOT imported from the production contract — sharing
#: the map would rebuild the common mode this exists to break.
ANALYTE_COLUMNS = (
    ("caffeine", "CF"),
    ("trigonelline", "TR"),
    ("5CQA", "5CQA"),
)

#: The named solutes the benchmark scores, in the order the corpus manifest declares them.
SOLUTES = tuple(solute for solute, _column in ANALYTE_COLUMNS)
VARIETIES = ("Arabica", "Robusta")
HELD_OUT_GRINDS = ("C", "F")

REQUIRED_COLUMNS = ("sample", "variety", "T_degC", "p_bar", "granulometry", "on_grid",
                    *(column for _solute, column in ANALYTE_COLUMNS))

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
        sample_id = row["sample"].strip()
        out.append({
            "sample_id": sample_id,
            "variety": row["variety"].strip(),
            "grind": row["granulometry"].strip(),
            "temperature": _num(row["T_degC"]),
            "pressure": _num(row["p_bar"]),
            "on_grid": row["on_grid"].strip() == "True",
            # The scored cells, validated. Only the retained held-out rows are checked: a source row
            # outside this corpus answers to a different contract, and failing on it here would make
            # the oracle reject data the benchmark never scores.
            "observations": tuple(
                {"solute": solute, "source_column": column,
                 "value": _scored_value(row.get(column), sample_id, solute, column)}
                for solute, column in ANALYTE_COLUMNS),
        })

    ids = [r["sample_id"] for r in out]
    if len(set(ids)) != len(ids):
        raise ValueError("held-out source records contain duplicate sample ids")
    for r in out:
        if not r["sample_id"] or "|" in r["sample_id"]:
            raise ValueError("sample id %r is empty or contains the observation delimiter"
                             % r["sample_id"])
    return out


def _scored_value(text, sample_id: str, solute: str, column: str) -> float:
    """Require one scored analyte cell to be present, numeric and finite.

    Round-10 (second review) P1-2. Without this, an artefact could claim 132 named-solute
    observations from a source that measures none of them. The message names the sample, the solute
    and the SOURCE COLUMN, because "132 != 132" would not tell anyone which cell to go and look at.
    """
    if text is None:
        raise ValueError("source observation %s|%s: column %r is absent from the row"
                         % (sample_id, solute, column))
    if not str(text).strip():
        raise ValueError("source observation %s|%s: column %r is blank"
                         % (sample_id, solute, column))
    try:
        value = float(str(text).strip())
    except (TypeError, ValueError) as exc:
        raise ValueError("source observation %s|%s: column %r is non-numeric (%r)"
                         % (sample_id, solute, column, text)) from exc
    if not math.isfinite(value):
        raise ValueError("source observation %s|%s: column %r is non-finite (%r)"
                         % (sample_id, solute, column, text))
    return value


def observation_ids(record: dict) -> list[str]:
    """The observation ids a sample record contributes, from its VALIDATED scored cells.

    Built from ``record["observations"]`` rather than from the canonical solute tuple, so the count
    132 is a result of source validation rather than an axiom (round-10, second review, P1-2).
    """
    observations = record.get("observations")
    if not observations:
        raise ValueError("source record %r carries no validated scored observations"
                         % record.get("sample_id"))
    ids = ["%s|%s" % (record["sample_id"], o["solute"]) for o in observations]
    if len(set(ids)) != len(ids):
        raise ValueError("source record %r yields duplicate observation ids %r"
                         % (record.get("sample_id"), ids))
    return ids


def _cluster_defs(scheme: str, record: dict):
    """(stratum_id, cluster_id, observation_ids) contributions of one record under ``scheme``.

    Written out per scheme, from the scheme's scientific definition, rather than routed through a
    shared key-builder — the production code already has one of those.
    """
    sid, var, grind = record["sample_id"], record["variety"], record["grind"]
    T, p = record["temperature"], record["pressure"]

    # Per-solute schemes iterate the record's VALIDATED observations, not the canonical solute
    # tuple, so every scheme's partition rests on the same source validation (round-10, second
    # review, P1-2).
    solutes = [o["solute"] for o in record["observations"]]

    if scheme == "cond_in_variety":
        yield var, "%s|%s|%s" % (var, T, p), observation_ids(record)
    elif scheme == "sample_in_variety_grind":
        yield "%s|%s" % (var, grind), sid, observation_ids(record)
    elif scheme == "cond_in_group":
        for solute in solutes:
            yield ("%s|%s" % (var, solute),
                   "%s|%s|%s|%s" % (var, solute, T, p),
                   ["%s|%s" % (sid, solute)])
    elif scheme == "group":
        for solute in solutes:
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
    """Put an artefact scheme into the oracle's canonical shape for comparison.

    ``n_observations`` is carried through as declared (``None`` when absent) rather than recomputed,
    so a cluster whose declared count contradicts its own id list is visible to the comparison
    instead of being quietly corrected here.
    """
    out = []
    for c in scheme_obj.get("membership") or []:
        out.append({"stratum_id": str(c.get("stratum", "")),
                    "cluster_id": str(c.get("cluster_id", "")),
                    "sample_ids": sorted(c.get("sample_ids") or []),
                    "grinds": sorted(c.get("grinds") or []),
                    "observation_ids": sorted(c.get("observation_ids") or []),
                    "n_observations": c.get("n_observations")})
    return sorted(out, key=lambda c: (c["stratum_id"], c["cluster_id"]))


def compare_design(artifact_design: dict, records=None) -> list[str]:
    """Compare an artefact's resampling design with the source-derived expectation.

    Returns a list of problems naming the scheme and the exact mismatch. Empty means the artefact's
    partition *is* the partition the source data implies, cluster by cluster.

    Round-10 P1-2 widened what "the partition" means here. The round-9 version compared observation
    ids, stratum ids and sample ids, and stopped: the archived ``grinds`` list, the per-cluster
    observation count, the declared stratum COUNT and the cluster-size distribution were all
    unchecked, so an artefact could archive a cluster claiming both grinds when the source says one
    — with a refreshed self-hash — and this function returned an empty list. Those fields are
    published: they generate the Methods census, Table 5 and Supplementary Table S6.

    The division of labour is deliberate. This module owns everything the SOURCE DATA determines
    (which observations, samples, grinds, strata and conditions move together, and how many of
    each). ``transfer_contract.validate_resampling_design`` owns the authorial declarations a CSV
    cannot adjudicate — a scheme's role, label and rationale. Neither is sufficient alone, and this
    one deliberately shares no code with the production grouping functions.
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

        # Structural census, derived from the source rather than hard-coded as the oracle. The
        # documented stratum count is included: it is published in Table S6, and leaving it out of
        # the diagnostic is what let a wrong `n_strata` pass in round 9.
        census = EXPECTED_CENSUS[name]
        if exp["n_clusters"] != census["n_clusters"] \
                or exp["cluster_size_distribution"] != census["sizes"] \
                or exp["n_strata"] != census["n_strata"]:
            problems.append("scheme %r: the SOURCE no longer produces the documented census "
                            "(%d clusters, %d strata, sizes %r vs documented %d, %d, %r) — "
                            "adjudicate the data change before touching the artefact"
                            % (name, exp["n_clusters"], exp["n_strata"],
                               exp["cluster_size_distribution"], census["n_clusters"],
                               census["n_strata"], census["sizes"]))

        got = _normalise_artifact_scheme(got_obj)
        if len(got) != exp["n_clusters"]:
            problems.append("scheme %r: artefact has %d clusters, the source implies %d"
                            % (name, len(got), exp["n_clusters"]))

        # The artefact's OWN declared census, against the source. `validate_resampling_design`
        # checks these against the artefact's own membership; only the source can say whether that
        # membership is the right one to be self-consistent with.
        for field, want in (("n_clusters", exp["n_clusters"]), ("n_strata", exp["n_strata"])):
            if got_obj.get(field) != want:
                problems.append("scheme %r: artefact declares %s=%r, the source implies %r"
                                % (name, field, got_obj.get(field), want))
        got_sizes = {int(k): int(v)
                     for k, v in (got_obj.get("cluster_size_distribution") or {}).items()}
        if got_sizes != exp["cluster_size_distribution"]:
            problems.append("scheme %r: artefact declares cluster sizes %r, the source implies %r"
                            % (name, got_sizes, exp["cluster_size_distribution"]))
        got_obs_total = sum(len(c["observation_ids"]) for c in got)
        if got_obs_total != exp["n_observations"]:
            problems.append("scheme %r: artefact clusters carry %d observations, the source implies "
                            "%d" % (name, got_obs_total, exp["n_observations"]))

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
            if e["grinds"] != g["grinds"]:
                problems.append("scheme %r cluster %r: grinds are %r, the source implies %r — the "
                                "grind composition of a cluster is what the Methods census and "
                                "Table S6 report" % (name, cid, g["grinds"], e["grinds"]))
            if g["n_observations"] is not None and g["n_observations"] != len(e["observation_ids"]):
                problems.append("scheme %r cluster %r: declares n_observations=%r, the source "
                                "implies %d" % (name, cid, g["n_observations"],
                                                len(e["observation_ids"])))

        # A content-level comparison already happened above; the hash comparison catches ordering
        # and normalisation drift that a per-cluster loop cannot see (two clusters swapped in the
        # serialised list, say). It is a SECOND signal over reconstructed content, never the first.
        if canonical_hash(exp) != canonical_hash({"clusters": got}):
            problems.append("scheme %r: the artefact's normalised partition does not hash to the "
                            "source-derived one, though the per-cluster comparison found no "
                            "difference — inspect cluster ordering and id normalisation" % name)
    return problems


def source_observation_ids(records=None) -> list[str]:
    records = read_source_records() if records is None else records
    ids = sorted(o for r in records for o in observation_ids(r))
    if len(set(ids)) != len(ids):
        raise ValueError("source observation ids are not unique")
    return ids
