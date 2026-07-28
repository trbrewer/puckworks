"""Exporters + claim-card renderer + CLI (PV-00 §5.3, §5.6).

`export()` regenerates every public number from its Producer (so nothing is ever
copied from a paper by hand), stamps the source commit, and writes JSON, CSV, and
Markdown claim cards. One command regenerates the whole public layer:

    python -m puckworks.public export --out docs/public/generated [--slow]

Without --slow, Producers flagged slow (PDE/GPU solves) keep their stored snapshot
and are marked stale-unchecked in the output.
"""
from __future__ import annotations
import csv
import io
import json
import os
import subprocess
from .claims import PUBLIC_CLAIMS


def _source_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"],
                                       stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "UNKNOWN"


#: Fields that constitute a claim's PAYLOAD -- what it asserts. Provenance stamps are excluded by
#: construction, so re-verifying an unchanged claim at a new commit does not change its hash.
_PAYLOAD_EXCLUDED = ("generated_from_commit", "last_verified_against_commit", "source_commit",
                     "payload_sha256")


def payload_hash(claim) -> str:
    """A content hash over everything the claim asserts, excluding provenance stamps.

    This is what makes "immutable generation commit" mean anything: the generation commit may be
    carried forward from a previous export only while the payload hash is unchanged.
    """
    import dataclasses
    import hashlib

    def plain(o):
        if dataclasses.is_dataclass(o) and not isinstance(o, type):
            return {f.name: plain(getattr(o, f.name)) for f in dataclasses.fields(o)
                    if f.name not in _PAYLOAD_EXCLUDED}
        if isinstance(o, dict):
            return {str(k): plain(v) for k, v in sorted(o.items())}
        if isinstance(o, (list, tuple)):
            return [plain(v) for v in o]
        if callable(o):
            return getattr(o, "__qualname__", repr(o))
        return o

    blob = json.dumps(plain(claim), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _prior_provenance(out_dir) -> dict:
    """{claim_id: {payload_sha256, generated_from_commit}} read from the committed artifact.

    Fourth review P0-8: `generated_from_commit` was stamped only when it was `None`, but claims are
    rebuilt from source in every fresh process, where it is ALWAYS `None`. "Immutable" therefore
    held only within a single Python object's lifetime -- every export silently reset the
    generation commit to HEAD. Persisting it means reading what the previous export wrote.
    """
    path = os.path.join(out_dir, "claims.json")
    try:
        with open(path, encoding="utf-8") as fh:
            prior = json.load(fh)
    except (OSError, ValueError):
        return {}
    rows = prior.get("claims", prior) if isinstance(prior, dict) else prior
    out = {}
    for r in rows if isinstance(rows, list) else []:
        cid = r.get("claim_id")
        if cid:
            out[cid] = {"payload_sha256": r.get("payload_sha256"),
                        "generated_from_commit": r.get("generated_from_commit")}
    return out


def regenerate(claims=None, run_slow=False, out_dir="docs/public/generated"):
    """Return (claims, drift) with numeric_result recomputed from each Producer.
    `drift` lists (claim_id, key, snapshot, live) where a regenerated value differs
    from the stored snapshot — the staleness guard (a changed harness result must
    invalidate the card, PV-00 §5.7)."""
    # Copy before stamping. `PUBLIC_CLAIMS` are module-level singletons, so writing provenance
    # onto them made every export a process-wide side effect: an export into a scratch directory
    # left the real claims carrying that run's commit stamps.
    import copy as _copy
    claims = _copy.deepcopy(list(PUBLIC_CLAIMS if claims is None else claims))
    commit = _source_commit()
    prior = _prior_provenance(out_dir)
    drift = []
    for c in claims:
        if c.producer.slow and not run_slow:
            continue
        live = c.producer.compute()
        for k, v in live.items():
            snap = c.numeric_result.get(k)
            if isinstance(v, (int, float)) and isinstance(snap, (int, float)):
                # staleness guard: flag a MEANINGFUL shift (the card's rounded number
                # would change), not sub-percent float rounding of the display value.
                tol = max(1e-3, 5e-3 * abs(float(snap)))
                if abs(float(v) - float(snap)) > tol:
                    drift.append((c.claim_id, k, snap, round(float(v), 4)))
            elif v != snap:
                drift.append((c.claim_id, k, snap, v))
            # keep the authored (display-rounded) snapshot; the exporter writes it
            if not (isinstance(v, (int, float)) and isinstance(snap, (int, float))):
                c.numeric_result[k] = v

    # Provenance is stamped AFTER the payload is final, so the hash covers regenerated values too.
    for c in claims:
        h = payload_hash(c)
        c.payload_sha256 = h
        was = prior.get(c.claim_id) or {}
        # Carry the generation commit forward only while the payload is byte-identical; a changed
        # payload is a NEW generation, whatever the previous artifact said.
        if was.get("payload_sha256") == h and was.get("generated_from_commit"):
            c.generated_from_commit = was["generated_from_commit"]
        else:
            c.generated_from_commit = commit
        c.last_verified_against_commit = commit
        c.source_commit = c.generated_from_commit     # deprecated alias, kept for consumers
    return claims, drift


def to_json(claims) -> str:
    return json.dumps([c.to_dict() for c in claims], indent=2, default=str)


def to_csv(claims) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["claim_id", "headline", "key", "value", "unit", "evidence_strength",
                "badge", "dataset_manifest_ids", "source_commit"])
    for c in claims:
        for k, v in c.numeric_result.items():
            w.writerow([c.claim_id, c.headline, k, v, c.units.get(k, ""),
                        c.evidence_strength, c.badge,
                        ";".join(c.dataset_manifest_ids), c.source_commit or ""])
    return buf.getvalue()


def render_card(c) -> str:
    """A minimal claim card: headline, one result, scope sentence, reproduction."""
    nums = "; ".join(f"**{k}** = {v} {c.units.get(k, '')}".strip()
                     for k, v in c.numeric_result.items())
    dials = " · ⚠ grinder-dial: non-portable" if c.compares_grinder_dials else ""
    return (
        f"### {c.claim_id} — {c.headline}\n\n"
        f"`[{c.badge}]` · evidence: **{c.evidence_strength}**{dials}\n\n"
        f"**Question.** {c.public_question}\n\n"
        f"**Finding.** {c.plain_language_finding}\n\n"
        f"**Numbers.** {nums}\n\n"
        f"**Uncertainty / sensitivity.** {c.uncertainty_or_sensitivity}\n\n"
        f"**Validity.** {c.validity_range}\n\n"
        f"**Caveat (scope sentence).** {c.primary_caveat}\n\n"
        f"**Practical implication.** {c.practical_implication}\n\n"
        f"**Datasets.** {', '.join(c.dataset_manifest_ids)} · "
        f"**Generated by** `{c.producer.ref()}`"
        f"{' (slow)' if c.producer.slow else ''} · commit `{(c.source_commit or '')[:10]}`\n\n"
        f"**Reproduce.** `{c.reproduction}`\n"
    )


def to_markdown(claims) -> str:
    head = ("# puckworks — public claim cards (generated)\n\n"
            "*Generated by `python -m puckworks.public export`. Every number is "
            "produced by a named function (see each card's *Generated by*); "
            "evidence-strength labels are carried UNCHANGED from the scientific "
            "analyses. Do not hand-edit — regenerate.*\n\n")
    return head + "\n---\n\n".join(render_card(c) for c in claims)


def export(out_dir="docs/public/generated", run_slow=False):
    claims, drift = regenerate(run_slow=run_slow, out_dir=out_dir)
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "claims.json"), "w") as f:
        f.write(to_json(claims))
    with open(os.path.join(out_dir, "claims.csv"), "w") as f:
        f.write(to_csv(claims))
    with open(os.path.join(out_dir, "claims.md"), "w") as f:
        f.write(to_markdown(claims))
    return dict(out_dir=out_dir, n_claims=len(claims), drift=drift,
                slow_run=run_slow)


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="puckworks.public")
    sub = p.add_subparsers(dest="cmd")
    e = sub.add_parser("export", help="regenerate + write JSON/CSV/Markdown cards")
    e.add_argument("--out", default="docs/public/generated")
    e.add_argument("--slow", action="store_true", help="also run slow Producers")
    args = p.parse_args(argv)
    if args.cmd == "export":
        r = export(args.out, run_slow=args.slow)
        print(f"wrote {r['n_claims']} claims -> {r['out_dir']} "
              f"(slow={r['slow_run']})")
        if r["drift"]:
            print("DRIFT (snapshot != regenerated):")
            for cid, k, snap, live in r["drift"]:
                print(f"  {cid}.{k}: snapshot {snap} -> live {live}")
    else:
        p.print_help()


if __name__ == "__main__":
    main()
