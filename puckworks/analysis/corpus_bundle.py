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


def _claim_bundle(snapshot, census, atlas):
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
        "exploratory": snapshot.classification != "publication-freeze",
        "corpus": {
            "n_shots": allc["n_shots"],
            "n_unique_users": allc["n_unique_users"],
            "max_shots_per_user": allc["max_shots_per_user"],
            "n_shots_one_per_user": ospu["n_shots"],
        },
        "pressure_tracking": {
            "n_eligible": ov["n_shots"],
            "rmse_bar_median": ov.get("rmse_bar", {}).get("median"),
            "rmse_bar_iqr": [ov.get("rmse_bar", {}).get("p25"),
                             ov.get("rmse_bar", {}).get("p75")],
            "n_eligible_one_per_user": ospu_atlas["n_shots"],
            "note": "tracking-behaviour distribution, NOT a machine ranking",
        },
        "caveats": [
            "recent-updated public window, not the historical corpus",
            "integration_source is largely unknown/inferred (no source-side enum)",
            "flow tracking withheld until quantity kinds are resolved (pressure only)",
            "user/profile concentration is high — see one-shot-per-user figures",
        ],
    }


def build_bundle(snapshot, dst_dir=None, require_freeze=False):
    """Build (and optionally write) the corpus analysis bundle. Returns the bundle dict with a
    content hash. `require_freeze=True` refuses a non-publication-freeze snapshot."""
    if require_freeze and snapshot.classification != "publication-freeze":
        raise RuntimeError(
            "a publication bundle requires a 'publication-freeze' snapshot; got %r"
            % snapshot.classification)
    manifest = snapshot.manifest()
    census = visualizer_census.corpus_census(snapshot)
    atlas = controller_atlas.pressure_atlas(snapshot)
    eligibility = {p: eligibility_report(snapshot, p) for p in sorted(PROFILES)}
    products = {
        "census": census,
        "pressure_atlas": atlas,
        "eligibility": eligibility,
        "claim_bundle": _claim_bundle(snapshot, census, atlas),
    }
    bundle = {
        "bundle_schema_version": 1,
        "snapshot_name": snapshot.name,
        "classification": snapshot.classification,
        "exploratory": snapshot.classification != "publication-freeze",
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
