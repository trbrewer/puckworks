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
from puckworks.product import lab, lab_service

try:  # importable both as `streamlit run apps/lab_app.py` and as the `apps.lab_app` module
    from apps.lab_ui_common import BOUNDS, build_request, format_finding, preset_defaults
except ImportError:  # pragma: no cover - streamlit-run path
    from lab_ui_common import BOUNDS, build_request, format_finding, preset_defaults

# This app is the LOCAL/PRIVATE development surface; its execution context is FIXED (never user-selected).
EXECUTION_CONTEXT = "LOCAL_PRIVATE"


def _apply_preset():
    for k, v in preset_defaults(st.session_state.get("preset_id", "pv19_named")).items():
        st.session_state[k] = v


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
    st.caption("This is the LOCAL_PRIVATE surface — private inspection on your machine. It is NOT a "
               "public-hosting clearance; NOT_REVIEWED models are inspectable here but not publicly live.")
    st.json(selection_preview(request))
    # single rights-safe path (shared with the public app + batch): the service runs the rights preflight
    # BEFORE any producer. In LOCAL_PRIVATE only a RIGHTS_BLOCKED selection (e.g. Grudeva) is refused.
    try:
        result = lab_service.execute_lab_request(
            request, execution_context=EXECUTION_CONTEXT,
            provenance=lab.BuildProvenance(package_version=__import__("puckworks").__version__))
    except Exception as exc:                              # useful message, never a stack dump
        st.error(f"Could not run the scenario: {type(exc).__name__}: {exc}")
        return
    if result.blocked:
        st.error("This request was blocked by the rights preflight — no model ran:")
        for b in result.blockers:
            st.markdown(f"- {b}")
        return
    report = result.report

    # domain findings BEFORE results; the run already evaluated the domain through the authoritative
    # product domain and decided whether the producer ran (REJECTED blocks always; WARNING blocks strict).
    st.subheader("Domain findings")
    findings = list(report["domain"]["findings"])
    for f in findings:
        level, text, detail = format_finding(f)
        {"error": st.error, "warning": st.warning, "success": st.success, "info": st.info}[level](text)
        if detail:
            with st.expander("technical reason"):
                st.write(detail)
    if not findings:
        st.success("No domain findings.")
    if report["domain"]["blocked"]:
        st.error(f"Scenario blocked by domain policy ({report['domain']['effective_policy']}); the "
                 f"scientific producer was not run. Reason: {report['domain']['block_reason']}")
        return

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
