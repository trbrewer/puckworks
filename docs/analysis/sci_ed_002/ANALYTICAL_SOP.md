# Analytical SOP v1.0.0

This commissioning-ready default must be technically confirmed by each candidate laboratory before contracting; instrument settings may live in a controlled annex only after these common requirements pass.

## Sample and moisture

Prepare test sample by the principles of ISO 6668. Grind to pass a laboratory-qualified 500 µm screen without heating, mix, and promptly seal. Determine loss in mass on three independent 5.00 g aliquots by ISO 6673 at 105 ± 1 °C to constant mass (successive change ≤1 mg after an additional hour). Record raw wet/dry masses. The numeric constant-mass criterion is a preregistered design criterion requiring confirmation against the licensed standard before commissioning.

## Total assayable content

For each independent 0.5000 g preparation add 50.00 mL water at 95 ± 2 °C, agitate 20 min, cool quantitatively, make to volume, centrifuge, and filter 0.22 or 0.45 µm after demonstrating no analyte loss. Repeat the extraction of the residue twice and combine quantitatively. HPLC-DAD simultaneously determines caffeine and trigonelline using a polar-compatible C18 method qualified in roasted Arabica and Robusta. ISO 20481 is the caffeine reference-method anchor; the simultaneous trigonelline lane must be validated under ISO/IEC 17025 principles before use. This three-cycle result is `T_total`, conditional on spike recovery and residue-challenge qualification; a single extraction is never presumed total.

## Operational reference extractability

On a separate adjacent randomized 0.5000 g aliquot, sequentially extract with 50.00 mL 95 ± 2 °C reagent water for 10.0 min under fixed orbital agitation, separate quantitatively, and assay every fraction separately. For analyte `a` and step `k`, `r[a,k]=blank_corrected_mass[a,k]/cumulative_blank_corrected_mass[a,1:k]`. An analyte stops after two consecutive steps with `r < 0.010`, provided each fraction is below the run-specific LOQ contribution of 0.005 of cumulative recovery. Continue to at most eight cycles. If either condition is censored, it does not qualify. Caffeine and trigonelline may stop independently, but all collected fractions are retained. Failure to stop by cycle eight is `MAXIMUM_REACHED_NOT_QUALIFIED`, not an estimate of completeness.

The 1%/two-consecutive rule is a preregistered operational definition, not a claim of absolute extraction. Its rationale is to require residual increments below the method's demonstrated 90–107% recovery-scale uncertainty while guarding against one anomalously low fraction; it must be confirmed in the pre-commissioning method-performance study. Public literature supports repeated/hot-water extraction and simultaneous HPLC measurement, but does not establish a universal metaphysical endpoint.

## Chromatography and QC

Use traceable neat caffeine and trigonelline certified reference materials; no internal standard by default. Use at least six non-zero calibration levels bracketing samples, weighted only when residual diagnostics preregister it. Acceptance: back-calculated calibrators 95–105% (lowest level 90–110%); reagent blank < LOQ and <0.1% of batch sample signal; matrix-spike recovery 90–107%; preparation RSD ≤5%; duplicate injections differ ≤2%; continuing calibration 95–105%; carry-over blank <20% of LOQ response. A failed control rejects the affected analyte batch; investigate, repeat preparation under the frozen rerun rule, retain both records, and never convenience-delete. Quantify only within range; report below-LOD, detected-below-LOQ, and quantified distinctly.

Randomize samples within balanced batches containing blank, calibration, continuing check every ten injections, matrix spike per species/roast coverage block, duplicate preparation, and carry-over blank after the highest standard/sample. Stability must demonstrate 95–105% retained response over the maximum frozen storage interval. Archive raw chromatograms, sequences, integrations, calibration fits/residuals, preparation records, audit trails, and native files.

## Reduction and uncertainty

For moisture fraction `w=(m_wet-m_dry)/m_wet`, convert `x_dry=x_as_received/(1-w)`. Do not convert absent or incompatible moisture. Propagate mass, volume, moisture, preparation, recovery, calibration, batch, laboratory, and covariance inputs. `f_ref=I_ref/T_total` uses a joint covariance estimate from paired or adjacent aliquots, is never clipped, and triggers discrepancy investigation when `I_ref-T_total` exceeds their combined expanded uncertainty. Neither estimand is redefined.
