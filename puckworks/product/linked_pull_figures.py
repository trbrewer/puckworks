"""Figures for the Espresso Model Relay — RESULT-BOUND and purely presentational (§8).

`relay_figures(result)` draws ONLY from `result["figure_payloads"]`, which the engine populated from
already-computed authoritative data. The drawing path calls NO models and NO producers, mutates no global
state, and contains no scientific fallback constants — every figure's numbers come from the completed,
provenance-hashed result. Each figure reuses an existing evidence-bound `VizSpec` + tour draw primitive
(so it carries the same badge / evidence strength / fidelity ceiling and in-figure stamp) and records its
owning component id(s). matplotlib is a viz extra, imported lazily.
"""
from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True)
class RelayFigure:
    figure_id: str
    station_id: str
    owner_component_ids: tuple
    viz_spec_id: str
    figure: object            # matplotlib Figure
    caption: str
    evidence_badge: str
    fidelity_ceiling: str
    source_stage_hashes: tuple


# figure_id -> the pure tour_insight_draw primitive that renders its payload data
_DRAW = {
    "cameron_shot": "figure_cameron_shot_timeseries",
    "synthetic_pack": "figure_pack_slice",
    "wetting_front": "figure_wetting_front",
}


def relay_figures(result: dict, *, presentation: str = "notebook") -> tuple:
    """Draw every figure from the completed result's payloads. Zero model/producer calls."""
    from ..viz import registry as R, tour_insight_draw as D
    out = []
    for payload in result.get("figure_payloads", []):
        draw_name = _DRAW.get(payload["figure_id"])
        if not draw_name:
            continue
        spec = R.viz_by_id(payload["viz_spec_id"])
        fig, narrative = getattr(D, draw_name)(payload["data"], presentation=presentation,
                                               ceiling=spec.fidelity_ceiling, title=spec.title)
        R.stamp_fig(fig, spec)
        out.append(RelayFigure(
            figure_id=payload["figure_id"], station_id=payload["station_id"],
            owner_component_ids=tuple(payload["owner_component_ids"]), viz_spec_id=payload["viz_spec_id"],
            figure=fig, caption=narrative.to_caption(), evidence_badge=spec.badge,
            fidelity_ceiling=spec.fidelity_ceiling,
            source_stage_hashes=tuple(payload.get("source_stage_hashes", ()))))
    return tuple(out)


def figures_by_owner(result: dict, presentation: str = "notebook") -> dict:
    """{component_id: [RelayFigure, ...]} — for rendering a figure beneath its actual owning component."""
    out: dict = {}
    for f in relay_figures(result, presentation=presentation):
        for cid in f.owner_component_ids:
            out.setdefault(cid, []).append(f)
    return out
