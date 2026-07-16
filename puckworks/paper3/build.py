"""Paper 3 build/verify — extends the existing release model to the registry resource (WP3.2).

`verify` is CI-runnable: it fails when the generated registry artifacts are stale/hand-edited
or the registry schema is invalid, and it lists the Paper 3 bundle contents (checking each
exists). It does NOT tag, deposit to Zenodo, or mint a DOI — those remain explicit human
actions, consistent with the existing release runbook.

CLI:  python -m puckworks.paper3.build verify | bundle
"""
import json
import sys
from pathlib import Path

import puckworks.models  # noqa: F401  (registers components)
from puckworks import registry as R
from puckworks.paper3 import registry_artifacts as gen

REPO_ROOT = Path(__file__).resolve().parents[2]

# files a Paper 3 resource bundle should include (relative to repo root). Generated artifacts
# are listed via the generator so the two never drift.
_BUNDLE_STATIC = [
    "docs/PAPER_3_PUCKWORKS_DRAFT.md",
    "docs/CLAIM_OWNERSHIP.md",
    "puckworks/data/MANIFEST.csv",
    "puckworks/data/visualizer/PROVENANCE.md",
    "puckworks/data/paper_b_evidence_matrix.csv",
    "puckworks/data/paper_b_evidence_dictionary.csv",
]


def bundle_contents():
    """Return the list of repo-relative files the Paper 3 bundle should contain."""
    gen_files = ["%s/%s" % (gen.GENERATED_REL, rel) for rel in sorted(gen.generate())]
    return sorted(_BUNDLE_STATIC + gen_files)


def verify(root=REPO_ROOT):
    """Return a report dict {ok, problems, warnings, bundle_missing}. `ok` is False on any
    hard problem: stale generated artifacts, an invalid registry enum, or a missing bundle
    file. Unclassified evidence_strength is a WARNING (known card-driven debt), not a failure."""
    root = Path(root)
    problems, warnings = [], []

    stale = gen.verify(root)
    if stale:
        problems.append("stale_generated_artifacts:%s" % ",".join(stale))

    for p in R.validate_registry():
        (warnings if "unclassified evidence_strength" in p else problems).append(p)

    bundle_missing = [f for f in bundle_contents() if not (root / f).exists()]
    if bundle_missing:
        problems.append("bundle_missing:%s" % ",".join(bundle_missing))

    return {
        "ok": not problems,
        "n_components": len(R.components()),
        "problems": problems,
        "warnings": warnings,
        "bundle_files": bundle_contents(),
        "bundle_missing": bundle_missing,
    }


def main(argv=None):   # pragma: no cover
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "verify"
    if cmd in ("bundle", "list-bundle"):
        if cmd == "bundle":
            print("NOTE: `bundle` only LISTS paths and is renamed to `list-bundle`. For the real "
                  "immutable archive use `python -m puckworks.paper3.archive create-archive`.",
                  file=sys.stderr)
        print(json.dumps(bundle_contents(), indent=2))
        return 0
    rep = verify()
    print(json.dumps(rep, indent=2))
    if rep["warnings"]:
        print("WARNINGS: %d unclassified-evidence components (card-driven debt)"
              % len(rep["warnings"]), file=sys.stderr)
    return 0 if rep["ok"] else 1


if __name__ == "__main__":   # pragma: no cover
    sys.exit(main())
