# SCI-MD-MATIAS-CAFFEINE-FRACTION-SHAPE-001 — fixed analysis contract

Recorded before numerical assessment, 25 October 2026. Actual implementation
base: `49cf29104ede7b20eae0cf48b71caa56ce1c34a0` (live main; #363 merged).
G1 / NO_GOVERNING_PHYSICS_CHANGE / RESEARCH_ONLY / RETROSPECTIVE /
TARGET_EXPOSED / SOURCE_INTERNAL / NONSCORING.
Public observations are already exposed: no protected holdout, target-blind
selection, preregistration or independent predictive-validation claim.

Fixed cohort: ALL TEN Figure 3 aggregate caffeine means across four extractions,
nominal finite-vial windows [0,5],...,[45,50] mL; displayed endpoints 5,...,50 mL.
Dataset ID `matias2023/fig3_caffeine_fractions`. No cutoffs, deletions, alternate
families or mechanisms. Concentrations in mg/L; SI conversion 1 mg/L = 0.001 kg/m³.
No volume/time/mass mapping; no common dose or 70 mg four-shot normalization.

Numerical identity: arXiv:2304.03161v2 PDF SHA256
`500edb0bf2f76e2f616b4abed291ad2ca8208128a5f78cb3114e59ca85cb417b`;
archive `5e114561670c7253417ea47cd14b6288020bbde9fad57c6eecba16c77943015f`;
`img/experiment.pdf` member
`7757b8cc762f26e60e0c77a1d4a7f4da5e1791f1b3ab2da9526d6b50c98d61c9`.
Fetched identities match. Authenticate TeX inclusion, tick calibration, marker
ordering and rendered article agreement. Source-derived geometry: CC BY 4.0,
attributed to Matias et al.; first-party analysis code retains repository MIT.

Recovery: preserve native PDF decimal tokens as rationals, transforms, all ten
centers, twenty vertical endpoints and ten horizontal segments. Shared linear
volume/log10 concentration calibration from ticks; check remaining ticks. Use
exact serialized geometry for N, plus a conservative enclosure derived from
source-coordinate quantization and calibration consistency, declared in source
notes before assessment. Retain covered/clipped/unsupported feature statuses.
Never infer endpoints by reflection or use the blue model curve. Horizontal
semantics unknown; no boundary uncertainty model. Retain raw log readings as
authority. Graphical enclosures are conservative independent rectangular outer
relaxations of shared calibration, explicitly not independent measurement errors.

Operator: c(V)=A exp(-kV), A>0,k>=0; width w=5 mL. Integrating each finite bin
gives B q^(i-1), q=exp(-kw), B=A(1-q)/(kw); at k=0, B=A,q=1.
With z=log10(cbar/(1 mg/L)), x=i-1, fit alpha+beta*x, beta<=0.
Objective: minimize maximum distance from that line to each declared interval.
N uses point centers; G uses graphical center bands; P_outer uses the lowest
admissible lower endpoint and highest admissible upper endpoint. If valid,
P_inner uses highest lower/lowest upper endpoints. For EVERY endpoint realization,
epsilon_outer <= epsilon_realized <= epsilon_inner; outer zero alone establishes
only relaxation intersection. Inner zero supplies a universally intersecting line.
SE is descriptive displayed-extent sensitivity, not simultaneous confidence.

Calculate exactly using all 45 pairs and FULL 2,025 ordered pair-of-pair terms,
including nonnegativity and beta<=0 bounds. Record every attaining constraint,
exact epsilon, slope/intercept feasible intervals and deterministic midpoint
witness; directly verify all original inequalities and interval distances.
Enclose 10^epsilon and reciprocal by a justified outward calculation, separately
from approximate displays. Retain all nine adjacent log ratios/eight curvatures,
center residuals, nearest permitted readings, interval distances and mg/L diagnostics.
No authorized practical tolerance; no statistical rejection/equivalence claim.

One compact source/mathematical independent-method review in this session,
using another source extraction/check calculation without calling the producer.
Test analytical/synthetic limits, independent LP, exact certificates, coverage,
finite-bin operator and aggregation limitation. Deterministic offline CLI,
JSON/CSV, semilog comparison and source overlay; existing VizSpec conventions.
Update only relevant card/MANIFEST/capability/discovery authorities through their
producers. Preserve Khamitova, prior caffeine predictors and EWP analytical
NO_EXPERIMENTAL_VALIDATION reference. No new lifecycle framework.

Discovery: repository tree/MANIFEST/register contain no Matias fraction intake.
Existing configured external inventory and root are accessible; bounded Matias
name/metadata search initially found historical EWP analytical references, no qualified
Figure 3 intake. Before assessment, a bounded current filename search also found
a byte-identical pinned paper PDF; it is source material, not a numerical intake. This is not an absent/exhausted collection claim. Public primary
source supplies this intake. Initial repository-location search was broader than
needed; subsequent content inspection is confined to named repos/configured root.

Interpretation: aggregate curvature does not reject extraction-specific
exponentials; mixtures can curve, but no rescue mixture is fitted or established.
No inference of diffusion or rejection of the full Matias continuum model.
Actual unequal-volume robustness NOT_ESTABLISHED. Repository gains an empirical
fraction benchmark and quantified one-rate compression cost; practical adequacy
unadjudicated. PHYSICAL_VALIDATION=NOT_ESTABLISHED.

Deliver one OPEN / DRAFT / UNMERGED PR, auto-merge disabled. EWP and lock remain
read-only (remote main f44c33dbb9b4fb80143e360e6f4a90f8ac0aa516;
locked Puckworks fc61c4670ec7bf801e40bb391aab16048b8da26b). Record tested
scientific hashes independently of final documentation/PR head.
