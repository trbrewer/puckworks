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

## Net effect

No affirmative outward clearance was recorded this session; every reviewed component remains
`NOT_REVIEWED` (or `RIGHTS_BLOCKED` for Grudeva). The public Laboratory batch is therefore **gated**: a
`PUBLIC_BATCH` / `PUBLIC_ARTIFACT` run blocks before any producer and emits only the rights preflight.
Local/private inspection is unaffected.
