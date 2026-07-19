"""Guided Pull Laboratory — a small Streamlit development UI (PV-19B / #43 / #70).

Development-only (`0.4.0.dev0`). It calls ONLY the supported `puckworks.product` API and the Guided
Pull Laboratory comparison API — it re-implements no scientific equation, hard-codes no science number,
makes no external network request, and stores no user data. Run it in Codespaces or locally::

    pip install -e ".[dev,viz,webapp]"
    streamlit run apps/lab_app.py

`puckworks` core never imports this module (it lives outside the package), so installing the core wheel
never pulls in the web stack.
"""
from __future__ import annotations

import dataclasses

import streamlit as st

import puckworks.product as prod
from puckworks.product import lab

# bounded input ranges (the widgets enforce these; no silent clamp of a model parameter)
DOSE = (5.0, 30.0, 18.0)
BEVERAGE = (10.0, 80.0, 36.0)
PRESSURE = (1.0, 12.0, 9.0)
TEMPERATURE = (80.0, 98.0, 92.0)


@st.cache_data(show_spinner=False)
def _presets():
    return list(prod.available_pull_presets())


def _build_run(preset_id, dose_g, target_beverage_g, pressure_bar, brew_temperature_c):
    recipe, config = prod.load_pull_preset(preset_id)
    recipe = dataclasses.replace(
        recipe, dose_g=float(dose_g), target_beverage_g=float(target_beverage_g),
        pressure_bar=float(pressure_bar), brew_temperature_c=float(brew_temperature_c))
    findings = prod.evaluate_domain(recipe)
    # route the run through the shared public helper so UI == package == batch output
    run = lab.run_scenario(preset_id, dose_g=dose_g, target_beverage_g=target_beverage_g,
                           pressure_bar=pressure_bar, brew_temperature_c=brew_temperature_c)
    return recipe, findings, run


def main():
    st.set_page_config(page_title="Guided Pull Laboratory", page_icon="☕", layout="wide")
    st.title("Guided Pull Laboratory")
    st.caption("Development UI (0.4.0.dev0) — independent model lenses over one bounded scenario. "
               "Not a validated digital twin; competing mechanisms are never averaged. "
               "Every number comes from a named producer.")

    with st.form("scenario"):
        st.subheader("Scenario")
        col1, col2, col3 = st.columns(3)
        with col1:
            preset_id = st.selectbox("Preset / scenario", _presets(),
                                     help="A fixed, rights-independent reference recipe.")
            dose_g = st.number_input("Dose (g)", DOSE[0], DOSE[1], DOSE[2], step=0.5)
        with col2:
            target_beverage_g = st.number_input("Target beverage mass (g)", BEVERAGE[0], BEVERAGE[1],
                                                 BEVERAGE[2], step=1.0)
            pressure_bar = st.number_input("Pressure (bar)", PRESSURE[0], PRESSURE[1], PRESSURE[2],
                                           step=0.5)
        with col3:
            brew_temperature_c = st.number_input("Temperature (°C)", TEMPERATURE[0], TEMPERATURE[1],
                                                 TEMPERATURE[2], step=1.0)
            st.text_input("Grinder / particle input",
                          value="reference recipe (no universal dial→size conversion)", disabled=True,
                          help="A grinder dial is not a universal particle size; no conversion is applied.")
        show_refs = st.checkbox("Show the component reference suite", value=True)
        run_clicked = st.form_submit_button("Run comparison", type="primary")

    if not run_clicked:
        st.info("Set the bounded scenario above and press **Run comparison**. Expensive models run "
                "only when you press Run.")
        return

    try:
        recipe, findings, run = _build_run(preset_id, dose_g, target_beverage_g, pressure_bar,
                                           brew_temperature_c)
        report = lab.build_comparison(run)
    except Exception as exc:                      # fail with a useful message, never a stack dump
        st.error(f"Could not run the comparison: {type(exc).__name__}: {exc}")
        return

    # domain warnings BEFORE results
    st.subheader("Domain findings")
    if findings:
        for f in findings:
            status = getattr(f, "status", "")
            msg = getattr(f, "message", str(f))
            (st.warning if str(status).lower() not in ("ok", "in_domain") else st.success)(
                f"{getattr(f, 'field', '')}: {msg}")
    else:
        st.success("No domain findings.")

    # executed common-scenario lens
    st.subheader("Executed common-scenario lens")
    lens = report["executed_lenses"][0]
    st.markdown(f"**`{lens['component_id']}`** — {lens['status']} via `{lens['adapter']}`")
    st.table([{"observable": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"]}
              for o in lens["observables"]])

    # coverage matrix
    st.subheader("All-component coverage matrix")
    st.dataframe([{"component": r["component_id"], "stage": r["stage"], "role": r["execution_role"],
                   "disposition": r["disposition"], "gates": r["n_gates"]}
                  for r in report["component_matrix"]], width="stretch")

    # dispositioned / excluded (never hidden)
    with st.expander("Excluded / dispositioned components (honest, not hidden)"):
        for e in report["excluded_or_dispositioned"]:
            st.markdown(f"- `{e['component_id']}` — **{e['disposition']}**: {e['reason']}")

    if show_refs:
        st.subheader("Component reference suite")
        st.caption("Each is the component's OWN native reference case, not the common scenario.")
        st.table([{"component": r["component_id"], "status": r["status"]}
                  for r in report["component_reference_suite"]])

    # what this does not prove
    st.subheader("What this does not prove")
    for s in report["what_this_does_not_prove"]:
        st.markdown(f"- {s}")
    st.caption(report["fidelity_ceiling"])

    # downloads
    st.subheader("Download")
    st.download_button("Comparison JSON", data=lab.canonical_json(report),
                       file_name="guided_pull_lab.json", mime="application/json")
    st.download_button("Comparison Markdown", data=lab.render_markdown(report),
                       file_name="guided_pull_lab.md", mime="text/markdown")


if __name__ == "__main__":
    main()
