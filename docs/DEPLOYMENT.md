# DEPLOYMENT.md — public Guided Pull Laboratory Explorer (Streamlit Community Cloud)

How the **public** Explorer (`apps/lab_public_app.py`) is hosted. This is the reference for a maintainer;
the actual account connection and the final **Deploy** click are **maintainer actions** (this repository
commits no credentials and performs no deploy).

## What gets deployed

- **App:** `apps/lab_public_app.py` — the public Explorer. Its execution context is fixed to
  `PUBLIC_ARTIFACT` **in code**; it is never selectable by the user, a query string, or an environment
  variable. Live execution is enabled per-model, only for components with affirmative public-execution
  **and** output-publication clearance (today: `brewer2026.lb_reference`). Everything runs through the one
  rights-safe service (`puckworks.product.lab_service`), so the rights preflight runs before any producer.
- **Not** `apps/lab_app.py` — that is the LOCAL/PRIVATE development surface (`LOCAL_PRIVATE`); it is for
  Codespaces / local use and must not be the public entrypoint.

## Hosting parameters (Streamlit Community Cloud)

| Setting | Value |
|---|---|
| Repository | `trbrewer/puckworks` |
| Branch | a **stable, pinned deployment branch or release tag** — **not** `main` |
| Main file path | `apps/lab_public_app.py` |
| Python version | **3.12** |
| Dependencies | `requirements.txt` (repo root) — installs `.[webapp]` (streamlit + matplotlib) + pandas |
| Secrets | **none** — the app needs no secret and stores no user data |

Deploy from a **stable branch or tag**, never auto-deploying every development-`main` commit: the
Laboratory is `0.4.0.dev0` and its surface changes between commits. `requirements.txt` pins to the
deployed revision's own package (`.[webapp]`), so the app files and the installed package never drift.

## Dependency scope

`requirements.txt` installs **only** what the public UI needs: the package (numpy + scipy core), streamlit,
matplotlib, and pandas. It deliberately excludes the optional GPU extra (`taichi`, `[lb]`) and the 3-D
extra (`pyvista`/`vtk`, `[viz3d]`) — neither is used by the public app and both are heavy/platform-bound.

## Privacy / safety posture

- No usage statistics are gathered (`.streamlit/config.toml` sets `gatherUsageStats = false`).
- The app makes no external network request and sends no recipe, result, or identifier to any Puckworks
  service; it logs no recipe values or results.
- No login is required to browse. Browsing the **Model library** runs **no** scientific producer.
- A blocked request produces and displays **no** scientific result — only the rights decision.
- `grudeva2025.reduced` is rights-blocked and never runs (#73).

## Startup verification

- CI: the `codespaces-ci` job boots both `apps/lab_app.py` and `apps/lab_public_app.py` headless and
  asserts `/_stcore/health` returns 200 (a clean-Linux startup smoke).
- Locally: `streamlit run apps/lab_public_app.py` then `curl -s localhost:8501/_stcore/health` → `ok`.

## Human acceptance before advertising the URL (issue #43)

Do **not** add a public README badge or advertise the URL until a human has verified the deployed app
**signed out**:

- opens the deployment URL with no login;
- browses the catalog **keyboard-only**;
- sees an honest **disabled** live-run state when no common-scenario model is cleared, with the
  private-Colab path reachable;
- confirms **no** scientific producer ran during catalog browsing;
- after a component is affirmatively cleared: selects only that component, the `PUBLIC_ARTIFACT` preflight
  passes, exactly that producer runs, and the artifact carries the rights verdict + provenance; an
  uncleared mixed request stays blocked before all producers.

Record the date, reviewer, and checks in issue #43.
