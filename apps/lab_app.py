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
    """(level, text, detail) for a DomainFinding. Unit-testable; no Streamlit dependency."""
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
        request = lab.ScenarioRequest(preset_id=preset_id, overrides=overrides)
        execution = lab.execute_scenario(request)
    except Exception as exc:                              # useful message, never a stack dump
        st.error(f"Could not run the scenario: {type(exc).__name__}: {exc}")
        return

    # domain findings BEFORE results; REJECTED blocks execution
    st.subheader("Domain findings")
    findings = prod.evaluate_domain(prod.load_pull_preset(preset_id)[0]) if not overrides else \
        [f for f in _domain_findings_for(preset_id, overrides)]
    rejected = False
    for f in findings:
        level, text, detail = format_finding(f)
        {"error": st.error, "warning": st.warning, "success": st.success, "info": st.info}[level](text)
        if detail:
            with st.expander("technical reason"):
                st.write(detail)
        rejected = rejected or level == "error"
    if not findings:
        st.success("No domain findings.")
    if rejected:
        st.error("Scenario rejected by the domain policy; not executed.")
        return

    report = lab.build_comparison(execution, provenance=lab.BuildProvenance(
        package_version=__import__("puckworks").__version__))

    st.subheader(f"Scenario: {report['scenario']['scenario_id']}")
    st.json(report["scenario"]["applied_overrides"] or {"overrides": "none (preset defaults)"})

    lens = report["executed_lenses"][0]
    st.subheader("Executed common-scenario lens")
    st.markdown(f"**`{lens['component_id']}`** — {lens['status']} via `{lens['adapter']}`")
    st.table([{"observable": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"],
               "note": o["note"]} for o in lens["observables"]])

    st.subheader("Scientific trace plots")
    for panel in lab.render_data(report):
        st.markdown(f"**{panel['title']}**  — evidence: {panel['evidence_badge']}")
        chart = {panel["x_label"]: panel["x"]}
        for s in panel["series"]:
            chart[f"{s['label']} [{s['role']}, {s['unit']}]"] = s["y"]
        try:
            import pandas as pd
            df = pd.DataFrame(chart).set_index(panel["x_label"])
            st.line_chart(df)
            with st.expander("data table"):
                st.dataframe(df, width="stretch")
        except Exception:
            st.table(chart)

    st.subheader("All-component coverage matrix")
    st.dataframe([{"component": r["component_id"], "stage": r["stage"], "role": r["execution_role"],
                   "disposition": r["disposition"], "runner": r["native_runner_state"],
                   "rights": r["rights_state"], "gates": r["n_gates"]}
                  for r in report["component_matrix"]], width="stretch")

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
        st.table([{"component": r["component_id"], "runner_state": r["runner_state"], "note": r["note"]}
                  for r in report["reference_suite_coverage"]])

    st.subheader("What this does not prove")
    for s in report["what_this_does_not_prove"]:
        st.markdown(f"- {s}")
    st.caption(report["fidelity_ceiling"])

    st.subheader("Download (full provenance-bearing artifact)")
    st.download_button("Comparison JSON", data=lab.artifact_json(report),
                       file_name="guided_pull_lab.json", mime="application/json")
    st.download_button("Comparison Markdown", data=lab.render_markdown(report),
                       file_name="guided_pull_lab.md", mime="text/markdown")


def _domain_findings_for(preset_id, overrides):
    import dataclasses
    recipe, _ = prod.load_pull_preset(preset_id)
    return prod.evaluate_domain(dataclasses.replace(recipe, **overrides))


if __name__ == "__main__":
    main()
