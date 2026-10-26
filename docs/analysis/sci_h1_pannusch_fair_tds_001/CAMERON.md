# Separate Cameron assessment — no new model execution

Current [implementation](../../../puckworks/models/cameron2020/extraction_bdf.py)
defines D_S=6.25e-10 m²/s as **intragrain diffusivity** and
K_RATE=6e-7 m⁷ kg⁻² s⁻¹ as the nonlinear surface-dissolution coefficient.
The radial diffusion flux retains D_S independently of surface exchange.
Changing K_RATE alone is therefore not a complete equilibrium counterfactual.

Retained source inputs include measured Darcy flux and shot time by grind,
20 g dry dose, 40 g beverage, and 5 bar overpressure. Geometry uses basket
radius 29.2 mm, solid fraction .8272 and source density 330 kg/m³. Initial
grain concentration is 118 kg/m³; saturation is 212.4 kg/m³. Spherical areas
are derived after primitive radius/phase-fraction interpolation. The current
default initial soluble inventory is **24.467473% of dry dose** under printed
Eq.25; the separately requested 118/.8272 streamtube inventory is 29.578667%.
Physical EY is 100 × cup solute mass / actual dry dose, never a bed-concentration
percentage or Pannusch fraction TDS.

The [original-file audit](../cameron_local_audit_20260930.md) inspected publisher
main text and complete SI alongside manuscript versions. Its corrected default
homogeneous Fig.5 RMSE is **7.1024 EY percentage points**. Conservation repair
does not repair this source-reproduction discrepancy. Fig.5 bars are SD, with
graphical reading allowance separate. Printed Eq.25 gives 18.715912 mm depth;
the normal bulk-density identity gives 22.625620 mm. Released MATLAB EY scaling
differs by phi_s^-2=1.461433 relative to the printed geometry. Author code at
79ebefb72446eb706084e2392cab64bf0fad93a2 was read, not executed: its radii,
diffusivity, surface coefficient and full dimensionless horizon differ from
paper/Puckworks inputs. The actual Fig.5 generating configuration remains unresolved.
This task reuses that original inspection; it does not claim a new PDF inspection
or MATLAB run.

The supplied **D_S ST≈.83 and K_RATE ST≈0 are user-reported**, not reproduced
here. The original GSA receipt was not recovered by bounded searches of the
configured corpus inventory, tracked PW files/history, EWP analysis metadata,
retained September audit and named existing evidence directories. Prior ranges,
distributions, sampled observable(s), sampling design/budget, seed, estimator and
confidence intervals are **UNKNOWN**. This is not a corpus-exhaustion claim.
A low K_RATE ST would justify fixing it under that declared prior/observable,
not rejecting kinetic mechanisms; high D_S ST does not establish identifiability
or physical validation. GSA describes the model under its priors.

**Cameron's empirical H1 adjudication remains unresolved.** Keep its cup-EY
evidence separate from the Pannusch fraction-TDS losses. The sole selected next
task, if no ready blind candidate emerges, is to recover and qualify the Cameron
Fig.5 source configuration and D_S/GSA baseline (geometry, inventory, physical
EY and original receipt) before its complete diffusion/equilibrium comparison.
No second fitting campaign or author message is initiated here.
