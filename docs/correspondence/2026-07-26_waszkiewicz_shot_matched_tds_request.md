# Data request — shot-matched TDS(t) for the 9-bar flow traces (Waszkiewicz et al. 2026)

**Status:** DRAFT — for Tim to review, address and send.
**Purpose:** unblocks Paper 2 (B2) review items 4.3/4.4, the leave-one-shot-out cross-fit of Φ(t).
**Why it cannot be unblocked by analysis:** Φ(t) = m_d(t)/m₀ is reconstructed from TDS(t) × Q(t).
The Zenodo deposit publishes **3 TDS replicates** and **5 flow traces at 9 bar**, but the replicates
are not identified with individual shots. A held-out shot therefore cannot have its own Φ(t)
rebuilt, so the cross-fit is blocked on *identification*, not on effort or method.

## Recipients

Primary: **Marcel Lisicki** and **Bogdan Szymczak** (corresponding authors, Phys. Fluids 38, 063113).
Suggested cc: Maciej Waszkiewicz (first author).
Addresses are on the article's title page — please fill them in before sending; they are not
recorded in this repository.

## What we are asking for, precisely

One of the following, in descending order of usefulness:

1. **Shot-level identification of the existing TDS replicates** — which TDS replicate (if any)
   corresponds to which of the five 9-bar flow traces. If the mapping exists in lab notes, this
   alone unblocks the analysis and requires no new measurement.
2. **Per-shot TDS(t) series** for the five 9-bar shots, if more were recorded than were deposited.
3. **A statement that no such pairing exists** — that the TDS replicates and the flow traces were
   run as separate campaigns. This is genuinely useful: it lets us close the item as
   *not obtainable* rather than leave it indefinitely open.

Answer (3) is a perfectly good answer and we would rather have it than silence.

---

## Suggested message

> **Subject:** Espresso poroelastic data — are the TDS replicates matched to individual 9-bar shots?
>
> Dear Dr Lisicki and Dr Szymczak,
>
> I am working on an independent re-analysis of the time-dependent part of your poroelastic
> espresso model (*Under pressure: Poroelastic regulation of flow in espresso brewing*, Phys.
> Fluids **38**, 063113, 2026), using the CC-BY data you deposited at
> doi:10.5281/zenodo.18046315. Thank you for making it public — the deposit is unusually complete,
> and our re-implementation reproduces your published calibration pair
> (P_c, Q_c) = (12.39 bar, 1.897 g s⁻¹) and your parameter-free 9-bar Q(t) trace.
>
> I have one question about the deposit's structure.
>
> We are evaluating the Φ(t) construction per shot rather than against the across-shot mean, so
> that we can report a **leave-one-shot-out** result: hold out one of the five 9-bar traces, build
> Φ(t) without it, and predict it. Because Φ(t) = m_d(t)/m₀ is reconstructed from TDS(t) × Q(t),
> that requires knowing which TDS measurement belongs to which shot. The deposit contains three
> TDS replicates and five 9-bar flow traces, and I could not find a field identifying them with
> one another.
>
> So: **are the three TDS replicates matched to individual 9-bar shots, and if so, which?** If the
> pairing exists in your records, even informally, it would let us report a genuine held-out result
> instead of the weaker statement we can currently support. If more per-shot TDS series were
> recorded than were deposited, those would be equally welcome.
>
> If no such pairing exists — if the TDS replicates and the flow traces were separate runs — please
> just say so. That is an entirely satisfactory answer and lets us state the limitation precisely
> rather than leave it open.
>
> For transparency about what we currently report: evaluated per shot over 15–95 s at 9 bar, your
> Φ(t) construction beats a constant-flow baseline in **all five** shots (mean RMSE 0.19 vs
> 0.58 g s⁻¹). We describe it as a **zero-free-parameter prediction**, and we explicitly do *not*
> call it a cross-fit, precisely because Φ(t) is not rebuilt per held-out shot. We would rather fix
> that than caveat it.
>
> Two notes on how your work is used. Your analysis code is GPLv3 and we have deliberately **not**
> ingested it; our component is an independent re-expression of the published equations. The data
> we use are the CC-BY-4.0 Zenodo series, attributed per-dataset in our manifest. We are happy to
> share our re-implementation and results before anything is submitted, and would welcome your
> correction if we have misread the model.
>
> With thanks and best regards,
>
> Tim Brewer
> brewer@synthetik-technologies.com

---

## Notes for Tim before sending

- **Fill in the addresses** from the article title page. This repository does not hold them, and I
  have not guessed them.
- Every number quoted in the message is producer-backed:
  `puckworks/analysis/waszkiewicz_shot_level.py::per_shot_ladder()` — 5 shots, 15–95 s, 9 bar,
  `rung4_phi_of_t` mean RMSE 0.1894 g s⁻¹ vs `rung1_const` mean 0.5798 g s⁻¹, 5/5 shots.
  The calibration pair is from `gate_waszkiewicz_static_refit`.
- The message deliberately offers "no pairing exists" as an acceptable answer. An unanswered
  request leaves item 4.3/4.4 open forever; an explicit "no" closes it as *not obtainable*, which
  is a reportable outcome.
- It does **not** ask for anything paywalled or GPL-encumbered, and it states our licence posture
  up front so the rights position is unambiguous on first contact.
