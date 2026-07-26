"""Evidence ontology for the Paper B2 flow ladder (review 4.12 / P0.9).

The manuscript retired several overclaims, but the CODE kept them -- "parameter-free", "flexible
floor", "ZERO-param", "genuinely held-out" -- in docstrings, result keys and verdict strings. That is
not stylistic: regeneration can push obsolete evidentiary language back into tables, JSON, notebooks
and later papers, undoing a correction that was only ever made in prose.

The fix is to name what each branch's relationship to the target ACTUALLY is. A branch is not
"parameter-free" because it has no coefficient fitted to the scored trace; it may still carry
constants estimated from the same rig, the same campaign, or the target itself upstream.
"""
from __future__ import annotations

#: Ordered from most target-dependent to least. A label describes the branch's ACCESS to the
#: quantity being scored, not its parameter count.
EVIDENCE_LABELS = {
    "same_trace_fitted":
        "Free coefficients fitted to the very trace being scored. In-sample by construction; a "
        "descriptive benchmark, never a predictive claim. (The degree-3 polynomial null.)",
    "same_campaign_target_informed":
        "No coefficient fitted directly to the scored trace, but upstream constants derive from the "
        "same campaign -- and, for Phi(t), partly from the target itself via TDS(t) x Q(t). NOT "
        "parameter-free and NOT held out. (The poroelastic Phi(t) branch.)",
    "equilibrium_calibration_lopo":
        "The EQUILIBRIUM calibration excludes the held-out unit; the temporal construction is "
        "retained. A calibration-channel sensitivity, not held-out trace prediction.",
    "shot_cross_fitted":
        "The held-out SHOT is excluded from every stage that can be rebuilt without it. Currently "
        "attainable for the equilibrium channel only; the dissolved-mass sigmoid cannot be rebuilt "
        "because the TDS replicates are not shot-matched.",
    "shot_held_out_null":
        "A NULL comparator refitted on the other shots only and scored on the excluded shot. What "
        "is withheld is stated per protocol, not asserted. This is a property of the comparator's "
        "protocol, not evidence that any mechanistic branch is held out.",
    "segment_held_out_null":
        "A NULL comparator refitted on the remaining segments of the SAME shot and scored on an "
        "excluded contiguous time interval. Tests interpolation of a temporal gap, a different "
        "question from predicting a new shot.",
    "external_validation":
        "Scored against data from a different rig/campaign with no shared fitted constants. Not "
        "attained anywhere in this paper.",
}

#: Which label each ladder branch actually carries.
BRANCH_EVIDENCE = {
    "rung1_const": "same_trace_fitted",          # LS-optimal constant IN the scored window
    "rung1b_longrun_const": "same_campaign_target_informed",
    "rung3_static": "same_campaign_target_informed",
    "rung4_phi_of_t": "same_campaign_target_informed",
    "flexible_cubic": "same_trace_fitted",
    "lopo_equilibrium": "equilibrium_calibration_lopo",
    "shot_loso_equilibrium": "shot_cross_fitted",
    # P0.4 null comparators. They are held out; the MECHANISTIC branches above still are not.
    "penalized_spline_loso": "shot_held_out_null",
    "penalized_spline_segment": "segment_held_out_null",
}

#: Language that must not describe any branch in this paper's code or prose. Each maps to the
#: reason it was retired, so a reviewer can see WHY rather than just that it is banned.
RETIRED_LANGUAGE = {
    "parameter-free": "Phi(t) carries rig constants and target-derived sigmoid parameters upstream; "
                      "'no coefficient fitted to the scored trace' is the accurate statement.",
    "zero-param": "Same reason: a zero free-parameter COUNT is not the same as no target access.",
    "flexible floor": "The same-trace cubic is a descriptive benchmark, not a floor -- it is neither "
                      "a lower bound nor predictive.",
    "genuinely held-out": "Retired for the MECHANISTIC branches: only the equilibrium calibration "
                          "is withheld and the temporal template is retained, so those are not "
                          "held-out trace prediction. The P0.4 null comparators genuinely are "
                          "withheld, but they are described by their protocol "
                          "(shot_held_out_null / segment_held_out_null) rather than by this "
                          "phrase, so the phrase cannot leak back onto a mechanistic branch.",
}


def label_for(branch):
    """The evidence label for a ladder branch, or None if the branch is unknown."""
    return BRANCH_EVIDENCE.get(branch)


def describe(branch):
    """Human-readable evidence relationship for a branch."""
    lab = label_for(branch)
    return None if lab is None else EVIDENCE_LABELS[lab]


def is_target_informed(branch):
    """True when the branch has ANY access to the scored target, direct or upstream.

    This is the predicate the review asked to be testable: a branch for which this is True must
    never be described as parameter-free or independently held out."""
    return label_for(branch) in {"same_trace_fitted", "same_campaign_target_informed",
                                 "equilibrium_calibration_lopo"}


def is_withheld_null(branch):
    """True for the P0.4 comparators, whose fitting data excludes the scored points entirely."""
    return label_for(branch) in {"shot_held_out_null", "segment_held_out_null"}
