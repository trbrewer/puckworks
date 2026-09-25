# Independent source review — SCI-MD-MO-TRANSFER-001

Reviewer: independent scientific-review agent, separate from the implementing
agent. Date: 2026-09-24. This is a source qualification finding, not approval of
an unexamined implementation or a completed scoring result.

The review follows SCI-GOV-001 G1: freeze the operator before parameter fitting;
do not choose a mapping using response agreement. The owner authorization permits
implementation and synthetic verification after a source stop, but not scoring
through an unresolved operator. Physical validation remains not established.

## Evidence actually inspected

- Puckworks base commit `3ed109d60ffcaaca502345ab56e19b116198934e`, tree
  `3e71edf861c3b9ec13504319000b0aab1251ae05`; its Mo card, data guide, MANIFEST,
  and the two canonical CSVs.
- Author-uploaded article manuscript for DOI
  `10.1016/j.jfoodeng.2023.111843`, SHA256
  `9e3f99a97530ec4b0936b8295f5b3e4485614dcbd25ef3f3c2dbbae0c8afdd82`:
  relevant methodology, results, Appendix A.2, table and figure captions;
  rendered equation 37 and Figure 7/8 pages inspected directly. Printed page
  numbers below refer to manuscript pagination, not PDF indices. The inconsistent
  printed denominator “of 24” does not change the page references.
- The article's apparatus reference,
  [EP3713462B1](https://patents.google.com/patent/EP3713462B1/en), especially
  the exit pipe 11b and dispensing valve 15 description. This is a bounded
  source-family follow-up, not a new corpus survey.

No raw replicate records or campaign-specific controller trace were inspected.
This review makes no assertion that such records do not exist. It did not access
protected observations, contact authors, fit responses, or execute native code.

Canonical granulometry SHA256:
`781299488ad480fd121bcea7a9c592c2a7f12af539f3df9b7fd61e9fd45d6521`.
Canonical yield/strength SHA256:
`4413a5c7bdfd42b1e86f7770c682e04848e7e861c3e318dba4cfe97ad36633d3`.

## Qualified facts

| Fact | Source authority and limit |
|---|---|
| Approximately 15 g basket; 29 mm radius, 13.5 mm height | Section 2.7, p11. Approximately 7.5 g is separately named for a single shot. |
| Whole-basket superficial conversion | Section 2.7: 2/3/4 mL/s become 0.757/1.135/1.514 mm/s using the stated basket area. |
| Controlled quantity is dispensing flow leaving the extraction chamber | Section 2.7, p11. It is not a documented constant inlet flow during dry filling. |
| Temperature | Heater setting 98 C; chamber inlet intended to lie within 90 +/- 5 C. No shot-resolved isothermal temperature measurement is supplied. |
| Density and porosity conventions | Section 2.6, pp10–11: nominal bed porosity 0.17 from another study; particle porosity 0.4 and particle envelope density about 0.6 g/mL derive from literature/assumed intrinsic density. These are not independently measured for these shots. Beverage mass/volume conversion neglects density correction. |
| PSD | Section 2.5 and Table 1, pp9/22: volume fractions; split at 100 micrometres diameter; table columns are twice the representative radii. Divide tabulated sizes by two and convert micrometres to metres. |
| Exchange convention | Equation 16 and pp5–6: liquid concentration equals K times particle concentration at equilibrium; external exchange permits extraction only, with no re-adsorption. |
| Cumulative readout | Equation 38, p12, integrates delivered solute and liquid. It is cup-average strength, not instantaneous effluent strength. |
| Sampling and variability | Section 2.7 restarts a brew for each cup mass. Captions of Figures 6–9, pp26–28, identify bars as SD from three independent brews. They do not supply covariance, replicate values or a precise averaging operator. |

The CSV has 51 rows: six each in eight powder/flow conditions and three in E/4,
whose CSV support ends at 20 g. H has PSD only. Simulation curves and K/flow-decay
sweeps are not measured targets. Figure 7 visibly includes green E/4 markers at
larger mass than the retained CSV support; any added points would require a
separate traceable digitization, never silent extension or interpolation of the
51-row table. Zero digitized errors are not evidence of zero uncertainty.

## Material unresolved mapping

1. **Cup delivery and clock.** Two-shot capacity plus a single-shot dose supports
   considering half-basket collection, but does not establish the actual split
   fraction, whether plotted mass is one cup or combined output, or any normalized
   single-shot equivalent. Whole-basket Q is independently supported. Consequently
   the cup-mass-to-elapsed-extraction-time conversion differs among live
   interpretations. The apparatus patent describes a valve capable of retaining
   water before dispensing; it does not identify the protocol used for these
   observations. Section 2.4 and Figure 5 describe the model's filling front,
   not an experimental inlet history or measured downstream hold-up.
2. **EY denominator.** Equation 37 on the original rendered p12 explicitly uses
   initial soluble concentration times particle volume in its denominator.
   Section 2.6 identifies that concentration as soluble inventory; section 2.7
   invokes initial coffee-bed mass to calculate experimental yield. The source
   therefore does not unambiguously identify a common dry-dose observer for
   experimental points and model lines. A strength × mass / 7.5 g audit may expose
   consistency or mismatch, but cannot repair authority by selecting the
   denominator with best response agreement. Independently averaged summaries
   also need not satisfy a product identity exactly.
3. **Powder sharing.** Section 2.5 names Espresso, Refilly Moka and PillowPack as
   distinct commercial powder types. It does not identify them as one material
   ground into three preparations or establish common accessible inventory.
   The general statement of a measured soluble fraction does not document a
   per-product or common-material inventory measurement for these shots.

Bounded alternatives considered are pooled delivery with 15 g dry dose;
single-cup delivery with 7.5 g allocated dose and a separately specified split;
and an inventory-normalized interpretation of the printed yield equation.
Likewise, source-model dry filling and prefilled/delayed dispensing are distinct
startup alternatives. None may be selected by kinetic fits. No source-supported
finite uncertainty interval supplied here settles these alternatives.

## Independent disposition

**Flow-transfer: BLOCKED_SOURCE_CONTRACT.** The preauthorized per-powder inventory
alternative removes the need for common material, but cannot fix delivery,
startup or yield-operator ambiguity. Missing authority is the campaign-specific
cup/flow mapping, startup/storage/readout protocol, and experimental EY
denominator/summary definition.

**Powder-transfer: BLOCKED_SOURCE_CONTRACT.** The same observer gaps apply, with
the additional absence of common-material/shared-inventory authority.

This is not evidence that Mo's data are unusable or that PSD/diffusion fails.
Retain all source-supported descriptive information and historical evidence.
Implementing a conservative analysis kernel and testing its mathematics is
permitted; response optimization, out-of-fit scores and a kinetic winner are
not qualified by the inspected source material. An exact implementation review
must still examine conservation, baseline fairness, fold isolation and decision
arithmetic before any future source-qualified scoring execution.
