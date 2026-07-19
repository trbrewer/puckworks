# Rights review notes (public Laboratory outward use)

A bounded evidence review of the components whose outputs would enter a **public** Guided Pull
Laboratory artifact. Rights are use-specific (see `puckworks.rights`): code execution, data use, and
output redistribution are separate. A public batch/artifact is gated by `lab_rights_gate` and refuses any
component that is not **affirmatively** cleared for the requested outward use — a `NOT_REVIEWED` state is
a visible gap, never "clear."

Nothing here changes a rights record. Where the evidence available in-session is insufficient for a
self-service affirmative determination, the component is **retained `NOT_REVIEWED` and the outward path is
blocked** (a maintainer determination is required). Article/equation rights are never treated as code
rights (see #73 for the contrasting Grudeva case).

## Review order and findings

1. **`cameron2020.extraction_bdf`** (the only common-scenario lens)
   - **Code:** the module (`puckworks/models/cameron2020/extraction_bdf.py`) documents a *Python
     reimplementation* of the multiscale model from Cameron et al., *Matter* 2, 631–648 (2020),
     mapping the paper's Eqs. 18–22; the card status is "gated (reimplementation validated)". There is
     **no** port/copy claim (contrast Grudeva 2025's self-documented "faithful port" of unlicensed
     upstream code). This is materially consistent with `INDEPENDENT_REIMPLEMENTATION`.
   - **Not yet self-clearable in-session:** an affirmative determination also needs a maintainer to
     confirm the absence of any copied upstream *supplementary code* (if the article's SI shipped code
     under a restrictive licence) — which cannot be fully verified from this session.
   - **Output/data:** the Lab runs Cameron on the Puckworks-owned `pv19_named` preset; the outputs are
     Puckworks-derived time histories, not the paper's data. Output redistribution is plausibly clear,
     but rides on the code determination above.
   - **Conclusion:** review performed; evidence documented; **retained `NOT_REVIEWED`**; public
     execution and output publication remain **blocked** pending a maintainer determination.

2–4. **`waszkiewicz2025.poroelastic`, `wadsworth2026.permeability`, `foster2025.infiltration`**
   (native reference runners)
   - Each runner reproduces the **authors' own reference data** (Waszkiewicz calibration curve,
     Wadsworth Table 1, the Foster DE1 fixture). Publishing those outputs in a public artifact raises a
     genuine **data-redistribution** question distinct from the code.
   - **Conclusion:** **retained `NOT_REVIEWED`**; native-reference outputs remain **blocked** for public
     publication. A public artifact must therefore run Cameron-only (`--references none`) — and even then
     is blocked until Cameron's review completes.

5. **`romancorrochano2017.extraction`** — assessed in the Phase 6 lens work; execution-ready on the
   shared scenario but `NOT_COMPARABLE` with Cameron EY/TDS, and not cleared for public outward use.

6. **Datasets / fixtures** the public outputs would depend on: the `pv19_named` preset (Puckworks-owned)
   for Cameron; the native-reference fixtures embed authors' source data (see 2–4). No dataset is
   affirmatively cleared for public redistribution in-session.

## Bounded affirmative review — `brewer2026.lb_reference` (2026-07-19, #70)

- **Component ID:** `brewer2026.lb_reference`.
- **Review date:** 2026-07-19.
- **Files / commits inspected:** `puckworks/models/brewer2026/lb_reference.py` (git blame: 138/138 lines
  Tim Brewer; introduced `c54a2a6` "puckworks v0.1.0"; full history is that single commit — no later
  edits); its registry declaration in `puckworks/models/__init__.py`; the authoritative gate
  `puckworks.validation.gates.gate_lb_channel`; the registry gate result (`err_pct = 0.052`, passes
  `abs(err) < 0.5`). Provenance-marker grep of the module returned no `port` / `copyright` / `licence` /
  `adapted from` / `based on` / upstream-solver marker (the only matches were the substring "port" inside
  `import`).
- **Code provenance / redistribution:** **`CLEAR`.** First-party in-repo code authored by the maintainer;
  a self-contained numpy D3Q19 TRT lattice-Boltzmann kernel. No port/copy claim anywhere in the module
  (contrast Grudeva 2025's self-documented "faithful port" of unlicensed upstream code). The D3Q19
  lattice stencil constants (`C`, `W`, `OPP`) are standard textbook LB facts, not copyrightable content.
- **Data / input provenance:** **`NOT_APPLICABLE`.** The verification input is generated synthetically in
  code — the gate constructs a plane-channel `solid` boolean array in memory. No third-party experimental
  dataset, velocity field, or numerical result is read, bundled, or redistributed (the module reads no
  input files; its `__main__` block only *writes* a scratch JSON).
- **Generated-output redistribution:** **`CLEAR`.** The outputs (simulated lattice permeability, the
  analytic plane-Poiseuille reference `k = h²/12`, and their relative error) are first-party numerical
  content produced by first-party code from a synthetic input.
- **Limitations of the determination:** this is a **numerical code-verification** clearance only. It does
  **not** establish that a porous coffee-bed simulation predicts espresso, and carries no claim of
  experimental accuracy or beverage fidelity. It is bounded to the LB plane-channel verification path
  (the runner and outputs of §"Native LB reference runner" once added); it does not extend to
  `brewer2026.lb_taichi`, `brewer2026.pack_generator`, or any other component.
- **Decision issue:** #70.
- **Explicit non-application:** this conclusion applies to `brewer2026.lb_reference` **only**. It does
  **not** clear Cameron, Grudeva, Roman-Corrochano, Wadsworth, Waszkiewicz, Foster, or any other
  component, author, model class, or namespace. Those remain `NOT_REVIEWED` (or `RIGHTS_BLOCKED` for
  Grudeva, #73). A rights record is per-component and never propagates.

## Net effect

`brewer2026.lb_reference` is the **first** component with an affirmative outward clearance (code `CLEAR`,
data `NOT_APPLICABLE`, output `CLEAR`) — bounded to its synthetic LB channel code-verification path. Every
other reviewed component remains `NOT_REVIEWED` (or `RIGHTS_BLOCKED` for Grudeva). A `PUBLIC_ARTIFACT`
request therefore passes preflight **only** when it selects exactly the affirmatively-cleared component(s);
a default/broad public request still blocks before any producer and emits only the rights preflight.
Local/private inspection is unaffected.
