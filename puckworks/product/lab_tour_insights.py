"""Educational insight figures for the Full Laboratory Tour deep dive (#43, ROADMAP §8).

`component_figures(result, ...)` returns ZERO, ONE, or SEVERAL `TourFigure`s per component — each an
educational *relationship* figure that teaches one idea, drawn from an authoritative producer and governed
by a registered `VizSpec` (badge + evidence strength + fidelity ceiling stamped into the figure). It is
NOT the tour execution layer: it never changes routes, hashes, or rights, and it obeys the component's
tour rights decision — a component that did not execute receives ZERO educational producer calls and an
honest, finite reason instead.

Scientific-check (gate) numbers are deliberately NOT plotted here — a gate pass supports trust in a
component without being an interesting public figure (its status stays in the technical/checks area).
"""
from __future__ import annotations

import dataclasses

# finite reason vocabulary for a component with no educational figure
NO_FIGURE_REASONS = ("NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET", "RIGHTS_BLOCKED",
                     "OPTIONAL_DEPENDENCY_UNAVAILABLE", "REFERENCE_ONLY", "TOO_EXPENSIVE_FOR_DEFAULT_TOUR")


@dataclasses.dataclass
class TourFigure:
    component_id: str
    viz_spec_id: str
    headline: str            # public hook (plain language, not the component id)
    question: str            # the ordinary-language question the figure answers
    caption: str             # backwards-compatible flat Markdown (composed from `narrative`)
    figure: object           # matplotlib Figure
    varied_input: str
    fixed_inputs: dict
    evidence_badge: str
    evidence_strength: str
    fidelity_ceiling: str
    producer_ref: str
    narrative: object = None  # tour_style.TourFigureNarrative — structured novice explanation


# component_id -> ordered list of insights: (viz_spec_id, headline, question, draw_fn_name, kwargs_fn)
# kwargs_fn(scenario) -> producer kwargs (scenario is the tour's {preset, overrides, ...} or None).
def _cam_kwargs(scenario):
    ov = (scenario or {}).get("overrides", {}) if scenario else {}
    out = {}
    for k in ("dose_g", "target_beverage_g", "pressure_bar", "brew_temperature_c"):
        if k in ov:
            out[k] = float(ov[k])
    if scenario and scenario.get("preset_id"):
        out["preset"] = scenario["preset_id"]
    return out


def _none(_scenario):
    return {}


_INSIGHTS: dict = {
    "cameron2020.extraction_bdf": [
        ("cameron_shot_timeseries", "The whole simulated shot, moment to moment",
         "What does the whole simulated shot look like over time?",
         "figure_cameron_shot_timeseries", _cam_kwargs),
        ("cameron_pressure_sweep", "Does more pressure make a stronger espresso?",
         "Does more pressure make a stronger, more-extracted shot?",
         "figure_cameron_pressure_sweep", _cam_kwargs),
        ("cameron_beverage_sweep", "More coffee, or a weaker drink?",
         "Why can collecting more liquid raise extraction yet weaken the drink?",
         "figure_cameron_beverage_sweep", _cam_kwargs),
    ],
    "foster2025.infiltration": [
        ("wetting_front_sweep", "How fast water soaks the dry puck",
         "How quickly does water reach the bottom of a dry puck?",
         "figure_wetting_front", _none)],
    "brewer2026.lb_reference": [
        ("puck_flow_field", "Why flow is fastest in the middle",
         "Why is flow fastest in the middle and zero at the walls?",
         "figure_stokes_profile", _none)],
    "brewer2026.pack_generator": [
        ("grain_pack_3d", "What the model's puck looks like",
         "What does the model's synthetic puck actually look like?",
         "figure_pack_slice", _none)],
    "fasano2000_partI.fines_migration": [
        ("fines_migration_mechanism", "Can more pressure give LESS flow?",
         "Can more pressure eventually give less flow when fines compact?",
         "figure_fines_qinf", _none)],
    "brewer2026.streamtube": [
        ("channeling_concentration", "Can uneven paths concentrate the flow?",
         "When paths differ, does flow spread out or concentrate?",
         "figure_channeling", _none)],
}


def _reason_for(result: dict) -> str:
    st = result.get("execution_status")
    if st == "RIGHTS_BLOCKED":
        return "RIGHTS_BLOCKED"
    if st in ("RIGHTS_NOT_CLEARED",):
        return "RIGHTS_BLOCKED"
    if st == "OPTIONAL_UNAVAILABLE":
        return "OPTIONAL_DEPENDENCY_UNAVAILABLE"
    if result.get("execution_kind") == "NATIVE_REFERENCE":
        return "REFERENCE_ONLY"
    return "NO_DEFENSIBLE_PUBLIC_RELATIONSHIP_YET"


def no_figure_reason(result: dict) -> str:
    """A finite, honest reason a component has no educational figure (never a raw error dump)."""
    return _reason_for(result)


def component_figures(result: dict, *, scenario: dict | None = None, trace_panels=None,
                      execution_context: str = "LOCAL_PRIVATE") -> list:
    """ZERO or more TourFigures for a component's tour result. Obeys the tour rights decision: a
    component that did not EXECUTE gets zero educational producer calls and an empty list (use
    no_figure_reason for the honest reason)."""
    from puckworks.viz import registry as R, tour_insight_draw as draw
    cid = result["component_id"]
    if result.get("execution_status") != "EXECUTED":       # rights/blocked/optional/check-fail -> no calls
        return []
    out = []
    for spec_id, headline, question, draw_name, kwargs_fn in _INSIGHTS.get(cid, []):
        spec = R.viz_by_id(spec_id)
        data = getattr(R, "producer_data")(spec) if kwargs_fn is _none else \
            _run_producer(spec, kwargs_fn(scenario))
        # notebook presentation: the notebook prints the headline + question, so the figure never repeats
        # them. Pass the ceiling so the reserved footer band is sized to the wrapped scope text.
        fig, narrative = getattr(draw, draw_name)(
            data, presentation="notebook", ceiling=spec.fidelity_ceiling, title=spec.title)
        R.stamp_fig(fig, spec)                             # badge + evidence + fidelity stamped into the fig
        out.append(TourFigure(
            component_id=cid, viz_spec_id=spec.id, headline=headline, question=question,
            caption=narrative.to_caption(), figure=fig,
            varied_input=data.get("varied", "reference case"),
            fixed_inputs=dict(data.get("fixed", {})), evidence_badge=spec.badge,
            evidence_strength=spec.evidence_strength, fidelity_ceiling=spec.fidelity_ceiling,
            producer_ref=spec.producer.ref(), narrative=narrative))
    return out


def _run_producer(spec, kwargs: dict):
    import importlib
    p = spec.producer
    fn = getattr(importlib.import_module(p.module), p.function)
    return fn(**{**p.kwargs, **kwargs})
