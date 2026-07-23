# Model card: Barletta 2025 neural inverse map (surrogate + inversion)

**Paper:** Barletta, A.; Cuomo, S.; Egidi, N.; Giacomini, J.; Maponi, P. "Inverse modeling of porous flow through deep neural networks: the case of coffee percolation." arXiv:2511.11194v1 [math.NA], 14 Nov 2025 (preprint, no DOI).
**Stage(s):** extraction · observables · **Kind:** calibration
**Status:** card-only

## Scope and mechanism
Three objects stacked: (1) a forward multiphysics percolation model (their System 7 = Richards + Darcy + per-species ADR + solid balance + heat) that is the **same Camerino-lineage model already carded as angeloni2023** (their refs [11]=Giacomini 2020 IJMF, [2]=Angeloni 2023), with the identical 8 named species and the identical fitted α(T,p) dissolution polynomial; (2) a compact feed-forward **neural surrogate** f̂_ϕ that emulates the reduced forward operator f: recipe(R⁷) → cup-chemistry(R⁸); and (3) the paper's real contribution — a learned **inverse map** g_θ that reconstructs brewing parameters (temperature, grind-size class, blend fractions) from a target cup-chemistry vector, trained with a cycle-consistency term through the frozen surrogate. The paper also formalizes when a local inverse exists (Constant Rank Theorem: C¹ forward operator + locally constant nondegenerate Jacobian rank). **Everything is trained and "validated" on simulator output only** — there is no experimental campaign in this paper; the single sensorial session is qualitative.

## Governing equations
Forward model, their System (7), radial-symmetric domain C, t ∈ (0, τ) — **identical to angeloni2023 Eqs (1),(8),(9); reproduced here only for provenance, not because anything is new:**

1. **Richards (mass):** S₀ ∂h/∂t + ∇·q = 0
2. **Darcy:** q = −K f_μ · (∇h + χ e)
3. **ADR, liquid species k** (k = 1…N_s): ε ∂C_k/∂t + q·∇C_k + ∇·j_k = R_k, with Fick flux j_k = D_k·∇C_k
4. **Solid species k:** ε_s ∂C_k^s/∂t = R_k^s, ε_s = 1 − ε
5. **Heat:** (ε ρ_c + ε_s ρ^s c^s) ∂T/∂t + ρ_c q·∇T − ∇·(Λ·∇T) = 0

Reaction closure (unnumbered, after Eq. 7):
6. R_k = α_k (1 − ε) C_k^s ,  R_k^s = −α_k (1 − ε) C_k^s
   *(Sign convention here is liquid-gains / solid-loses. This is **flipped relative to the transcription in the angeloni2023 card** (which has R_k = −…, R_k^s = +…). Barletta's signs are the physically sensible dissolution direction; the discrepancy is a transcription/convention difference between the two papers, flagged not resolved.)*

Dissolution-rate polynomial (unnumbered):
7. α_k = A₀ + a T_z0 + b p_z0 + c T_z0² + d p_z0² + f T_z0 p_z0 + l T_z0² p_z0 + m T_z0 p_z0²
   coefficients species/granulometry/variety-dependent — **the angeloni2023 Appendix-A surrogate; coefficient tables are not reprinted here.**

Reduced forward operator, their Eqs (12)–(18):
8. f := Π ∘ S ∘ E,  f: Ω_rcp ⊆ R⁷ → Ω_chm ⊂ R⁸
   x = (x_T, x_p, x_gran, x¹…⁴_distr) = (water temp, pressure, grind size, 4 blend mass fractions);
   y = (y_caf, y_chl, y_tri, y_fer, y_tar, y_cit, y_ace, y_lip). S = numerical solver of System (7); E embeds recipe into full parameter set; Π projects final fields to cup concentrations at t_end.

Inverse-learning objective (the actual model), their Eqs (21)–(23), (34)–(40):
9. min_θ L_total = L_multi + β L_recon,  β = 3 (Eq. 40)
   L_multi = Σ_i w_i L_i (Eq. 34), fixed a-priori weights; heads:
   - L_distrib = 0.8‖y−ŷ‖²₂ + 0.2‖y−ŷ‖₁ + λ_s‖ŷ‖₁, λ_s = 1e−3 (Eq. 35, softmax head)
   - L_temp = 0.7 w(x)‖y−ŷ‖²₂ + 0.3 w(x)‖y−ŷ‖₁, w = α=1.5 if ŷ overestimates else 1 (Eq. 36, asymmetric)
   - L_press = ‖y_press − ŷ_press‖²₂ (Eq. 37) — **inert: pressure fixed at 9 bar, never inferred**
   - L_gran = −Σ_k y_gran,k log ŷ_gran,k (Eq. 38, cross-entropy)
   - L_recon = ‖f̂_ϕ(g_θ(y)) − y‖²₂ (Eq. 39, consistency through frozen surrogate)

Mixture-linearity assumption used for augmentation, their Eq. (25):
10. f(Σᵢ cᵢ Pᵢ) ≈ Σᵢ cᵢ f(Pᵢ),  Σᵢ cᵢ = 1
    cup chemistry of a blend ≈ convex combination of pure-fraction chemistries. (Verified on simulator: MAD < 1e−3 for 4-component, ~machine precision for binary. Note this is close to tautological — angeloni Eq. 8 is linear in solid inventory C_k^s and blend inventories add linearly in fractions, so linearity is largely built in.)

Symbols (forward model): as in the angeloni2023 card (h hydraulic head, q Darcy flux, S₀ storage, K conductivity tensor, f_μ/χ viscosity/buoyancy closures — forms never given, ε porosity, C_k/C_k^s liquid/solid conc., D_k dispersion tensor, α_k dissolution rate, ρ_c/ρ^s c^s heat capacities, Λ thermal conductivity tensor). ML symbols: f̂_ϕ surrogate NN; g_θ inverse NN; ŷ predictions; w_i task weights.

## Parameters
No new **physical** parameters — all inherited from the angeloni2023 / Giacomini 2020 lineage and not restated in this paper. What the paper actually specifies are ML/design and dataset-generation settings:

| symbol | value | units | source |
|---|---|---|---|
| dataset grid: temperature | 7 values, 88–98 (approx. equispaced) | °C | nominal (design) |
| dataset grid: pressure | 9 (fixed; machine not adjustable) | bar | nominal (design) |
| dataset grid: granulometry | 3 classes G/O/F → 0/1/2 | – | nominal (design) |
| dataset grid: composition | 4 fractions, step 1/6, Σ=1 | – | nominal (design) |
| N₀ original samples | 1759 | – | nominal (simulated) |
| augmentation: mixture / temperature | 3000 / 3000 | – | nominal (Eqs. 25–32) |
| total augmented | 7759 (70/15/15 train/val/test) | – | nominal |
| off-grid set | 153 pts, T = 89 / 92.5 / 95 | °C | nominal (simulated) |
| surrogate f̂_ϕ | feed-forward, MSE+MAE, batchnorm, dropout, early stop | – | nominal (architecture) |
| inverse backbone | 256–128–64, ReLU, batchnorm, dropout p=0.15 | – | nominal |
| inverse heads | softmax (distrib), sigmoid reg (T, p), softmax (grind) | – | nominal |
| optimizer | Adam, lr 5e−4, ReduceLROnPlateau (patience 150, factor 0.98) | – | nominal |
| early stopping | patience 300, Δ_min 1e−4; ~3–4e3 epochs to converge | – | nominal |
| loss weights | β=3, λ_s=1e−3, temp α=1.5, distrib 0.8/0.2, temp 0.7/0.3 | – | assumed (author-chosen a priori) |
| hardware | 256 GB RAM, RTX 4090, Threadripper 7995WX 96-core | – | reported |

## Calibration and validation offered by the source
**All metrics are self-consistency on synthetic held-out data — the NN recovering the simulator's own inputs from the simulator's own outputs. There is no comparison to any physical measurement.**

Surrogate f̂_ϕ (Table 1), per-solute R² on held-out simulated test set: caffeine 0.9989, chlorogenic 0.9985, trigonelline 0.9984, citric 0.9979, acetic 0.9908, tartaric 0.9986, ferulic 0.9990, lipids 0.9965 (MSE 3e−8…1.04e−4). This measures only how well a small NN emulates the angeloni-lineage solver on data drawn from that solver — an interpolation/compression check.

Inverse g_θ (Tables 2–3), same held-out simulated set: Temperature MSE 0.0215 / MAE 0.0876 / R² 0.9978; Distribution vector MSE 0.002618 / MAE 0.031899 / R² 0.9573; granulometry classification perfect (precision/recall/F1 = 1.00 across 1164 samples). The authors themselves attribute the perfect grind classification to the three grind classes forming **well-separated clusters in the simulated chemistry space** (Fig. 7 PCA) — an artifact of the simulator's structure, not evidence about real coffee. Pressure metrics omitted because pressure is fixed (the head "infers" a constant). The paper's own Conclusions concede that **experimental validation against real extractions is future work.**

Net: this is a *verification-only* result (model-vs-model, and in fact NN-vs-its-own-training-simulator), the weakest tier in the registry's validation hierarchy. No independent data, no held-out condition/variety, no lab reference.

## Assumptions and validity range
- Forward physics = angeloni2023 wholesale: saturated post-imbibition bed, isotropic/homogeneous medium, fitted machine-specific α(T,p), no c_sat cap, groundwater-scale dispersivities. All of that model's failure modes carry over (see angeloni2023 card).
- Training/eval domain is **entirely in-silico**: T 88–98 °C, p = 9 bar only, 3 grind classes, 4-fraction blends of components labelled A/R/L/E. Pressure is not a live variable — the "pressure head" is decorative.
- Inverse map is a *right*-inverse selection on a manifold: where f is non-injective it returns one locally-stable preimage, not the preimage. Validity of the Constant-Rank premise is asserted from qualitative LPCA on the simulated data, not proven.
- Mixture linearity (Eq. 25) assumed and used to manufacture 3000 augmented points; verified only on the simulator and largely implied by the model's linearity in solid inventory.
- Cup-chemistry y appears in **normalized/scaled units** (Figs. 1–4 axes run ~0.05–1.3, not g/L); values are not directly physical concentrations.
- Silent on everything dynamic: no pressure profiling, no flow/permeability, no imbibition, no time-resolved cup traces, no real blend beyond the four synthetic fractions.

## Interface mapping
Inputs consumed (forward surrogate): a recipe assembled from **GrindState** (grind class → x_gran), **MachineState** (inlet temperature → x_T; pressure pinned 9 bar), and 4 blend mass fractions (no registry contract field — blend composition is outside the current contracts).
Outputs produced (forward surrogate): an 8-vector of scaled species concentrations → nominally **ShotResultState** traces/EY territory, but as a single black-box NN it collapses grind+machine+extraction+observables into one opaque map — the mega-coupling-via-ML the registry avoids in a different guise.
The **inverse map runs backwards** (chemistry → recipe) and maps to **no forward stage** in the registry taxonomy; it is an offline personalization/recipe-optimization layer that would sit *on top of* the whole pipeline. To be meaningful for puckworks it would have to be **retrained on puckworks' own forward chain**, not this paper's angeloni-derived simulator. No adapter turns it into a stage component. Kind is calibration at best; realistically out of scope.

## Extractable data
- **Nothing worth transcribing.** The 1759-sample dataset (plus 6000 augmented, 153 off-grid) is a single text file, but it is **simulator output from the angeloni2023-lineage model already in the registry**, in scaled units, with no experimental content. It adds no independent validation data; the registry's value ceiling is measured data, which this paper has none of.
- The genuine chemistry data for this model family is already captured by the **angeloni2023** card (Tables 2–5, 7: real HPLC assays, 66 shots). Re-deriving simulator outputs would be strictly redundant.
- Availability: no repository or DOI stated; "a single text file" referenced but not linked. Code not published.
- One structural note worth keeping (not data): blend cup-chemistry is ~linear in fraction (Eq. 25) — useful to remember if puckworks ever models blends, but it falls out of any linear-inventory dissolution model.

## Overlaps and conflicts
- **angeloni2023 (duplicates forward physics; adds ML layer):** the forward model *is* angeloni's (same System, same 8 species, same α(T,p)). This paper neither supersedes nor complements it as physics — it wraps it in a surrogate and an inverse. No new stage component, no new data.
- **cameron2020.extraction_bdf / egidi2024 (no competition):** this offers no runtime extraction component; it is a surrogate of a solver, not a mechanistic extraction model. Nothing to swap.
- **Backlog "extraction: multi-class solute chemistry":** already better served by angeloni2023's real assays; this paper's synthetic 8-species outputs do not advance that slot.
- **Backlog "observables: temperature effects":** temperature is a recipe variable and an inverse target here, but only inside the fitted simulator — no independent temperature physics, so no contribution.
- **Inverse/personalization layer:** genuinely novel but has no home in the current forward-stage registry; it is out of scope until (a) puckworks defines an inverse/optimization surface and (b) it is retrained on puckworks' forward chain rather than the angeloni surrogate.

## Implementation estimate
No intake recommended. The forward physics is already carded (angeloni2023) and the surrogate+inverse are an out-of-scope ML layer trained on in-silico data from that same model, with zero experimental validation and no transcribable physical data. If ever pursued as a personalization tool, effort would be **M** (retrain surrogate + inverse on puckworks' own forward pipeline, define an inverse contract) for no current registry benefit. There is no gate to design because there is no independent data to gate against.

VERDICT: skip — the forward physics duplicates angeloni2023 verbatim, and the paper's novel surrogate + inverse map are an out-of-scope personalization layer trained and "validated" entirely on in-silico output from that already-registered model, with no experimental data to transcribe — effort S
