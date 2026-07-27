"""PublicClaim + Producer schema and the structural guardrails (PV-00 §5.2)."""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from importlib import import_module

# The four badges (PUBLIC_VALUE.md §3.1) — put ONE in the graphic, not the caption.
BADGES = ("OBSERVED", "RECONSTRUCTED", "PREDICTED", "EXPLORATORY_SIMULATION")

# PUBLIC evidence vocabulary. It is a DELIBERATELY COARSER, lay-facing vocabulary -- NOT the
# registry vocabulary. An earlier comment here claimed it "rides along UNCHANGED into public",
# which was false: the registry uses nine snake_case relations
# (puckworks.registry.EVIDENCE_STRENGTHS) and these are six spaced lay terms. Paper 3 review P0-2
# flagged the three drifting vocabularies; the mapping below makes the relationship explicit and
# testable instead of implied.
EVIDENCE_STRENGTHS = ("independent", "post-fit reconstruction", "verification",
                      "qualitative", "reference", "negative validation")

#: registry relation -> public lay term. Many-to-one BY DESIGN: the public surface deliberately
#: does not expose the registry's finer distinctions.
REGISTRY_TO_PUBLIC = {
    "controlled_independent": "independent",
    "within_campaign_held_out": "independent",
    "post_fit_reconstruction": "post-fit reconstruction",
    "source_curve_reproduction": "post-fit reconstruction",
    "code_verification": "verification",
    "sign_or_compatibility": "qualitative",
    "qualitative_capacity": "qualitative",
    "exploratory_synthesis": "qualitative",
    "proposed_experiment": "reference",
}

#: OUTCOME is a separate field from RELATION (Paper 3 §5, axis 2). `negative validation` is a
#: LEGACY COMPOUND: it encodes a *failed outcome*, not a kind of comparison, and the manuscript
#: says so explicitly ("a negative result ... is a failed outcome on some relation, not a relation
#: of its own"). It is retained because published public artifacts already carry it, but it MUST
#: decompose as below and must not be treated as a relation in new work.
PUBLIC_OUTCOMES = ("supported", "negative", "indeterminate")
LEGACY_COMPOUND_RELATIONS = {
    "negative validation": {"relation": "qualitative", "outcome": "negative"},
}


def _dig(obj, path):
    """Extract a value at a dotted path; segments may be dict keys or list indices."""
    cur = obj
    for seg in path.split("."):
        if isinstance(cur, (list, tuple)):
            cur = cur[int(seg)]
        else:
            cur = cur[seg]
    return cur


# --- dependency identity (Paper 3 review, step 0) ---------------------------------------------
# `components` was a flat list of FREE TEXT: of the 13 dependency edges across the public claims,
# only 2 resolved to a registry component id. The rest were prose labels ("foster2025 machine
# mode", "angeloni2023 endpoints", "kappa_t_ladder") that conflated three different kinds of thing
# -- registered components, producer functions, and datasets -- and could not be joined to the
# evidence graph at all. That is why an output could not carry the evidence relations of its
# dependencies: the dependencies were not identified.
DEPENDENCY_KINDS = ("component", "producer", "dataset")


@dataclass(frozen=True)
class ScopedEvidenceRef:
    """One evidence record attached to a dependency, WITH the scope it was demonstrated on.

    Mirrors `puckworks.paper3.evidence_graph.ScopedEvidence` on the public side. The scope is the
    load-bearing part: a relation belongs to a particular observable established by a particular
    gate, never to a component in general."""
    relation: str           # the REGISTRY relation (not the lay term)
    public_relation: str    # its lay rendering via REGISTRY_TO_PUBLIC
    scope: str              # the observable it was demonstrated on
    gate: str
    outcome: str            # supported | negative | indeterminate
    #: Stable id of the underlying EVIDENCE_LINKS record. Third review P0-1: a claim cannot SELECT
    #: the records that license it while those records are anonymous.
    evidence_id: str = ""
    #: The fit/evaluation design, kept separate from the comparison relation (third review P1-6):
    #: post_fit_same_data | same_campaign_not_held_out | within_campaign_held_out |
    #: independent_external | code_verification | not_empirical.
    fit_evaluation: str = ""
    #: Was the comparison reference a measured system at all?
    reality_facing: bool = False


@dataclass(frozen=True)
class Dependency:
    """One load-bearing input to a public claim, identified well enough to be looked up."""
    ref: str                # registry component id, producer dotted path, or dataset manifest id
    kind: str               # one of DEPENDENCY_KINDS
    role: str               # what it contributes to THIS claim
    evidence: tuple = ()    # ScopedEvidenceRef records; empty for producers and datasets

    def validate(self):
        errs = []
        if self.kind not in DEPENDENCY_KINDS:
            errs.append(f"dependency {self.ref!r}: kind {self.kind!r} not in {DEPENDENCY_KINDS}")
        if not self.role.strip():
            errs.append(f"dependency {self.ref!r}: no role recorded")
        for e in self.evidence:
            if e.relation not in REGISTRY_TO_PUBLIC:
                errs.append(f"dependency {self.ref!r}: unknown relation {e.relation!r}")
            if not e.scope.strip():
                errs.append(f"dependency {self.ref!r}: evidence record carries no scope")
        return errs



# --- claim-scoped evidence selection (third Paper 3 review P0-1) ------------------------------
@dataclass(frozen=True)
class ClaimEvidenceSelection:
    """The evidence records that license ONE claim's assertion.

    Before this, `_dep()` copied a component's ENTIRE evidence vector into every claim depending on
    it, and `evidence_profile()` flattened all of it into the claim's profile. Scope labels
    survived, but nothing prevented unrelated evidence from being presented as part of a claim's
    support: a component with code verification on one output, source-curve reproduction on
    another, and a compatibility check on a third contributed all three labels to any claim naming
    it, leaving the reader to infer which record was load-bearing.

    That is an evidence INVENTORY, not a claim-support relation. The paper's novelty claim is not
    that evidence records exist but that they CONSTRAIN what may be asserted, which requires an
    executable link between a claim and the exact records licensing its observable and verb.
    """
    dependency_ref: str             # which Dependency these records belong to
    evidence_ids: tuple             # the exact ScopedEvidenceRef.evidence_id values relied upon
    claim_observable: str           # what THIS claim is about
    claim_domain: str               # the conditions it is asserted over
    role_in_claim: str              # one of LICENSING_ROLES
    rationale: str = ""             # why these records are commensurate with the claim

    def validate(self):
        errs = []
        if not self.evidence_ids:
            errs.append(f"selection for {self.dependency_ref!r}: no evidence ids selected")
        for f in ("claim_observable", "claim_domain", "role_in_claim"):
            if not str(getattr(self, f)).strip():
                errs.append(f"selection for {self.dependency_ref!r}: {f} is empty")
        if self.role_in_claim and self.role_in_claim not in LICENSING_ROLES:
            errs.append(f"selection for {self.dependency_ref!r}: role_in_claim "
                        f"{self.role_in_claim!r} not in {LICENSING_ROLES}")
        return errs


#: What a component contributes to a claim. The badge describes how the claim's REPORTED VALUE was
#: produced, so a model that only supplies a comparator the finding is stated against does not turn
#: a measured result into a model output.
LICENSING_ROLES = (
    "produces_reported_value",   # the model output IS the number the claim reports
    "comparator_context",        # supplies a reference/timescale the measured finding is read against
    "diagnosed_subject",         # the claim is ABOUT this model's behaviour (e.g. a failed composition)
)

#: Badge derivation (third review P0-2). The manuscript said badges are "computed deterministically
#: from three authored evidence fields" and "never authored on its own", while `PublicClaim`
#: REQUIRED a badge argument, the seeded claims hard-coded values, and `validate()` only checked
#: membership in the four-item vocabulary. There was no derivation function at all.
#:
#: Derivation is conservative and FAILS CLOSED: an ambiguous or mixed combination raises rather
#: than selecting the strongest compatible badge.
_HELD_OUT_DESIGNS = ("within_campaign_held_out", "independent_external")
_RECONSTRUCTION_DESIGNS = ("post_fit_same_data", "same_campaign_not_held_out")


def derive_badge(claim) -> tuple:
    """Return ``(badge, rationale, limiting_dependency)`` from a claim's SELECTED evidence.

    * ``OBSERVED`` -- the claim reports a directly measured value and attributes no model
      prediction to it: it has no component dependency carrying reality-facing model evidence.
    * ``RECONSTRUCTED`` -- model output scored on fit data, source-generated curves, or
      same-campaign information without a qualifying held-out design.
    * ``PREDICTED`` -- every load-bearing model dependency has selected evidence at the claim's
      observable under a declared held-out or independent design, and every outcome is supported.
    * ``EXPLORATORY_SIMULATION`` -- composition or model-generated output without sufficient
      empirical evaluation for the claim.
    """
    selected = claim.selected_evidence()
    model_deps = [d for d in claim.dependencies if d.kind == "component"]
    roles = {s.dependency_ref: s.role_in_claim for s in claim.evidence_selections}

    if not model_deps:
        return ("OBSERVED",
                "no component dependency: the claim reports measured or dataset-derived values "
                "and attributes no model prediction to them", None)

    # A component that only supplies a comparator does not make the reported value a model output.
    producing = [d for d in model_deps
                 if roles.get(d.ref, "produces_reported_value") != "comparator_context"]
    if claim.evidence_selections and not producing:
        return ("OBSERVED",
                "every component dependency is a comparator/context reference; the reported value "
                "is measured or dataset-derived and no model prediction is attributed to it", None)
    model_deps = producing or model_deps

    if not selected:
        return ("EXPLORATORY_SIMULATION",
                "component dependencies are present but no evidence records are selected for this "
                "claim's observable, so nothing licenses a stronger verb", model_deps[0].ref)

    if any(e["outcome"] == "negative" for e in selected):
        limiting = next(e["dependency"] for e in selected if e["outcome"] == "negative")
        return ("EXPLORATORY_SIMULATION",
                "a selected evidence record carries a NEGATIVE outcome; a negative result cannot "
                "license a supported verb", limiting)

    if any(e["outcome"] == "indeterminate" for e in selected):
        limiting = next(e["dependency"] for e in selected if e["outcome"] == "indeterminate")
        return ("EXPLORATORY_SIMULATION",
                "a selected evidence record is indeterminate (blocked, unresolved or not run)",
                limiting)

    # Every load-bearing component must itself be covered by a selection.
    covered = {e["dependency"] for e in selected}
    uncovered = [d.ref for d in model_deps if d.ref not in covered]
    if uncovered:
        return ("EXPLORATORY_SIMULATION",
                f"load-bearing component {uncovered[0]!r} has no selected evidence for this claim",
                uncovered[0])

    # An exploratory synthesis or a composition is model-generated output, whatever the outcome of
    # the diagnostic that examined it. PV-05 is the case: its diagnostic gate PASSED (it correctly
    # diagnosed a failure), but the claim is still about a composition, not an evaluated prediction.
    relations = {e["relation"] for e in selected}
    if "exploratory_synthesis" in relations:
        return ("EXPLORATORY_SIMULATION",
                "the claim rests on an exploratory-synthesis record: a composition's behaviour is "
                "model-generated output, not an empirically evaluated prediction",
                next(e["dependency"] for e in selected
                     if e["relation"] == "exploratory_synthesis"))

    designs = {e["fit_evaluation"] for e in selected}
    # Code verification and non-empirical checks establish that the code does what it says. They
    # cannot license a reconstruction claim about reality on their own.
    if designs and designs <= {"code_verification", "not_empirical"}:
        return ("EXPLORATORY_SIMULATION",
                f"every selected record is non-empirical ({sorted(designs)}): code verification "
                f"establishes that the implementation matches its specification, not that the "
                f"output reconstructs a measurement", selected[0]["dependency"])

    if designs <= set(_HELD_OUT_DESIGNS) and designs:
        return ("PREDICTED",
                "every selected record is under a held-out or independent evaluation design "
                f"({sorted(designs)})", None)
    weakest = sorted(d for d in designs if d not in _HELD_OUT_DESIGNS)
    if not weakest:
        raise ValueError(
            f"{claim.claim_id}: badge derivation is ambiguous over designs {sorted(designs)} -- "
            f"resolve deliberately rather than defaulting")
    return ("RECONSTRUCTED",
            f"the weakest selected evaluation design is {weakest[0]!r}, which does not qualify as "
            f"held out or independent",
            next(e["dependency"] for e in selected if e["fit_evaluation"] == weakest[0]))


@dataclass
class Producer:
    """How a claim's numbers are GENERATED (never hand-typed). `result_map` maps a
    numeric_result key -> a dotted path into the named function's return value, so
    a test/exporter can recompute every public number and detect drift or a
    hard-coded value (a numeric key with no result_map entry is the failure)."""
    module: str
    function: str
    result_map: dict           # numeric_result key -> dotted result path
    kwargs: dict = field(default_factory=dict)
    slow: bool = False         # True => PDE/GPU solves; skip in the quick test

    def compute(self) -> dict:
        fn = getattr(import_module(self.module), self.function)
        res = fn(**self.kwargs)
        return {k: _dig(res, p) for k, p in self.result_map.items()}

    def ref(self) -> str:
        return f"{self.module}.{self.function}"


@dataclass
class PublicClaim:
    """One traceable public claim. Every numeric value regenerates from `producer`;
    every value carries a unit; the claim carries an evidence-strength label and a
    badge, its source datasets, validity range, caveat, and reproduction command."""
    claim_id: str
    public_question: str
    headline: str
    plain_language_finding: str
    numeric_result: dict            # key -> value (SNAPSHOT; regenerated by producer)
    units: dict                     # key -> unit string (every numeric key needs one)
    uncertainty_or_sensitivity: str
    evidence_strength: str          # one of the PUBLIC EVIDENCE_STRENGTHS above -- a coarser
                                    # lay term MAPPED from the registry relation via
                                    # REGISTRY_TO_PUBLIC, not the registry value verbatim
    badge: str                      # one of BADGES
    components: list                # DEPRECATED free-text list; use `dependencies`
    dataset_manifest_ids: list      # rows that MUST exist in data/MANIFEST.csv
    validity_range: str
    primary_caveat: str
    practical_implication: str
    reproduction: str               # one-line command
    producer: Producer
    compares_grinder_dials: bool = False   # if True, caveat MUST warn non-portability
    # --- commit provenance (Paper 3 review P0-6) -------------------------------------------
    # `source_commit` was AMBIGUOUS: it is stamped at export time, so it meant "the commit at
    # which this artifact was last regenerated" -- which a reader could equally read as "the
    # commit the result was produced from" or "the current release commit". Those are different
    # facts, and a snapshot can verify successfully at a later commit while still displaying an
    # earlier value. The two are now recorded SEPARATELY. `source_commit` is retained as a
    # deprecated alias of `generated_from_commit` because published artifacts already carry it.
    source_commit: str | None = None            # DEPRECATED alias of generated_from_commit
    generated_from_commit: str | None = None    # immutable: the commit the payload was produced at
    last_verified_against_commit: str | None = None   # mutable: most recent successful verification
    # --- identified dependencies + their scoped evidence (step 0 + P0-4 option b) -----------
    dependencies: tuple = ()        # Dependency records; `components` is derived from these
    #: Third review P0-1. Which of the dependencies' evidence records actually license THIS claim.
    #: A claim does not ingest a whole component evidence vector; it selects. Empty means the claim
    #: has not yet been scoped, which `validate()` reports rather than tolerating silently.
    evidence_selections: tuple = ()
    outcome: str = "supported"      # supported | negative | indeterminate -- an OUTCOME axis,
                                    # separate from the relation, so "negative validation" no
                                    # longer has to masquerade as an evidence relation

    def component_refs(self):
        """Registry component ids this claim depends on, derived from `dependencies`."""
        return tuple(d.ref for d in self.dependencies if d.kind == "component")

    def _flatten(self, deps):
        return tuple(
            dict(dependency=d.ref, kind=d.kind, relation=e.relation,
                 public_relation=e.public_relation, scope=e.scope, gate=e.gate,
                 outcome=e.outcome, evidence_id=e.evidence_id,
                 fit_evaluation=e.fit_evaluation, reality_facing=e.reality_facing)
            for d in deps for e in d.evidence)

    def evidence_inventory(self):
        """EVERY evidence record attached to every dependency.

        This is an inventory for navigation and drill-down. It is NOT the claim's support: a
        component's records may belong to observables this claim says nothing about."""
        return self._flatten(self.dependencies)

    def selected_evidence(self):
        """Only the records this claim SELECTS as licensing its assertion (third review P0-1).

        Unselected component evidence stays visible in `evidence_inventory()` but cannot
        strengthen the claim or alter its badge."""
        chosen = {(s.dependency_ref, eid)
                  for s in self.evidence_selections for eid in s.evidence_ids}
        return tuple(e for e in self.evidence_inventory()
                     if (e["dependency"], e["evidence_id"]) in chosen)

    def evidence_profile(self):
        """The claim's evidence profile.

        Once selections exist this returns ONLY the selected records. Before P0-1 it returned every
        record of every dependency, so a component with code verification on one output and source
        reproduction on another contributed both labels to any claim naming it. One level deep --
        the dependencies' own dependencies are not walked -- so it is a profile, not a transitive
        closure, and the manuscript says so."""
        return self.selected_evidence() if self.evidence_selections else self.evidence_inventory()

    def derived_badge(self):
        """``(badge, rationale, limiting_dependency)`` computed from the selected evidence."""
        return derive_badge(self)

    # ---- structural guardrails (PUBLIC_VALUE.md §3; enforced, not by convention) --
    def validate(self) -> list:
        """Return a list of guardrail violations (empty == clean)."""
        errs = []
        # (1) every numeric public claim value has a unit
        for k in self.numeric_result:
            if k not in self.units or not str(self.units[k]).strip():
                errs.append(f"{self.claim_id}: numeric '{k}' has no unit")
        # (1b) dependencies must be IDENTIFIED, not described. This is the guardrail that makes
        # per-dependency evidence possible at all: before it, 11 of 13 dependency edges were free
        # text and could not be joined to anything.
        for d in self.dependencies:
            errs += [f"{self.claim_id}: {e}" for e in d.validate()]
        if self.outcome not in PUBLIC_OUTCOMES:
            errs.append(f"{self.claim_id}: outcome '{self.outcome}' not in {PUBLIC_OUTCOMES}")
        # (1c) a compound label that fuses relation and outcome is exactly what S5 forbids
        if self.evidence_strength in LEGACY_COMPOUND_RELATIONS:
            errs.append(f"{self.claim_id}: '{self.evidence_strength}' is a compound of a relation "
                        f"and an outcome; set evidence_strength and outcome separately")
        # (2) evidence-strength tag present and in the vocabulary (never invented)
        if self.evidence_strength not in EVIDENCE_STRENGTHS:
            errs.append(f"{self.claim_id}: evidence_strength "
                        f"'{self.evidence_strength}' not in the ROADMAP §0 vocabulary")
        # (3) a badge is set and valid; a simulation claim needs the SIM badge
        if self.badge not in BADGES:
            errs.append(f"{self.claim_id}: badge '{self.badge}' invalid")

        # (3b) THIRD REVIEW P0-1 -- claim-scoped evidence selection is enforced, not advisory.
        by_ref = {d.ref: d for d in self.dependencies}
        model_deps = {d.ref for d in self.dependencies if d.kind == "component"}
        selected_refs = set()
        for s in self.evidence_selections:
            errs += [f"{self.claim_id}: {e}" for e in s.validate()]
            dep = by_ref.get(s.dependency_ref)
            if dep is None:
                errs.append(f"{self.claim_id}: evidence selection names dependency "
                            f"{s.dependency_ref!r}, which this claim does not declare")
                continue
            selected_refs.add(s.dependency_ref)
            available = {e.evidence_id for e in dep.evidence}
            for eid in s.evidence_ids:
                if eid not in available:
                    errs.append(f"{self.claim_id}: selected evidence {eid!r} does not belong to "
                                f"dependency {s.dependency_ref!r}")
        # every load-bearing component must be covered by a selection, or the claim is inheriting
        # its component's whole inventory again
        if self.evidence_selections:
            for ref in sorted(model_deps - selected_refs):
                errs.append(f"{self.claim_id}: component dependency {ref!r} is load-bearing but "
                            f"no evidence is selected for it")

        # (3c) THIRD REVIEW P0-2 -- the badge must be DERIVED, not authored.
        try:
            derived, why, limiting = derive_badge(self)
        except ValueError as exc:
            errs.append(f"{self.claim_id}: badge derivation failed closed -- {exc}")
        else:
            if self.badge != derived:
                errs.append(
                    f"{self.claim_id}: badge {self.badge!r} was authored but the selected evidence "
                    f"derives {derived!r} ({why}"
                    + (f"; limiting dependency {limiting!r}" if limiting else "") + ")")
        # (5) a public number is hard-coded (no producer path) — the integrity rule
        for k in self.numeric_result:
            if k not in self.producer.result_map:
                errs.append(f"{self.claim_id}: numeric '{k}' is hard-coded "
                            f"(no producer.result_map entry generating it)")
        # (6) a grinder-dial comparison without a non-portability warning
        if self.compares_grinder_dials:
            c = self.primary_caveat.lower()
            if not any(w in c for w in ("non-portable", "not portable", "adapter",
                                        "not a unit", "calibrat")):
                errs.append(f"{self.claim_id}: compares grinder dials but the caveat "
                            f"carries no non-portability / adapter warning")
        return errs

    def to_dict(self) -> dict:
        d = asdict(self)
        d["producer"] = {"ref": self.producer.ref(), "slow": self.producer.slow,
                         "kwargs": self.producer.kwargs}
        # the scoped evidence profile is exported flat as well as nested, so a consumer can read
        # "what evidence stands behind this output" without walking the dependency tree
        d["evidence_profile"] = list(self.evidence_profile())
        d["component_refs"] = list(self.component_refs())
        return d
