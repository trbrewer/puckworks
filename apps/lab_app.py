"""Guided Pull Laboratory — a small Streamlit development UI (PV-19B / #43 / #70).

Development-only (`0.4.0.dev0`). Calls ONLY the supported `puckworks.product` API and the Guided Pull
Laboratory comparison API — it re-implements no scientific equation, hard-codes no science number,
makes no external network request, and stores no user data. Run it in Codespaces or locally::

    pip install -e ".[dev,viz,webapp]"
    streamlit run apps/lab_app.py

`puckworks` core never imports this module.
"""
from __future__ import annotations

import streamlit as st

import puckworks.product as prod
from puckworks.product import lab

# bounded input ranges (widget constraints, not model clamps)
BOUNDS = {"dose_g": (5.0, 30.0), "target_beverage_g": (10.0, 80.0),
          "pressure_bar": (1.0, 12.0), "brew_temperature_c": (80.0, 98.0)}


def preset_defaults(preset_id: str) -> dict:
    import dataclasses
    recipe, _ = prod.load_pull_preset(preset_id)
    d = dataclasses.asdict(recipe)
    return {k: float(d[k]) for k in BOUNDS}


def format_finding(finding) -> tuple:
    """(level, text, detail) for a DomainFinding (object OR the serialized dict the execution carries).
    Unit-testable; no Streamlit dependency."""
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


def _apply_preset():
    for k, v in preset_defaults(st.session_state.get("preset_id", "pv19_named")).items():
        st.session_state[k] = v


def build_request(preset_id, overrides, state) -> "lab.ScenarioRequest":
    """Build a ScenarioRequest from the UI state (pure; unit-testable; no Streamlit dependency). Selected
    ids are honoured only under the 'selected' policy — the request validates the combination."""
    kw = dict(preset_id=preset_id, overrides=overrides,
              domain_policy=state.get("domain_policy", "warn"),
              lens_selection_policy=state.get("lens_policy", "primary"),
              reference_selection_policy=state.get("ref_policy", "interactive_fast"))
    if kw["lens_selection_policy"] == "selected":
        kw["requested_lens_ids"] = tuple(state.get("selected_lens_ids") or ())
    if kw["reference_selection_policy"] == "selected":
        kw["requested_reference_runner_ids"] = tuple(state.get("selected_ref_ids") or ())
    return lab.ScenarioRequest(**kw)


def selection_preview(request) -> dict:
    """What WILL run for this request, BEFORE execution: the selected lens ids + their readiness, rights
    eligibility, and runtime class; and the resolved reference ids. A model is never executed merely
    because it is available."""
    from puckworks import rights
    from puckworks.product import lab_runners
    considered = lab.resolve_lens_selection(request)
    lenses = []
    for cid in considered:
        state, ready, reason = lab.lens_readiness(cid)
        lenses.append({"component_id": cid, "adapter_readiness": state, "will_execute": ready,
                       "local_execution_allowed": rights.may_execute_locally(cid).allowed,
                       "public_execution_allowed": rights.may_execute_in_public_batch(cid).allowed,
                       "reason": reason})
    refs = lab._resolve_reference_component_ids(request)
    ref_rows = [{"component_id": c, "has_runner": lab_runners.has_runner(c),
                 "runtime_class": lab_runners.runtime_class(c) if lab_runners.has_runner(c) else None,
                 "rights_blocked": rights.is_code_rights_blocked(c)} for c in refs]
    return {"lens_selection_policy": request.lens_selection_policy, "lenses": lenses,
            "reference_selection_policy": request.reference_selection_policy, "references": ref_rows,
            "note": "availability is not selection; a lens executes only if ready + in-domain"}


def main():
    st.set_page_config(page_title="Guided Pull Laboratory", page_icon="☕", layout="wide")
    st.title("Guided Pull Laboratory")
    st.caption("Development UI (0.4.0.dev0) — independent model lenses over one bounded scenario. "
               "Not a validated digital twin; competing mechanisms are never averaged. "
               "Every number comes from a named producer.")

    presets = list(prod.available_pull_presets())
    if "preset_id" not in st.session_state:
        st.session_state["preset_id"] = presets[0]
        _apply_preset()

    with st.sidebar:
        st.header("Scenario")
        st.selectbox("Preset / scenario", presets, key="preset_id", on_change=_apply_preset,
                     help="A fixed, rights-independent reference recipe. Changing it reloads its values.")
        st.number_input("Dose (g)", *BOUNDS["dose_g"], key="dose_g", step=0.5)
        st.number_input("Target beverage mass (g)", *BOUNDS["target_beverage_g"],
                        key="target_beverage_g", step=1.0)
        st.number_input("Pressure (bar)", *BOUNDS["pressure_bar"], key="pressure_bar", step=0.5)
        st.number_input("Temperature (°C)", *BOUNDS["brew_temperature_c"],
                        key="brew_temperature_c", step=1.0)
        st.text_input("Grinder / particle input", value="reference recipe (no dial→size conversion)",
                      disabled=True, help="A grinder dial is not a universal particle size.")
        st.selectbox("Domain policy", ["warn", "strict"], key="domain_policy",
                     help="strict: an evidence-range departure blocks execution before the producer runs; "
                          "warn: the run completes with the departure flagged.")
        st.header("Model lens selection")
        st.selectbox("Lens selection policy", list(lab.LENS_SELECTION_POLICIES), key="lens_policy",
                     help="primary: Cameron only · all_ready: every ready adapter · selected: choose · "
                          "none: run no common-scenario model.")
        st.multiselect("Selected lenses (only under 'selected')",
                       [c.name for c in __import__("puckworks").components()], key="selected_lens_ids",
                       help="A component with no adapter is surfaced as REQUESTED_BUT_NOT_EXECUTABLE.")
        st.header("Native reference selection")
        st.selectbox("Reference selection policy", list(lab.REFERENCE_SELECTION_POLICIES),
                     key="ref_policy", index=1)
        from puckworks.product import lab_runners as _lr
        st.multiselect("Selected native references (only under 'selected')", _lr.available_runners(),
                       key="selected_ref_ids")
        st.button("Reset to preset", on_click=_apply_preset)
        run_clicked = st.button("Run comparison", type="primary")

    if not run_clicked:
        st.info("Set the bounded scenario in the sidebar and press **Run comparison**. The selected "
                "preset's values populate the controls; expensive models run only when you press Run.")
        return

    preset_id = st.session_state["preset_id"]
    base = preset_defaults(preset_id)
    overrides = {k: float(st.session_state[k]) for k in BOUNDS
                 if abs(float(st.session_state[k]) - base[k]) > 1e-9}
    try:
        request = build_request(preset_id, overrides, st.session_state)
    except Exception as exc:
        st.error(f"Invalid selection: {type(exc).__name__}: {exc}")
        return
    # pre-execution preview: what WILL run (a model does not run merely because it is available)
    st.subheader("Selection preview (before execution)")
    st.json(selection_preview(request))
    try:
        execution = lab.execute_scenario(request)
    except Exception as exc:                              # useful message, never a stack dump
        st.error(f"Could not run the scenario: {type(exc).__name__}: {exc}")
        return

    # domain findings BEFORE results; the execution already evaluated the domain through the authoritative
    # product domain and decided whether the producer ran (REJECTED blocks always; WARNING blocks strict).
    st.subheader("Domain findings")
    findings = list(execution.domain_findings)
    for f in findings:
        level, text, detail = format_finding(f)
        {"error": st.error, "warning": st.warning, "success": st.success, "info": st.info}[level](text)
        if detail:
            with st.expander("technical reason"):
                st.write(detail)
    if not findings:
        st.success("No domain findings.")
    if execution.domain_blocked:
        st.error(f"Scenario blocked by domain policy ({execution.effective_domain_policy}); the scientific "
                 f"producer was not run. Reason: {execution.domain_block_reason}")
        return

    report = lab.build_comparison(execution, provenance=lab.BuildProvenance(
        package_version=__import__("puckworks").__version__))
    cap = report["capability_snapshot"]

    st.subheader(f"Scenario: {report['scenario']['scenario_id']}")
    st.json(report["scenario"]["applied_overrides"] or {"overrides": "none (preset defaults)"})

    if not report["executed_lenses"]:
        st.warning("No common-scenario lens executed for this request.")
    else:
        lens = report["executed_lenses"][0]
        st.subheader("Executed common-scenario lens")
        st.markdown(f"**`{lens['component_id']}`** — {lens['status']} via `{lens['adapter']}`")
        st.table([{"observable": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"],
                   "note": o["note"]} for o in lens["observables"]])

    st.subheader("Scientific trace plots")
    st.caption("Each panel carries exactly one unit on its y-axis — incompatible units "
               "(bar / g/s / g / % / kg/m³) are never overlaid on one axis.")
    panels = lab.render_data(report)
    labels = {f"{p['component_id']} — {p['title'].split(': ', 1)[-1]}": p["panel_id"] for p in panels}
    chosen = st.multiselect("Panels to show (one per unit)", list(labels), default=list(labels))
    chosen_ids = {labels[c] for c in chosen}
    for panel in panels:
        if panel["panel_id"] not in chosen_ids:
            continue
        st.markdown(f"**{panel['title']}**  — y-axis: {panel['unit']} · evidence: "
                    f"{panel['evidence_badge']}")
        chart = {panel["x_label"]: panel["x"]}
        for s in panel["series"]:
            chart[f"{s['label']} [{s['role']}]"] = s["y"]        # all series share the panel's one unit
        try:
            import pandas as pd
            df = pd.DataFrame(chart).set_index(panel["x_label"])
            st.line_chart(df, y_label=panel["y_label"], x_label=panel["x_label"])
            with st.expander("data table (text alternative)"):
                st.dataframe(df, width="stretch")
            st.download_button("Download panel CSV", data=df.to_csv().encode("utf-8"),
                               file_name=f"{panel['panel_id'].replace('::', '__')}.csv",
                               mime="text/csv", key=f"csv_{panel['panel_id']}")
        except Exception:
            st.table(chart)

    st.subheader("All-component coverage matrix")
    st.dataframe([{"component": r["component_id"], "stage": r["stage"], "role": r["execution_role"],
                   "disposition": r["disposition"], "runner_capability": r["native_runner_capability"],
                   "rights": r["rights_state"], "gates": r["n_gates"]}
                  for r in cap["component_matrix"]], width="stretch")

    st.subheader("Executed native reference results")
    st.caption("Each is the component's OWN native reference case, not the common scenario.")
    if report["executed_reference_results"]:
        st.table([{"component": r["component_id"], "runner": r.get("runner_id"),
                   "runtime": r.get("runtime_class"), "status": r["status"]}
                  for r in report["executed_reference_results"]])
        for r in report["executed_reference_results"]:
            if r.get("outputs"):
                with st.expander(f"{r['component_id']} — native outputs"):
                    st.table([{"output": o["name"], "value": o["value"], "unit": o["unit"],
                               "role": o["role"]} for o in r["outputs"]])
    else:
        st.info("No native reference runners executed in this request.")

    with st.expander("Reference-runner coverage (not-yet-implemented / rights-blocked / optional)"):
        st.table([{"component": r["component_id"], "capability": r["native_runner_capability"],
                   "note": r["note"]} for r in cap["reference_suite_coverage"]])

    st.subheader("What this does not prove")
    for s in report["what_this_does_not_prove"]:
        st.markdown(f"- {s}")
    st.caption(report["fidelity_ceiling"])

    st.subheader("Download (full provenance-bearing artifact)")
    st.download_button("Comparison JSON", data=lab.artifact_json(report),
                       file_name="guided_pull_lab.json", mime="application/json")
    st.download_button("Comparison Markdown", data=lab.render_markdown(report),
                       file_name="guided_pull_lab.md", mime="text/markdown")


if __name__ == "__main__":
    main()
