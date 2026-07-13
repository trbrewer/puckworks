"""VizSpec — the honesty-bound description of one visual (ROADMAP §8).

A visual is EVIDENCE-BOUND: it binds to a `public.schema.Producer` (the same
"numbers recompute from a named function, never hand-typed" rule the public/
layer enforces), carries ONE of the four public badges + a ROADMAP §0
evidence-strength label rendered INTO the graphic, and declares a FIDELITY
CEILING it may not exceed. A VizSpec with no producer, an unknown badge/evidence
word, or an empty fidelity ceiling fails `.validate()` — a visual with no honest
source cannot ship.

This module adds NO registry component and NO physics gate: it is presentation
tooling that CONSUMES registered components / harness / data (CLAUDE.md rule 1).
It reuses `public.schema` vocabulary verbatim; it does not mint new badges or
strength words.
"""
from __future__ import annotations
from dataclasses import dataclass, field

# Reuse the public layer's vocabulary UNCHANGED — do not invent new badges/words.
from ..public.schema import BADGES, EVIDENCE_STRENGTHS, Producer

# --- FIDELITY CEILINGS (per source component / data source) ---------------
# The one honest sentence each source's visuals may not exceed. Keyed by the
# component/data key a VizSpec lists in `.components`; the test asserts every
# referenced source has an entry here (no unlabelled source). Copied from the
# task's fidelity contract + the cards' own validity ranges.
FIDELITY_CEILINGS = {
    "registry": (
        "A labelled process map of registered components; each stage carries its "
        "own component's badge — the diagram asserts nothing beyond the registry."),
    "brewer2026.lb_reference": (
        "Computed Stokes-regime flow on VERIFICATION geometry (model-vs-model "
        "twin). Render as 'computed Stokes flow, verification geometry', NEVER "
        "'the flow in your puck'."),
    "brewer2026.lb_taichi": (
        "Stokes-regime verification twin (GPU). Same ceiling as lb_reference: a "
        "verification field, not a measured puck flow."),
    "brewer2026.pack_generator": (
        "Boolean-sphere synthetic geometry; fines are sub-voxel columnar "
        "heterogeneity. Render grains honestly and label fines a HETEROGENEITY "
        "FIELD, not resolved particles."),
    "brewer2026.streamtube": (
        "Static lognormal channeling; the sigma(phi1) closure is EMPIRICAL / "
        "calibrated on 3 points. Time-averaged response only."),
    "brewer2026.coupled_kappa_t": (
        "kind=synthesis: 'framework; branch fidelity inherited'. NEVER a "
        "'validated kappa(t) law' (3 of 4 donor branches carry unidentified "
        "params); flow closure is poroelastic, not Kozeny-Carman."),
    "ntube_union": (
        "Dynamic per-tube concentration is EXPLORATORY — ONE configuration "
        "(gs 1.1, 9 bar, N=200), NOT a proven instability. Caption 'one "
        "configuration, not a general result' (ANALYSIS_P2 §2.4 / G-lat)."),
    "fasano2000_partI.fines_migration": (
        "fasano-STRUCTURED with ZERO identified params: mechanism illustration "
        "only. Caption 'closures are ours, not the paper's; not a coffee fit.' "
        "NEVER render fines transport as measured."),
    "foster2025.infiltration": (
        "Infiltration front validated on CT (independent), fine grind; coarse "
        "front non-uniform. A front computed from recorded pressure is a "
        "reconstruction of that validated model."),
    "foster2025.machine_mode": (
        "Pump+headspace machine mode; reported t_p/t_s include a FITTED t_shift "
        "(post-fit) — label it. Pump curve is nominal."),
    "mo2023_2.swelling": (
        "Fixed-dP swelling decay is UNVALIDATED in the source -> qualitative "
        "mechanism only."),
    "mo2023_2.coupled_bed": (
        "Depth-resolved swelling bed; M_c>~30 g over-prediction is genuine, not "
        "a bug. Qualitative for the swelling claim."),
    "visualizer.coffee": (
        "Reference-strength, selection-biased POPULATION; HYDRAULICS only. User "
        "TDS/EY/sensory are NOT groundtruth and are never shown as such. "
        "Population/ensemble visuals only, badged reference."),
    "waszkiewicz2025.poroelastic": (
        "Closed-form poroelastic kappa(P,Phi(t)); public rig dataset; "
        "quantitative only at high P; constants per rig/coffee/grind."),
    "waszkiewicz2025": (
        "One public rig's measured traces (pressure-controlled). Measured but "
        "single rig/coffee — an OBSERVED trace, not a universal curve."),
    "identifiability": (
        "Inventory<->kinetics SSE valley is a LOCAL-curvature identifiability "
        "diagnostic (flat valley); not a claim that transfer fails at matched "
        "mass. post-fit reconstruction strength."),
    "wadsworth2026.permeability": (
        "Validated untamped k(<R>,phi_p) (phi_p 0.37-0.67); TAMPED is an "
        "extrapolation. Use for porosity colouring only within the untamped range."),
    "de1_fixtureA": (
        "One held DE1 shot (P(t)/W(t)/flow). Pressure-NODE identity OPEN (§5.9); "
        "an independent parameter-free triangle, not a universal curve."),
}


@dataclass
class VizSpec:
    """One evidence-bound visual. `render_fn` is a dotted 'module:function' ref
    resolved lazily at render time (so the registry imports before the drawing
    modules and without matplotlib). `producer` binds the numbers to a named
    function exactly as `public.schema.PublicClaim` does."""
    id: str
    title: str
    class_: int                     # 1 = functional 2D · 2 = high-fidelity render
    producer: Producer              # numbers recompute from here (never hand-typed)
    badge: str                      # one of BADGES, drawn INTO the graphic
    evidence_strength: str          # one of EVIDENCE_STRENGTHS (UNCHANGED from source)
    fidelity_ceiling: str           # the honest sentence this visual may not exceed
    render_fn: str                  # 'module:function' dotted ref
    components: list                # source component / data keys (must be in FIDELITY_CEILINGS)
    caption: str
    outputs: list = field(default_factory=list)   # expected output tokens
    used_in: str = ""               # where the visual is used (papers / PV)
    evidence_scope: str = ""        # closed-vocab scope qualifier, e.g. "within-rig"
    composite: bool = False         # per-lens labelling (Note 1): spec badge = STRICTEST lens
    class_label: str = ""           # display override for the class cell (e.g. "1+2")
    slow: bool = False              # LB / 3D / video -> not run in CI
    source_commit: str | None = None

    def validate(self) -> list:
        """Return a list of honesty-contract violations (empty == clean)."""
        errs = []
        if self.class_ not in (1, 2):
            errs.append(f"{self.id}: class_ must be 1 or 2")
        # (1) a producer binding must be present and point at a named function
        if not isinstance(self.producer, Producer) or not self.producer.module \
                or not self.producer.function:
            errs.append(f"{self.id}: no Producer binding (numbers must recompute "
                        f"from a named function, never hand-typed)")
        # (2) a valid badge + evidence word, reused from the public vocabulary
        if self.badge not in BADGES:
            errs.append(f"{self.id}: badge '{self.badge}' not in public BADGES")
        if self.evidence_strength not in EVIDENCE_STRENGTHS:
            errs.append(f"{self.id}: evidence_strength '{self.evidence_strength}' "
                        f"not in the ROADMAP §0 vocabulary")
        # (3) a NON-EMPTY fidelity ceiling (the anti-overclaim clause)
        if not str(self.fidelity_ceiling).strip():
            errs.append(f"{self.id}: empty fidelity_ceiling")
        if not str(self.render_fn).strip() or ":" not in self.render_fn:
            errs.append(f"{self.id}: render_fn must be a 'module:function' ref")
        # (4) every source component must be labelled in FIDELITY_CEILINGS
        for c in self.components:
            if c not in FIDELITY_CEILINGS:
                errs.append(f"{self.id}: source '{c}' has no FIDELITY_CEILINGS entry "
                            f"(unlabelled source)")
        return errs

    def badge_line(self) -> str:
        """The one-line honesty stamp drawn into every output."""
        return f"[{self.badge}] · {self.evidence_strength}"

    def class_display(self) -> str:
        return self.class_label or str(self.class_)

    def evidence_display(self) -> str:
        """Evidence cell for the gallery: closed-vocab word + optional scope
        qualifier (the vocab word rides along UNCHANGED; scope is only a rendered
        annotation, never a new strength word)."""
        return (f"{self.evidence_strength} ({self.evidence_scope})"
                if self.evidence_scope else self.evidence_strength)

    def badge_display(self) -> str:
        """Badge cell for the gallery. Composites (Note 1) carry the STRICTEST lens
        badge at spec level, with per-lens badges rendered inline in the graphic."""
        return f"{self.badge} (composite)" if self.composite else self.badge

    def to_dict(self) -> dict:
        return {
            "id": self.id, "title": self.title, "class": self.class_,
            "class_display": self.class_display(),
            "badge": self.badge, "badge_display": self.badge_display(),
            "evidence_strength": self.evidence_strength,
            "evidence_display": self.evidence_display(),
            "fidelity_ceiling": self.fidelity_ceiling,
            "producer": self.producer.ref(), "slow": self.slow,
            "composite": self.composite,
            "components": list(self.components), "outputs": list(self.outputs),
            "used_in": self.used_in,
            "caption": self.caption, "source_commit": self.source_commit,
        }
