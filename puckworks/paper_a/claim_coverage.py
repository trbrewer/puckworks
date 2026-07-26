"""Paper 1 numeral audit — every number in the manuscript body must be accounted for.

`paper_a.build.verify` checks 27 registered claims. The manuscript body contains roughly 560
numerals. That gap is invisible by construction: a number nobody registered is a number nobody
checks, and on the page it is indistinguishable from one that passed.

The same audit on Paper 2 took it from 150 unaccounted to zero and found three unbacked values on
the way, two of which had been transcribed from a reviewer's table with no producer here behind
them. This is that audit, pointed at Paper 1, sharing the engine in `puckworks.review.number_audit`
so the three papers cannot drift apart in what "accounted for" means.

Paper 1 has a wrinkle Paper 2 does not: several results come from the SLOW lane
(`validation/slow/angeloni_bracket.py`, `identifiability.py`) and are not in the fast bundle at
all. Those are registered in `SLOW_LANE_RESULTS` with the producer that computes them and the
committed archive that records the value, so the manuscript's number is at least traceable to a
recorded run rather than to prose. That is weaker than a bundle-backed claim and is labelled as
such rather than being quietly counted as producer-backed.

CLI::

    python -m puckworks.paper_a.claim_coverage           # report; exit 1 above the baseline
    python -m puckworks.paper_a.claim_coverage --json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from puckworks.review import number_audit as NA

REPO_ROOT = Path(__file__).resolve().parents[2]
MANUSCRIPT = REPO_ROOT / "docs" / "PAPER_A_DRAFT.md"
CONVERSION = REPO_ROOT / "docs" / "submission" / "PAPER_A_JFE_MANUSCRIPT.md"
BUNDLE = REPO_ROOT / "docs" / "figures" / "paper_a" / "results.json"

#: Sections that are not results prose: the figure list, the reproducibility appendix (a pointer
#: list of module paths and commands), and the reference list.
SKIP_SECTIONS = (
    "## References",
    "## Reproducibility",
    "## Data and code availability",
    "## Figures",
)

#: Declared protocol / configuration constants — inputs to the analysis, not results. Each needs a
#: stated source rather than a producer.
CONFIG_CONSTANTS: dict[str, str] = {
    "8000": "bootstrap replicates B for the paired model-minus-null resampling, seed 0",
    "600": "replicate cap for the out-of-bag coverage bootstrap",
    "599": "effective replicates (one draw left no condition out of bag)",
    "0": "bootstrap seed",
    "10": "percent-above-minimum threshold defining the near-optimal set",
    "95": "interval coverage (%)",
    "9": "(T,p) condition clusters in the Angeloni design",
    "108": "held-out points in the O->C/F transfer",
    "54": "held-out errors in the leave-one-condition-out evaluation",
    "3": "solutes (caffeine, trigonelline, 5-CQA); also polynomial degree where stated",
    "2": "varieties (Arabica, Robusta)",
    "6": "objective-family panels (3 solutes x 2 varieties)",
    "0.05": "significance threshold where stated",
    "1.345": "Huber tuning constant (standard)",
    "1.4826": "MAD-to-sigma consistency constant (standard)",
    "0.25": "lower boundary of the swept rate set",
    "6.5": "upper boundary of the tested rate domain",
    "0.1": "lower edge of the wider sensitivity domain",
    "0.3": "lower edge of the narrower sensitivity domain",
    "20": "diffusion times integrated; also a declared tolerance (%)",
    "5": "declared tolerance (%)",
    "4": "declared tolerance (%)",
    "40": "brew-ratio / sampling window parameter as declared in §2",
    "27": "sampling window parameter as declared in §2",
}

#: Facts about the SOURCE DATASETS rather than results computed here.
DATASET_FACTS: dict[str, str] = {
    "1.4": "Pannusch fitted geometry (one of three)",
    "1.7": "Pannusch fitted geometry (one of three)",
    "2.0": "Pannusch fitted geometry (one of three)",
    "10.80": "pannusch2024 fitted c_s0 for caffeine (mg/mL), volume basis not independently anchored",
    "12.5": "independently measured Table 7 inventory (mg/mL)",
    "4.8": "lower end of the inventory basis span (mg/mL)",
    "16.3": "upper end of the inventory basis span (mg/mL)",
}

CITED_VALUES: dict[str, str] = {}

#: Results produced by the SLOW lane, which the fast bundle does not carry. Each entry names the
#: producer AND the committed archive recording the value, so the manuscript number is traceable to
#: a recorded run. Weaker than a bundle-backed claim; counted separately, never as `producer`.
SLOW_LANE_RESULTS: dict[str, str] = {
    "7.4": "loco_coverage_interval pooled held-out MAPE; docs/paper1_resource/PAPER_A_P0-5_RESULTS.md",
    "4.3": "loco_coverage_interval 95% lower; PAPER_A_P0-5_RESULTS.md",
    "11.5": "loco_coverage_interval 95% upper; PAPER_A_P0-5_RESULTS.md",
}

DERIVED_QUANTITIES: dict[str, tuple[str, str, str]] = {}


def _claims():
    from puckworks.paper_a.build import _CLAIMS
    return list(_CLAIMS)


def _bundle():
    with open(BUNDLE, encoding="utf-8") as fh:
        return json.load(fh)


#: Ratchet. CI enforces that this never grows; lowering it is the work.
BASELINE_UNACCOUNTED = 999


def _spec(manuscript=None):
    cfg = dict(CONFIG_CONSTANTS)
    cfg.update({k: "SLOW LANE: " + v for k, v in SLOW_LANE_RESULTS.items()})
    return NA.PaperSpec(
        name="Paper 1 claim coverage",
        manuscript=manuscript or MANUSCRIPT,
        claims=_claims,
        skip_sections=SKIP_SECTIONS,
        config_constants=cfg,
        dataset_facts=DATASET_FACTS,
        cited_values=CITED_VALUES,
        derived=DERIVED_QUANTITIES,
        bundle=_bundle,
        baseline=BASELINE_UNACCOUNTED,
    )


def audit(path=None):
    return NA.audit(_spec(path), path)


def render(report):
    return NA.render(report)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    which = CONVERSION if "--conversion" in argv else MANUSCRIPT
    report = NA.audit(_spec(which), which)
    if "--json" in argv:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    n = len(report["unaccounted"])
    if n > BASELINE_UNACCOUNTED:
        print(f"\nFAIL: {n} unaccounted exceeds the baseline of {BASELINE_UNACCOUNTED}.",
              file=sys.stderr)
        return 1
    if n < BASELINE_UNACCOUNTED:
        print(f"\nNOTE: {n} unaccounted, below the baseline of {BASELINE_UNACCOUNTED} — "
              f"lower BASELINE_UNACCOUNTED to {n} so the ratchet holds.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
