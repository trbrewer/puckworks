"""Context-independent presentation + request logic shared by the Guided Pull Laboratory UIs.

Pure Python — imports NO streamlit and NO scientific stack — so it is unit-testable and reused by both
the local/private dev app (`apps/lab_app.py`, LOCAL_PRIVATE) and the public hosted Explorer
(`apps/lab_public_app.py`, PUBLIC_ARTIFACT). It re-implements no science and hard-codes no execution
context: each app declares its own context and passes it to `puckworks.product.lab_service`.
"""
from __future__ import annotations

# bounded input ranges (widget constraints, NOT model clamps) — shared by both apps
BOUNDS = {"dose_g": (5.0, 30.0), "target_beverage_g": (10.0, 80.0),
          "pressure_bar": (1.0, 12.0), "brew_temperature_c": (80.0, 98.0)}

# the immutable public notebook fallback (a link the user clicks — NOT a network call from the app)
COLAB_LAB_URL = ("https://colab.research.google.com/github/trbrewer/puckworks/blob/main/"
                 "notebooks/guided_pull_laboratory_colab.ipynb")

# plain-language relabelling of the internal vocabulary (novice layer)
PLAIN_LABELS = {
    "domain_policy": "What should happen outside the evidence range?",
    "warn": "Show the result with a warning",
    "strict": "Do not run outside the evidence range",
    "native reference runner": "Component self-check",
    "common-scenario lens": "Model that can use this recipe",
    "disposition": "Availability",
}
# the two evidence-range choices a novice sees, mapped to the internal domain policy
EVIDENCE_RANGE_CHOICES = {PLAIN_LABELS["warn"]: "warn", PLAIN_LABELS["strict"]: "strict"}


def preset_defaults(preset_id: str) -> dict:
    import dataclasses
    import puckworks.product as prod
    recipe, _ = prod.load_pull_preset(preset_id)
    d = dataclasses.asdict(recipe)
    return {k: float(d[k]) for k in BOUNDS}


def build_request(preset_id, overrides, state):
    """Build a ScenarioRequest from a plain state dict (pure; no streamlit). Selected ids are honoured
    only under the 'selected' policy — the request validates the combination."""
    from puckworks.product import lab
    kw = dict(preset_id=preset_id, overrides=overrides,
              domain_policy=state.get("domain_policy", "warn"),
              lens_selection_policy=state.get("lens_policy", "primary"),
              reference_selection_policy=state.get("ref_policy", "interactive_fast"))
    if kw["lens_selection_policy"] == "selected":
        kw["requested_lens_ids"] = tuple(state.get("selected_lens_ids") or ())
    if kw["reference_selection_policy"] == "selected":
        kw["requested_reference_runner_ids"] = tuple(state.get("selected_ref_ids") or ())
    return lab.ScenarioRequest(**kw)


def format_finding(finding) -> tuple:
    """(level, text, detail) for a DomainFinding (object OR serialized dict). No streamlit dependency."""
    if isinstance(finding, dict):
        status_v = str(finding.get("status") or "").lower()
        field = finding.get("field", "")
        plain = finding.get("plain_explanation", "") or ""
        detail = finding.get("technical_reason", "") or ""
        text = f"{field}: {plain}".strip(": ")
        level = {"rejected": "error", "warning": "warning", "in_domain": "success"}.get(status_v, "info")
        return level, text or field or status_v, detail
    status = getattr(finding, "status", None)
    status_v = str(getattr(status, "value", status) or "").lower()
    field = getattr(finding, "field", "")
    plain = getattr(finding, "plain_explanation", "") or ""
    detail = getattr(finding, "technical_reason", "") or ""
    text = f"{field}: {plain}".strip(": ")
    if status_v in ("rejected", "out_of_domain", "reject"):
        level = "error"
    elif status_v in ("warning", "warn", "extrapolation"):
        level = "warning"
    elif status_v in ("in_domain", "ok", "supported"):
        level = "success"
    else:
        level = "info"
    return level, text or field or status_v, detail


# ── public-live derivation (affirmative rights only; never hard-coded, never NOT_REVIEWED) ──
def public_live_ids() -> list:
    """Components a PUBLIC surface may offer as live-runnable today — from use-specific rights only."""
    from puckworks.product import lab_explorer
    return lab_explorer.public_live_component_ids()


def default_reference_shot_public_ready() -> bool:
    """Is the default common-scenario lens (the recipe-driven 'reference shot') affirmatively cleared for
    public execution AND output publication? Today Cameron is NOT_REVIEWED, so this is False — the public
    Run button is disabled and the Colab path is offered instead."""
    from puckworks import rights
    from puckworks.product import lab
    cid = lab.PRIMARY_LENS_ID
    return (rights.may_execute_in_public_batch(cid).allowed and rights.may_publish_outputs(cid).allowed)


def build_public_selfcheck_request(selected_ids):
    """A PUBLIC selected-references-only request. Guards the selection to affirmatively public-live
    components — an uncleared id is refused here (the rights preflight is still the authority downstream)."""
    from puckworks.product import lab
    live = set(public_live_ids())
    bad = [c for c in selected_ids if c not in live]
    if bad:
        raise ValueError(f"not publicly cleared: {sorted(bad)}")
    if not selected_ids:
        raise ValueError("select at least one publicly-cleared component self-check")
    return lab.ScenarioRequest("pv19_named", lens_selection_policy="none",
                               reference_selection_policy="selected",
                               requested_reference_runner_ids=tuple(selected_ids))


# ── novice result ordering (what modeled -> key results -> evidence -> caveats -> plots -> details) ──
def novice_result_sections(report: dict) -> list:
    """Ordered (heading, kind, payload) sections for the novice result layer. 'kind' lets the renderer
    pick a widget without re-deciding the order. No science is recomputed."""
    sections = []
    sc = report["scenario"]
    sections.append(("What was modeled", "text",
                     f"{sc['scenario_id']} — overrides: {sc['applied_overrides'] or 'none (preset)'}"))
    lenses = report.get("executed_lenses", [])
    key = []
    for lens in lenses:
        for o in lens["observables"][:4]:
            key.append({"observable": o["name"], "value": o["value"], "unit": o["unit"],
                        "role": o["role"]})
    sections.append(("Key results", "table", key))
    dom = report["domain"]
    if dom["blocked"]:
        ev = ("Outside the evidence range — the model was not run.", "error")
    elif dom["warning_count"]:
        ev = ("A warning was raised: the recipe is at the edge of the model's evidence range.", "warning")
    else:
        ev = ("Inside the model's stated evidence range.", "success")
    sections.append(("Evidence-range status", "status", ev))
    sections.append(("What this does not mean", "list",
                     list(report["what_this_does_not_prove"]) + [report["fidelity_ceiling"]]))
    return sections


def panel_table(panel: dict) -> dict:
    """The text-alternative data table for a chart panel (accessibility): column headers carry unit+role,
    rows are the x + per-series y values. No science recomputed."""
    headers = [panel["x_label"]] + [f"{s['label']} [{s['role']}, {panel['unit']}]" for s in panel["series"]]
    rows = list(zip(panel["x"], *[s["y"] for s in panel["series"]]))
    return {"headers": headers, "rows": rows}
