"""Public Guided Pull Laboratory Explorer — a hosted, sign-out-friendly Streamlit app (#43 / #70).

Reachable by one URL. Its execution context is FIXED to ``PUBLIC_ARTIFACT`` in code — it is NOT selectable
by the user, a query string, or an environment variable. Everything runs through the one rights-safe
service (``puckworks.product.lab_service``): the rights preflight runs before any producer, and only
components with affirmative public-execution AND output-publication clearance can ever run live. The app
is useful even when NO component is publicly cleared: the producer-free **Model library** always works,
and the live-run controls are disabled with a plain explanation + a private-Colab link.

Deploy: Streamlit Community Cloud, Python 3.12, entrypoint ``apps/lab_public_app.py``, deps in
``requirements.txt``. No secret, no telemetry, no user data leaves the app.
"""
from __future__ import annotations

import json

import streamlit as st

from puckworks.product import lab, lab_explorer, lab_service

try:  # importable both as `streamlit run apps/lab_public_app.py` and as `apps.lab_public_app`
    from apps.lab_ui_common import (BOUNDS, COLAB_LAB_URL, PLAIN_LABELS, build_public_selfcheck_request,
                                    default_reference_shot_public_ready, novice_result_sections,
                                    panel_table, public_live_ids)
except ImportError:  # pragma: no cover - streamlit-run path
    from lab_ui_common import (BOUNDS, COLAB_LAB_URL, PLAIN_LABELS, build_public_selfcheck_request,
                               default_reference_shot_public_ready, novice_result_sections,
                               panel_table, public_live_ids)

# The public context is a hard-coded constant — never read from the user, a query string, or the env.
EXECUTION_CONTEXT = "PUBLIC_ARTIFACT"
VIEWS = ("Try a reference shot", "Component self-checks", "Model library")


# ── pure helpers (unit-testable; no Streamlit) ───────────────────────────────────────
def public_artifact_bundle(result) -> dict:
    """The downloadable public artifact for an ALLOWED self-check run: the rights-preflight verdict +
    execution context + the full provenance-bearing comparison. Never called for a blocked result."""
    if result.blocked or result.report is None:
        raise ValueError("no public artifact for a blocked request")
    return {"report": "puckworks-public-lab-artifact", "execution_context": result.execution_context,
            "rights_preflight": result.rights_preflight, "comparison": result.report}


def run_public_selfcheck(selected_ids):
    """Build + run a selected-references-only PUBLIC_ARTIFACT request through the shared service. Returns
    the typed LabRequestResult (blocked or allowed). Selection is guarded to publicly-cleared components."""
    request = build_public_selfcheck_request(selected_ids)
    return lab_service.execute_lab_request(request, execution_context=EXECUTION_CONTEXT)


# ── views ────────────────────────────────────────────────────────────────────────────
def _model_library():
    st.subheader("Model library")
    st.caption("Browse every model in Puckworks. This page runs **no** simulation — it is catalog "
               "information only.")
    cat = lab_explorer.explorer_catalog()
    live = cat["public_live_component_ids"]
    st.write(f"**{cat['n_components']}** models. Publicly runnable today (rights-cleared): "
             + (", ".join(f"`{c}`" for c in live) if live else "_none yet_") + ".")
    rows = [{"Model": r["component_id"], "What it covers": r["plain_stage"], "Role": r["plain_role"],
             "Evidence": r["evidence_strength"], "Availability": ("public live" if r["public_live_available"]
                                                                  else (r["unavailable_reason"] or "—")),
             "Code": r["code_rights_state"], "Data": r["data_rights_state"],
             "Output": r["output_redistribution_state"]}
            for r in cat["components"]]
    st.dataframe(rows, width="stretch")
    st.caption("Rights are per-model and separate (code / data / output). NOT_REVIEWED is a visible gap, "
               "never a clearance; a rights-blocked model never runs.")


def _try_reference_shot():
    st.subheader("Try a reference shot")
    ready = default_reference_shot_public_ready()
    if not ready:
        st.warning("The recipe-driven reference shot is **not available to run on this public page yet** — "
                   "its model has not completed an affirmative public rights review. This is a pending "
                   "review, not an error.")
        st.markdown(f"You can run it **privately** in your own browser runtime instead: "
                    f"[Run privately in Colab]({COLAB_LAB_URL}).")
        st.info("Meanwhile, open **Model library** to browse every model, or **Component self-checks** to "
                "run the models that *are* publicly cleared.")
        return
    # (reached only once a common-scenario lens is affirmatively public-cleared)
    with st.form("reference_shot"):
        dose = st.number_input("Dose (g)", *BOUNDS["dose_g"], value=20.0, step=0.5,
                               help="How much dry coffee.")
        bev = st.number_input("Beverage mass (g)", *BOUNDS["target_beverage_g"], value=40.0, step=1.0,
                              help="How much espresso in the cup.")
        pres = st.number_input("Pressure (bar)", *BOUNDS["pressure_bar"], value=9.0, step=0.5,
                               help="Brew pressure.")
        with st.expander("Advanced (optional)"):
            st.number_input("Temperature (°C)", *BOUNDS["brew_temperature_c"], value=93.0, step=1.0,
                            help="Brew temperature.")
            st.radio(PLAIN_LABELS["domain_policy"], [PLAIN_LABELS["warn"], PLAIN_LABELS["strict"]],
                     help="Whether to run when the recipe is outside the model's evidence range.")
        st.form_submit_button("Run")   # wired when a public common lens exists
    st.info("A publicly-cleared recipe model is not configured yet; see Component self-checks.")


def _render_result(result):
    if result.blocked:
        st.error("This request was blocked by the rights preflight — **no** model ran and no result was "
                 "produced:")
        for b in result.blockers:
            st.markdown(f"- {b}")
        return
    rep = result.report
    st.success("Ran under the PUBLIC_ARTIFACT rights preflight (allowed).")
    for heading, kind, payload in novice_result_sections(rep):
        st.markdown(f"**{heading}**")
        if kind == "table":
            st.table(payload or [{"note": "no common-scenario observables (self-check run)"}])
        elif kind == "status":
            text, level = payload
            {"error": st.error, "warning": st.warning, "success": st.success}[level](text)
        elif kind == "list":
            for s in payload:
                st.markdown(f"- {s}")
        else:
            st.write(payload)
    # component self-checks (each is the component's own reference case, not a prediction of a shot)
    refs = rep.get("executed_reference_results", [])
    if refs:
        st.markdown("**Component self-checks** (each is the model's own reference case, not a shot prediction)")
        for r in refs:
            st.markdown(f"`{r['component_id']}` — {r['status']} — {r.get('runtime_class')}")
            if r.get("outputs"):
                st.table([{"output": o["name"], "value": o["value"], "unit": o["unit"], "role": o["role"]}
                          for o in r["outputs"]])
            st.caption(r.get("fidelity_ceiling", ""))
    _plots(rep)
    # the download carries the rights preflight + provenance
    bundle = public_artifact_bundle(result)
    # PW-APP-002: canonical, deterministic bytes — allow_nan=False and NO default=str masking, so a
    # non-JSON-native value surfaces instead of being silently stringified into the downloaded artifact.
    st.download_button("Download artifact (JSON, includes rights preflight + provenance)",
                       data=json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False,
                                       allow_nan=False),
                       file_name="public_lab_artifact.json", mime="application/json")


def _plots(rep):
    panels = lab.render_data(rep)
    if not panels:
        st.caption("No time-series trace for a self-check-only run (the results above are the summaries).")
        return
    st.markdown("**Plots** (each y-axis carries exactly one unit)")
    for panel in panels:
        st.markdown(f"{panel['title']} — y-axis: {panel['unit']}")
        try:
            import pandas as pd
            df = pd.DataFrame({panel["x_label"]: panel["x"],
                               **{f"{s['label']} [{s['role']}]": s["y"] for s in panel["series"]}}
                              ).set_index(panel["x_label"])
            st.line_chart(df, y_label=panel["y_label"], x_label=panel["x_label"])
        except ImportError:
            st.caption("_(interactive chart needs pandas; showing the data table below)_")
        except Exception as exc:                          # noqa: BLE001 - chart is optional; degrade to the table
            st.caption(f"_(chart unavailable: {type(exc).__name__}; showing the data table below)_")
        tbl = panel_table(panel)                          # text alternative (accessibility): always present
        with st.expander("data table (text alternative)"):
            st.table([dict(zip(tbl["headers"], row)) for row in tbl["rows"]])


def _component_self_checks():
    st.subheader("Component self-checks")
    st.caption("Run a model's OWN reference case (not a prediction of your shot). Only models with an "
               "affirmative public rights review appear here.")
    live = public_live_ids()
    if not live:
        st.info("No component is publicly cleared to run live yet. Browse **Model library**, or "
                f"[run privately in Colab]({COLAB_LAB_URL}).")
        return
    selected = st.multiselect("Component self-checks to run (publicly cleared only)", live, default=live,
                              help="Each runs the model's own provenance-bound reference case.")
    if st.button("Run selected self-checks", disabled=not selected):
        result = run_public_selfcheck(selected)
        _render_result(result)


def main():
    st.set_page_config(page_title="Puckworks — Guided Pull Laboratory (public)", page_icon="☕",
                       layout="wide")
    st.title("Puckworks — Guided Pull Laboratory")
    st.caption("Explore the espresso model registry in your browser. This is an honest research tool — "
               "**not** a digital twin, recipe optimizer, taste predictor, or validated simulator. "
               "Live execution is enabled per-model, only after an affirmative public rights review.")
    view = st.radio("View", VIEWS, horizontal=True, help="Browse models, or run the publicly-cleared ones.")
    if view == "Model library":
        _model_library()
    elif view == "Component self-checks":
        _component_self_checks()
    else:
        _try_reference_shot()
    st.divider()
    st.caption("Runs in the PUBLIC_ARTIFACT context (fixed). No login is required to browse. No usage "
               "data, recipe, or result is sent to any Puckworks service. grudeva2025.reduced is "
               "rights-blocked and never runs (issue #73).")


if __name__ == "__main__":
    main()
