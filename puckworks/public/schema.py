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
    outcome: str = "supported"      # supported | negative | indeterminate -- an OUTCOME axis,
                                    # separate from the relation, so "negative validation" no
                                    # longer has to masquerade as an evidence relation

    def component_refs(self):
        """Registry component ids this claim depends on, derived from `dependencies`."""
        return tuple(d.ref for d in self.dependencies if d.kind == "component")

    def evidence_profile(self):
        """The claim's SCOPED EVIDENCE PROFILE: every (dependency, relation, scope, outcome) record
        behind it (Paper 3 review P0-4 option b).

        This is what replaces "one label for the whole output". It is one level deep -- the
        dependencies' own dependencies are not walked -- so it is a profile, not a transitive
        closure, and the manuscript says so."""
        return tuple(
            dict(dependency=d.ref, kind=d.kind, relation=e.relation,
                 public_relation=e.public_relation, scope=e.scope, gate=e.gate,
                 outcome=e.outcome)
            for d in self.dependencies for e in d.evidence)

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
