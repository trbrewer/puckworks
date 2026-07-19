# Browser-hosted Guided Pull Laboratory — feasibility note (#43)

**Status: feasibility note only. No browser port is implemented and nothing is deployed to a
third-party host in this work.** This records what a GitHub-Pages / browser-Python port would require,
so a later decision is evidence-based rather than speculative.

## The constraint that dominates

The scientific core is CPython + NumPy/SciPy. GitHub Pages serves **static files only** — no server-side
Python. A browser port therefore means running Python *in the browser* via **Pyodide** (or JupyterLite),
and it must call the **existing authoritative model code** — we will not maintain a second scientific
implementation.

## What to check before attempting a port

1. **Package compatibility (Pyodide).** NumPy and SciPy have Pyodide wheels; confirm the exact versions
   this project pins are available for the target Pyodide release. `puckworks` itself is pure Python and
   should load as a wheel via `micropip`, but every transitive dependency must have a wasm/pure-python
   wheel. Streamlit does **not** run under Pyodide — a browser UI would be a small hand-written HTML/JS
   front end calling Pyodide, or `stlite`, not the Streamlit server used in Codespaces.
2. **Initial download size.** Pyodide + NumPy + SciPy is on the order of tens of MB; measure the real
   cold-load payload for our dependency set and decide whether it is acceptable for a public page.
3. **Startup time.** Cold Pyodide init + wheel install is seconds-to-tens-of-seconds; measure it.
4. **Result parity.** A prototype must produce a comparison result **byte/numerically identical** (within
   a declared tolerance) to `python -m puckworks.product.lab compare` for the same bounded scenario. If
   it cannot, the port is abandoned — no divergent second implementation ships.
5. **CSP + static hosting.** A Pages port needs a strict CSP (as the existing PV interactives use),
   self-contained assets, and must run entirely client-side (no server, no external data fetch during a
   run) — consistent with the project's no-tracking / no-external-network stance.
6. **Accessibility.** The same bar as the PV interactives: labelled native controls, keyboard operation,
   text equivalents for any plot, no color-only meaning, readable tables.

## Decision rule

Implement a browser port **only after** a parity prototype proves Pyodide can call the authoritative
model code and reproduce `lab.build_comparison` within tolerance, at an acceptable payload/startup cost.
Until then, the supported dynamic UI is **Codespaces + Streamlit** (development) and the reproducible
non-interactive path is the **Actions batch runner**.

## Explicitly out of scope here

No deployment to Streamlit Community Cloud, Hugging Face Spaces, Render, or any external application host
— that requires separate operations/privacy authorization and credentials, which are not part of this
work.
