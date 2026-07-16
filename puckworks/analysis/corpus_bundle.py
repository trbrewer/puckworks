"""WP4 / PR6 — assemble the corpus analysis bundle from a CorpusSnapshot.

Runs the P0 census, the P1-dictionary-backed pressure P2 atlas, and every eligibility profile,
then wraps them with a claim bundle and a bundle manifest. A PUBLICATION bundle
(``require_freeze=True``) is refused unless the snapshot is a ``publication-freeze`` — so
partial/moving results can never be dressed up as paper-grade. The claim bundle carries the
ecological-evidence ceiling explicitly (this corpus does NOT validate latent puck physics).
"""
import hashlib
import json
from pathlib import Path

from puckworks.analysis import visualizer_census, controller_atlas
from puckworks.analysis.visualizer_eligibility import PROFILES, eligibility_report

_CEILING = (
    "Permitted: corpus measurement/quality description, operating-envelope coverage, "
    "commanded-vs-achieved tracking behaviour, ecological associations, hypothesis "
    "generation. NOT permitted from Visualizer alone: validation of latent puck mechanisms, "
    "causal effects, ground-truth permeability/channeling labels, or proof that a particular "
    "physical model is correct."
)


def _sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _claim_bundle(snapshot, census, atlas, exploratory=True):
    """Headline numbers WITH denominators + sensitivity + the evidence ceiling. Deliberately
    reports one-shot-per-user alongside every all-shots number (contributor concentration)."""
    allc = census["results"]["all_shots"]
    ospu = census["results"]["one_shot_per_user"]
    ov = atlas["results"]["overall"]
    ospu_atlas = atlas["results"]["one_shot_per_user"]
    return {
        "evidence_ceiling": _CEILING,
        "snapshot_name": snapshot.name,
        "snapshot_classification": snapshot.classification,
        "exploratory": exploratory,
        "corpus": {
            "n_shots": allc["n_shots"],
            "n_unique_users": allc["n_unique_users"],
            "max_shots_per_user": allc["max_shots_per_user"],
            "n_shots_one_per_user": ospu["n_shots"],
        },
        "pressure_tracking": {
            "n_eligible": ov["n_shots"],
            "tw_mae_bar_median": ov.get("tw_mae_bar", {}).get("median"),
            "tw_rmse_bar_median": ov.get("tw_rmse_bar", {}).get("median"),
            "tw_rmse_bar_iqr": [ov.get("tw_rmse_bar", {}).get("p25"),
                                ov.get("tw_rmse_bar", {}).get("p75")],
            "frac_time_within_0p5bar_median": ov.get("frac_time_within_0p5bar", {}).get("median"),
            "n_eligible_one_per_user": ospu_atlas["n_shots"],
            "metric": "time-weighted, active-phase (pressure-atlas/v1)",
            "note": "tracking-behaviour distribution, NOT a machine ranking",
        },
        "caveats": [
            "recent-updated public window, not the historical corpus",
            "integration_source is largely unknown/inferred (no source-side enum)",
            "flow tracking withheld until quantity kinds are resolved (pressure only)",
            "user/profile concentration is high — see one-shot-per-user figures",
        ],
    }


def build_bundle(snapshot, dst_dir=None, require_freeze=False, receipt=None):
    """Build (and optionally write) the corpus analysis bundle. Returns the bundle dict with a
    content hash.

    `require_freeze=True` (WP1.2) demands a VERIFIED publication receipt — a
    ``corpus_freeze.PublicationReceipt`` with ``qualifies_for_publication``. A classification
    STRING on the snapshot can no longer unlock a publication bundle; only a passing
    materialize→verify does."""
    if require_freeze:
        ok = bool(receipt is not None and getattr(receipt, "qualifies_for_publication", False))
        if not ok:
            raise RuntimeError(
                "a publication bundle requires a VERIFIED publication receipt "
                "(corpus_freeze.freeze_verify on a publication-freeze snapshot); a "
                "classification label is not sufficient. got receipt=%r" % (receipt,))
    # publication status derives from the VERIFIED receipt, never from the snapshot label
    is_publication = bool(require_freeze and receipt is not None
                          and getattr(receipt, "qualifies_for_publication", False))
    manifest = snapshot.manifest()
    census = visualizer_census.corpus_census(snapshot)
    atlas = controller_atlas.pressure_atlas(snapshot)
    eligibility = {p: eligibility_report(snapshot, p) for p in sorted(PROFILES)}
    products = {
        "census": census,
        "pressure_atlas": atlas,
        "eligibility": eligibility,
        "claim_bundle": _claim_bundle(snapshot, census, atlas, exploratory=not is_publication),
    }
    bundle = {
        "bundle_schema_version": 2,
        "snapshot_name": snapshot.name,
        "classification": snapshot.classification,
        "exploratory": not is_publication,
        "publication_receipt_sha256": getattr(receipt, "receipt_sha256", None) if is_publication else None,
        "snapshot_manifest_sha256": manifest["manifest_sha256"],
        "products": products,
    }
    bundle["bundle_sha256"] = _sha(json.dumps(bundle, sort_keys=True, ensure_ascii=False,
                                              default=str))
    if dst_dir is not None:
        out = Path(dst_dir)
        out.mkdir(parents=True, exist_ok=True)
        (out / "snapshot_manifest.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
        for name, prod in products.items():
            (out / ("%s.json" % name)).write_text(
                json.dumps(prod, indent=2, sort_keys=True, default=str), encoding="utf-8")
        (out / "bundle.json").write_text(
            json.dumps(bundle, indent=2, sort_keys=True, default=str), encoding="utf-8")
    return bundle
