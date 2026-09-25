# Independent original-PDF source audit

SCI-MD-MORONEY-TRANSFER-001; independent reviewer; 2026-09-24.

The owner-supplied Moroney 2015 PDF has SHA256 `896672a997e585a50d97f988caa66259a9a8ed0067300ea7d19725a13c01c4a8`, 19 pages. I independently rendered and visually inspected printed page 219 (zero-based index 3), printed page 233 (index 17), and the equations/Table 2 on printed page 225 (index 9). I also read original extracted source text for Table 1, source initial conditions, volume definitions and the shallow-bed conditions in section G.3 on printed page 232. The PDF and page renders remain private.

**The source-object blocker is resolved for selected Figure 3 panels a/b and Figure 11 panels a/b.** This source audit alone is not scoring approval; executable approval must bind the final revised scientific freeze.

Figure 11 has blue circular JK 60 g, 2.3 bar, 250 ml/min observations and red square JK 12.5 g, 0.5 bar, 250 ml/min observations. Each selected panel contains 22 deep observations, 14 shallow observations and two legend samples inside a rounded labelled legend box. The four questioned rows are those legend samples. They are excluded by source-object identity, not residuals.

| One-based CSV data row | Panel / series | Drawing index / sequence | PDF center x,y [points, top-left origin] | Reconstructed M [g], c [mg/g] |
| --- | --- | --- | --- | --- |
| 7 | a / blue 60 g | 36 / 99 | 181.83751, 79.17399 | 189.87890, 206.49841 |
| 33 | a / red 12.5 g | 38 / 103 | 181.86175, 94.28152 | 190.05614, 161.81214 |
| 45 | b / blue 60 g | 168 / 251 | 359.50700, 80.86351 | 179.87908, 201.50100 |
| 71 | b / red 12.5 g | 170 / 255 | 359.53050, 95.97110 | 180.05091, 156.81458 |

Drawing indices are zero-based positions in PyMuPDF `get_drawings()` for this exact PDF; sequence numbers are the associated PDF rendering sequence identifiers. Original CSV values agree to coordinate readout rounding. Exact bounding boxes and one-to-one matches are retained in the private `pdf-audit/independent-object-matches.json` receipt.

Figure 3 panels a/b contain exactly 22 blue observation markers each, no legend, and no analogous legend-marker contamination. Some PDF drawing paths hold several circles or squares. I split circle paths into their four-Bezier subpaths and rectangle paths into separate rectangle objects before counting. Counting drawing objects alone would miss valid tail observations. All 44 selected Figure 3 CSV rows and all 76 selected Figure 11 rows match distinct marker subpaths one-to-one. The maximum absolute coordinate disagreement is 0.02953 g / 0.00144 mg/g for Figure 3 and 0.01985 g / 0.00277 mg/g for Figure 11 under the independent major-tick calibration. These tiny matching discrepancies establish transcription/object correspondence, not experimental error bars.

The axis calibration uses labelled major ticks, not the enclosing frame. Figure 3 panel b and both Figure 11 frames extend below zero; treating the bottom frame as zero would corrupt small signed values. The independent PDF coordinates are:

| Page/panel | x at M=0,1000 g [pt] | y at c=0,200 mg/g [pt] |
| --- | --- | --- |
| 219/a | 150.617, 293.282 | 156.020996, 82.543976 |
| 219/b | 333.125, 475.790 | 152.494003, 81.956963 |
| 233/a | 155.871, 292.624 | 148.986984, 81.370972 |
| 233/b | 334.908, 471.661 | 148.986984, 81.370972 |

Figure 3 caption directly confirms mg/g against beverage mass in grams, pot panel a versus outlet panel b, 60 g including approximately 4% moisture, cylinder diameter 59 mm, and JK height 4.05 cm. Figure 11 caption confirms the same observables at different bed masses. Section G.3 confirms 12.5 g / 1.12 cm and 60 g / 4.05 cm at the same 250 ml/min flow, with pressure difference measured in each case. Duplicate deep Figure 11 curves do not create a further fold. No other panel/family acquires new authority through this selected audit.

Original Table 1 confirms rho=965.3 kg/m³, csat=212.4 kg/m³, solid density=1400 kg/m³, diffusivity=2.2e-9 m²/s, JK Sauter sizes 27.35/322.49 micrometers, grain-radius parameter 282 micrometers, cell dimension 30 micrometers and total grain-envelope soluble fraction 0.143435. The source text distinguishes dry porosity 0.56 from post-dissolution porosity, states the source-fit role of alpha/beta and solubility, and conditions cylindrical porosity on observed flow. The selected conservative volume and startup reconciliation therefore remains a declared research interpretation, not a parameter-free reproduction or a measurement of these conditional volumes.

**Original printed-sign inconsistency confirmed.** On page 225 Eq59 prints the internal dissolved-mass term as `-alpha * phi_v^(4/3) * D * 6/(ksv2*l_l) * (ch-cv)`, with the same exchange sign as mobile Eq57. Eq53 carries the analogous inconsistency. Literal use creates or destroys total solute in closed exchange. I accept the explicitly documented conservative interpretation in the implementation: the internal reservoir loses exactly what the mobile reservoir gains, equivalent to `+alpha * ... * (ch-cv)` internally. This is an independently diagnosed printed inconsistency resolved by mass conservation and the existing batch convention, **not an author-confirmed published erratum**. It must remain disclosed in the protocol and source audit.

The source assumes saturated first outflow, pre-dissolved kernel solute, clean inlet at source z=L, and a uniform JK initial mobile concentration; the research finite amplitude/linear family and local startup debit remain deliberate conditional sensitivity choices. This original-source inspection changes source readiness, not the parameter domains, observations, thresholds, fit policy or evidence ceiling. No real-data calibration, prediction or target scoring was performed in this audit.
