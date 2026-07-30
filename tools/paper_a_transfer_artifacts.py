#!/usr/bin/env python3
"""Deterministic writer and checker for Paper A's three transfer artefacts.

Round-8 §2.3. The committed transfer JSONs were produced by hand-run snippets — the corpus
contract still records ``python scratchpad/run_corpus_contracts.py`` as its command, and that
file does not exist. A result nobody can regenerate is a result nobody can check, which is the
soil every stale number in rounds 5 through 8 grew in.

Three modes, because they cost three different amounts:

``--check`` (CI-cheap, seconds)
    Rebuilds the corpus manifest *from the source CSV* and asserts the committed artefacts carry
    exactly that membership and hash; validates the endpoint contract, schema version, resampling
    design and every interval's full-precision/display reconciliation; and requires all three
    artefacts to agree on one manifest. This deliberately does NOT re-solve any PDE — the whole
    point is that membership and schema drift can be caught for free, every commit.

``--recompute`` (slow, ~14 min)
    Everything ``--check`` does, then re-runs the producers and compares the numbers, reporting
    any field that moved.

``--write`` (slow, ~14 min)
    Re-runs the producers and rewrites all three artefacts ATOMICALLY: every artefact is built and
    validated in memory first, and nothing is replaced unless all of them pass. A partial write
    would leave the tree in a state where two artefacts describe different corpora — the exact
    failure the manifest hash exists to detect.

Provenance is expressed through stable fields (source hash, schema version, RNG, seed, B), never
a wall-clock timestamp: a timestamp would make an otherwise deterministic artefact change on
every run and destroy ``--check``'s meaning.

CLI::

    python tools/paper_a_transfer_artifacts.py --check
    python tools/paper_a_transfer_artifacts.py --recompute
    python tools/paper_a_transfer_artifacts.py --write
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from puckworks.paper_a import source_resampling_oracle as ORACLE  # noqa: E402
from puckworks.paper_a import transfer_contract as TC  # noqa: E402
from puckworks.paper_a import transfer_semantics as TS  # noqa: E402

RESOURCE = _REPO / "docs" / "paper1_resource"
ENDPOINT_JSON = RESOURCE / "PAPER_A_ENDPOINT_PROPAGATION.json"
CORPUS_JSON = RESOURCE / "PAPER_A_TRANSFER_CORPUS_CONTRACTS.json"
LOSS_JSON = RESOURCE / "PAPER_A_COMPARATOR_LOSS_ROBUSTNESS.json"
SOURCE_CSV = _REPO / "puckworks" / "data" / "angeloni2023" / "bioactives.csv"

ARTIFACTS = (ENDPOINT_JSON, CORPUS_JSON, LOSS_JSON)


def source_sha256() -> str:
    return hashlib.sha256(SOURCE_CSV.read_bytes()).hexdigest()


def _reject_constant(name: str):
    """Refuse JSON's non-standard NaN/Infinity constants at the parse boundary.

    Round-10 P1-3. Python's `json` accepts `NaN`, `Infinity` and `-Infinity` by default and hands
    back floats that then flow into comparisons where NaN silently loses every ordering test. An
    artefact containing them is malformed, and the right place to say so is where it is read.
    """
    raise ValueError("artefact contains the non-standard JSON constant %r; bounds and losses must "
                     "be finite numbers" % name)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def _dump(obj: dict) -> str:
    """Serialise strictly: `allow_nan=False` raises rather than emitting `NaN`/`Infinity`."""
    return json.dumps(obj, indent=1, ensure_ascii=False, sort_keys=False, allow_nan=False) + "\n"


def reference_manifest(include_off_grid: bool = True) -> dict:
    """The corpus manifest rebuilt from the SOURCE data, independent of any artefact."""
    from puckworks import data as d
    return TC.build_transfer_corpus_manifest(d.angeloni_bioactives(),
                                             include_off_grid=include_off_grid)


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Checking
# ─────────────────────────────────────────────────────────────────────────────────────────────

def _check_corpus_block(label: str, block: dict, expected: dict) -> list[str]:
    """Bind one artefact's corpus block to the source-derived manifest."""
    problems = []
    if not isinstance(block, dict):
        return ["%s: no corpus block" % label]
    for field in ("estimand", "include_off_grid", "n_held_out_records", "n_observations",
                  "n_lookup_observations", "support_set"):
        if block.get(field) != expected.get(field):
            problems.append("%s: corpus.%s is %r, source says %r"
                            % (label, field, block.get(field), expected.get(field)))
    for field in ("held_out_sample_ids", "excluded_sample_ids", "off_grid_sample_ids",
                  "lookup_undefined_sample_ids"):
        if sorted(block.get(field) or []) != sorted(expected.get(field) or []):
            problems.append("%s: corpus.%s does not match the source-derived membership"
                            % (label, field))
    # A count cannot detect a DIFFERENT set of 44 records; the hash can.
    if block.get("manifest_sha256") != expected["manifest_sha256"]:
        problems.append("%s: corpus manifest hash %r != source-derived %r — the declared corpus "
                        "is not the corpus the source produces"
                        % (label, block.get("manifest_sha256"), expected["manifest_sha256"]))
    if block.get("included_sample_ids_sha256") != expected["included_sample_ids_sha256"]:
        problems.append("%s: included sample-ID hash does not match the source" % label)
    problems += ["%s: %s" % (label, p) for p in
                 TC.validate_corpus_manifest(block, bool(expected["include_off_grid"]))]
    return problems


def _check_intervals(label: str, node, problems: list[str], path: str = "") -> None:
    """Walk a structure and reconcile every interval record it contains."""
    if isinstance(node, dict):
        if "full_precision_pp" in node and "display" in node:
            for p in TC.validate_interval_record(node):
                problems.append("%s%s: %s" % (label, path, p))
        for k, v in node.items():
            _check_intervals(label, v, problems, path + "." + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            _check_intervals(label, v, problems, path + "[%d]" % i)


def check() -> list[str]:
    """Fast, CI-suitable source→artefact and schema checks."""
    problems: list[str] = []
    for path in ARTIFACTS:
        if not path.exists():
            problems.append("missing artefact %s" % path.relative_to(_REPO))
    if problems:
        return problems

    try:
        ep, corpus, loss = (_load(p) for p in ARTIFACTS)
    except ValueError as exc:
        return ["an artefact could not be read as strict JSON: %s" % exc]
    complete = reference_manifest(True)
    matched = reference_manifest(False)
    src = source_sha256()

    # -- schema and endpoint contract ---------------------------------------------------------
    for label, art in (("endpoint", ep), ("comparator-loss", loss), ("corpus-contract", corpus)):
        if int(art.get("schema_version", 0)) != TC.SCHEMA_VERSION:
            problems.append("%s: schema_version is %r, expected %d"
                            % (label, art.get("schema_version"), TC.SCHEMA_VERSION))
        if art.get("source_sha256") != src:
            problems.append("%s: source_sha256 %r != the committed bioactives.csv (%s)"
                            % (label, art.get("source_sha256"), src[:12]))
    problems += ["endpoint: %s" % p for p in TC.validate_endpoint_contract(ep)]
    problems += ["comparator-loss: %s" % p for p in
             TC.validate_endpoint_contract(loss, require_rows=False)]

    # -- corpus membership, bound to the SOURCE not to each other ------------------------------
    problems += _check_corpus_block("endpoint", ep.get("corpus"), complete)
    problems += _check_corpus_block("comparator-loss", loss.get("corpus"), complete)
    problems += _check_corpus_block("corpus-contract/complete",
                                    (corpus.get("complete_corpus") or {}).get("corpus"), complete)
    problems += _check_corpus_block("corpus-contract/matched",
                                    (corpus.get("matched_on_grid") or {}).get("corpus"), matched)

    # -- one canonical corpus across every result artefact -------------------------------------
    hashes = {
        "endpoint": (ep.get("corpus") or {}).get("manifest_sha256"),
        "comparator-loss": (loss.get("corpus") or {}).get("manifest_sha256"),
        "corpus-contract/complete": ((corpus.get("complete_corpus") or {})
                                     .get("corpus") or {}).get("manifest_sha256"),
    }
    if len(set(hashes.values())) != 1:
        problems.append("the complete-corpus artefacts do not agree on one manifest: %r" % hashes)

    # -- resampling design ---------------------------------------------------------------------
    design = ep.get("resampling_design")
    if not isinstance(design, dict):
        problems.append("endpoint: no archived resampling_design")
    else:
        # Round-10 P1-2: this validator now pins the WHOLE declared design — typed estimand
        # (re-derived from its primitives), typed inferential status, interval kind, refit flag,
        # primary scheme, scheme order, and every scheme's role, label, rationale, strata, cluster
        # key and recomputed census. Twelve mutations that changed only what the design SAYS used to
        # pass here, and the Methods paragraph, Table 5 and Table S6 are generated from it.
        problems += ["endpoint: %s" % p for p in
                     TC.validate_resampling_design(design, complete["n_observations"])]
        # Round-9 P1-3. This block used to carry exactly the comment above and then compare only
        # hard-coded cluster COUNTS plus the primary size distribution, while
        # `validate_resampling_design` compared the membership against its own hash. It did not
        # rebuild anything from the source, and two scientifically wrong partitions passed:
        # swapping one solute between two sample records, and moving an observation into the wrong
        # condition cluster. Both preserve every count, every size distribution and every hash.
        #
        # The comparison is now exact and against an INDEPENDENT oracle that parses the CSV itself
        # and deliberately shares no code with the production grouping functions, so a shared
        # grouping bug can no longer certify itself.
        problems += ["endpoint: %s" % p for p in ORACLE.compare_design(design)]

    # -- Monte Carlo audits: addressed by exact target, never reused (round-9 P1-1) -------------
    audits = ep.get("stability_audits")
    if not isinstance(audits, list) or not audits:
        problems.append("endpoint: no `stability_audits` list; the round-8 schema stored one "
                        "top-level scalar, which let a single target's Monte Carlo error be "
                        "printed as though it described every endpoint, scheme and fitting loss")
    else:
        for i, a in enumerate(audits):
            if not isinstance(a, dict) or not isinstance(a.get("target"), dict):
                problems.append("endpoint: stability_audits[%d] declares no exact target" % i)
        if not TS.has_exact_audit(ep, TS.AUDITED_TARGET):
            problems.append("endpoint: no archived Monte Carlo audit for the declared target %r"
                            % (TS.AUDITED_TARGET.as_dict(),))

    # -- intervals: every stored field must reconcile with full precision -----------------------
    # The corpus contract is walked too. It archives a per-scheme interval for both corpus arms, and
    # leaving it out meant "reconciles every interval record" described two artefacts out of three.
    for label, art in (("endpoint", ep), ("comparator-loss", loss), ("corpus-contract", corpus)):
        _check_intervals(label, art, problems)

    # -- the point estimate must not depend on the cluster scheme ------------------------------
    for row in ep.get("rows") or []:
        means = {n: s.get("observed_mean_delta_pp")
                 for n, s in (row.get("resampling") or {}).items()}
        if len(set(means.values())) > 1:
            problems.append("endpoint %r g: the observed point estimate differs by scheme (%r); "
                            "clustering must change the range, not the mean"
                            % (row.get(TC.ENDPOINT_ROW_KEY), means))
    return problems


# ─────────────────────────────────────────────────────────────────────────────────────────────
# Building
# ─────────────────────────────────────────────────────────────────────────────────────────────

def build() -> dict:
    """Re-run the producers and assemble all three artefacts. Slow (~14 min of PDE solves)."""
    from puckworks.validation.slow import angeloni_bracket as AB

    src = source_sha256()
    provenance = dict(
        producer="puckworks.validation.slow.angeloni_bracket",
        command="python tools/paper_a_transfer_artifacts.py --write",
        rng="PCG64", canonical_B=AB.CANONICAL_BOOT_B, seed=AB.CANONICAL_BOOT_SEED)

    endpoint = AB.endpoint_propagation_benchmark()
    endpoint["source_sha256"] = src
    endpoint["_provenance"] = dict(provenance)

    loss = AB.comparator_loss_robustness()
    loss["source_sha256"] = src
    loss["_provenance"] = dict(provenance)

    complete = AB.transfer_skill_vs_baselines(include_off_grid=True)
    matched = AB.transfer_skill_vs_baselines(include_off_grid=False)
    corpus = _corpus_contract(complete, matched, src, provenance)
    return {"endpoint": endpoint, "corpus": corpus, "loss": loss}


def _corpus_contract(complete, matched, src, provenance) -> dict:
    """The two defensible corpus contracts, side by side, with the adopted one named."""
    from puckworks.validation.slow import angeloni_bracket as AB
    from puckworks import data as d

    def arm(res, include_off_grid):
        manifest = TC.build_transfer_corpus_manifest(d.angeloni_bioactives(),
                                                     include_off_grid=include_off_grid)
        resampling = {}
        for name in TC.SCHEME_ORDER:
            b = AB.paired_clustered_bootstrap(res["records"], B=AB.CANONICAL_BOOT_B,
                                              seed=AB.CANONICAL_BOOT_SEED, unit=name)
            resampling[name] = dict(
                unit=name, role=TC.SCHEMES[name]["role"], n_clusters=b["n_clusters"],
                n_strata=b["n_strata"], observed_mean_delta_pp=b["observed_mean_delta_pp"],
                interval=b["interval"], B=b["B"], seed=b["seed"],
                interval_kind=b["interval_kind"])
        out = dict(
            corpus=manifest,
            support_set=manifest["support_set"],
            pooled_model_mape=res["pooled_model_mape"],
            pooled_const_mape=res["pooled_const_mape"],
            pooled_lookup_mape=res["pooled_lookup_mape"],
            skill_vs_const=res["skill_vs_const"],
            paired_difference_pp=res["paired_model_minus_const_mean_pp"],
            paired_median_pp=res["paired_model_minus_const_median_pp"],
            n_points=res["n_points"],
            n_model_worse_than_const=res["n_model_worse_than_const"],
            pooled_by_grind=res["pooled_by_grind"],
            per_fit=res["per_fit"],
            resampling=resampling)
        if include_off_grid:
            out["off_grid_only"] = _off_grid_only(res)
        else:
            out["off_grid_only"] = None
        return out

    return dict(
        schema_version=TC.SCHEMA_VERSION,
        source_sha256=src,
        question=(
            "Round-7 P0-3: the headline benchmark filtered every grind to on_grid==True, "
            "excluding eight coarse/fine off-grid validation records (24 named-solute "
            "observations) while Table 1 claimed the C/F corpus was held out in its entirety. "
            "Both defensible contracts are evaluated here; the COMPLETE corpus was adopted as "
            "the headline, and the matched on-grid subset is retained as the secondary corpus "
            "and as the support on which the same-(T,p) lookup comparator is defined."),
        adopted="complete_corpus",
        endpoint=TC.endpoint_object(),
        matched_on_grid=arm(matched, False),
        complete_corpus=arm(complete, True),
        _provenance=dict(provenance))


def _off_grid_only(res) -> dict:
    """The eight off-grid records scored alone — the increment the complete corpus adds."""
    import numpy as np
    recs = [r for r in res["records"] if not r["on_grid"]]
    em = np.array([r["e_model"] for r in recs], float)
    ec = np.array([r["e_const"] for r in recs], float)
    return dict(
        n_points=len(recs),
        sample_ids=sorted({r["sample"] for r in recs}),
        model_mape=round(float(em.mean()), 3),
        const_mape=round(float(ec.mean()), 3),
        paired_difference_pp=round(float((em - ec).mean()), 3),
        n_model_worse=int((em > ec + 1e-9).sum()))


def write() -> list[str]:
    """Build, validate in memory, then replace all three artefacts atomically."""
    built = build()
    staged = {ENDPOINT_JSON: built["endpoint"], CORPUS_JSON: built["corpus"],
              LOSS_JSON: built["loss"]}

    tmp_paths = {}
    try:
        for path, obj in staged.items():
            tmp = path.with_suffix(path.suffix + ".tmp")
            tmp.write_text(_dump(obj), encoding="utf-8")
            tmp_paths[path] = tmp
        # Validate the STAGED tree before touching anything committed.
        backups = {p: p.read_text(encoding="utf-8") if p.exists() else None for p in staged}
        for path, tmp in tmp_paths.items():
            os.replace(tmp, path)
        tmp_paths.clear()
        problems = check()
        if problems:
            for path, text in backups.items():
                if text is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(text, encoding="utf-8")
            return ["regenerated artefacts failed validation; the tree was rolled back"] + problems
        return []
    finally:
        for tmp in tmp_paths.values():
            tmp.unlink(missing_ok=True)


def recompute() -> list[str]:
    """Rebuild the numbers and report every field that moved, without writing."""
    problems = check()
    built = build()
    for label, path, fresh in (("endpoint", ENDPOINT_JSON, built["endpoint"]),
                               ("corpus-contract", CORPUS_JSON, built["corpus"]),
                               ("comparator-loss", LOSS_JSON, built["loss"])):
        committed = _load(path)
        for key in ("rows", "complete_corpus", "matched_on_grid"):
            if key in fresh and TC.canonical_json(fresh.get(key)) != \
                    TC.canonical_json(committed.get(key)):
                problems.append("%s: `%s` differs from the committed artefact — inspect the diff "
                                "and explain every moved value before writing" % (label, key))
    return problems


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true", help="fast source→artefact and schema checks")
    g.add_argument("--recompute", action="store_true", help="also re-run the producers (slow)")
    g.add_argument("--write", action="store_true", help="re-run and rewrite atomically (slow)")
    args = ap.parse_args(argv)

    if args.write:
        problems, verb = write(), "write"
    elif args.recompute:
        problems, verb = recompute(), "recompute"
    else:
        problems, verb = check(), "check"

    if problems:
        print("Paper A transfer artefacts FAILED (%s):" % verb, file=sys.stderr)
        for p in problems:
            print("  - %s" % p, file=sys.stderr)
        return 1
    print("Paper A transfer artefacts OK (%s)." % verb)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
