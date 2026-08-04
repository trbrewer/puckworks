"""Insight Foundry CLI.

    python -m puckworks.insights build      # build in memory, print the counts
    python -m puckworks.insights write      # (re)generate every tracked artifact + the pack
    python -m puckworks.insights verify     # staleness + hand-edit check (used by the tests)
    python -m puckworks.insights card I-007 # materialise one candidate card for a shortlisted id

`card` exists because the blueprint's per-candidate files are for SHORTLISTED candidates only
(§12 Stage B). Writing all 89 seeds as tracked cards would be the governance re-expansion §19.6
warns against — a card is created when a person decides to work one.
"""
from __future__ import annotations

import argparse
import json
import sys

from . import candidates as CD, export as EX, schema as S

CANDIDATE_DIR_REL = "docs/insights/candidates"


def _card_markdown(c) -> str:
    """One candidate card, in the blueprint §10.2 shape."""
    def block(title, body):
        return ["## %s" % title, "", body or "_not yet written — this is a seed._", ""]

    out = ["# %s — %s" % (c.id, c.title), "",
           "> Generated from the insight portfolio at commit `%s`. A card is created when a "
           "person decides to work a candidate; everything below the Question is a STARTING "
           "POINT, not a result." % (c.source_commit or "UNKNOWN")[:10], ""]
    out += block("Question", c.question)
    out += block("Insight type", ", ".join(c.insight_types))
    out += block("Target audiences", ", ".join(c.audience_tracks))
    out += block("Why it may matter", c.why_it_may_matter)
    out += block("Why it may be surprising", c.why_it_may_surprise)
    out += block("Models, datasets, and other entities",
                 "\n".join("- `%s`" % e for e in c.entity_ids))
    out += block("Tension rows", ", ".join(c.tension_ids))
    out += block("Existing evidence", "\n".join("- %s" % e for e in c.existing_evidence))
    out += block("Strongest alternative explanation", c.strongest_alternative)
    out += block("Cheap scientific screen", c.cheap_test)
    out += block("Minimum viable figure", c.minimum_figure)
    out += block("Decision rule",
                 "- **SURVIVE if** %s\n- **RETIRE if** %s\n- **INCONCLUSIVE if** %s"
                 % (c.survive_if, c.retire_if, c.inconclusive_if))
    out += block("Stop condition", c.stop_condition)
    out += block("Possible outputs",
                 "\n".join("- %s" % t for t in c.audience_tracks) or "- undecided")
    out += block("External novelty search terms",
                 "\n".join("- %s" % t for t in c.novelty_search_terms) +
                 "\n\n_Run only after the candidate survives its cheap screen (blueprint §13.4)._")
    out += block("Status", "%s\n\nTransitions require a one-line reason appended here." % c.status)
    return "\n".join(out) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m puckworks.insights",
                                 description="Puckworks Insight Foundry")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build", help="build in memory and print counts")
    w = sub.add_parser("write", help="regenerate every tracked artifact and the ChatGPT pack")
    w.add_argument("--stamp-time", action="store_true",
                   help="add a wall-clock timestamp to the snapshot manifest (untracked exports "
                        "only — it makes the tracked artifacts diff on every run)")
    sub.add_parser("verify", help="staleness + hand-edit check")
    c = sub.add_parser("card", help="materialise a candidate card for a shortlisted id")
    c.add_argument("candidate_id", help="e.g. I-007")
    args = ap.parse_args(argv)

    if args.cmd == "build":
        state = EX.build_all()
        print(json.dumps({"commit": state["corpus"]["commit"],
                          "counts": state["corpus"]["counts"],
                          "tensions": len(state["tensions"]),
                          "candidates": len(state["candidates"]),
                          "portfolio": CD.portfolio_summary(state["candidates"]),
                          "warnings": len(state["corpus"]["warnings"])}, indent=2))
        return 0

    if args.cmd == "write":
        written = EX.write(stamp_time=args.stamp_time)
        for rel in written:
            print("wrote %s" % rel)
        print("%d files" % len(written))
        return 0

    if args.cmd == "verify":
        problems = EX.verify()
        for p in problems:
            print(p)
        print("OK" if not problems else "%d problem(s)" % len(problems))
        return 1 if problems else 0

    if args.cmd == "card":
        state = EX.build_all()
        match = [c for c in state["candidates"] if c.id == args.candidate_id]
        if not match:
            print("no candidate %r in the current portfolio" % args.candidate_id)
            return 1
        card = match[0]
        rel = "%s/%s_%s.md" % (CANDIDATE_DIR_REL, card.id,
                               "".join(ch if ch.isalnum() else "_"
                                       for ch in card.title.lower())[:48].strip("_"))
        path = S.REPO_ROOT / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_card_markdown(card), encoding="utf-8")
        print("wrote %s" % rel)
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
