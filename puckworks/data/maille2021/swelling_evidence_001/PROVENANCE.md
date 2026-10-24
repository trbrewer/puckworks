# Maille 2021 swelling observations: bounded graphical intake

Maille, M.J., Sala, K., Scott, D.M., Zukswert, H. (2021), *Critical examination
of particle swelling during wetting of ground coffee*, Journal of Food Engineering
295,110420. DOI [10.1016/j.jfoodeng.2020.110420](https://doi.org/10.1016/j.jfoodeng.2020.110420).
The numerical reading source is Sala, Maille, Scott and Zukswert's official
[ASIC2021 poster S8-PO-01](https://www.alphavisa.com/asic/2021/documents/eposters-presentation/S8-PO-01_KYLE.pdf),
Figure4 left, not the inaccessible journal figure. It explicitly cites this article.

The poster SHA256 is
`75740726613515012a2a5ccf593b799add001dbcdbca195f21bc5b01eb438b73`.
The supporting [White Rose thesis](https://etheses.whiterose.ac.uk/id/eprint/36281/)
redacted V1 PDF has SHA256
`840c22d792fe32662bdf4c9f77f75fda41f3b3fc5b05b26293913af88f6fb0ea`.
Both retrieved files match the reviewed fingerprints. No version substitution.
`sources.json` records access, exact public locators, attribution and lineage;
`holdings_checked.json` records portable file identities and inspection limits.

Figure4 is a710×268 embedded raster, PDFpage1/xref36. `coordinates.csv` retains
native integer marker-centre readings with stable experiment/observation/series/
depiction IDs. `contract.json` fixes axes, units, reading allowances and conditional
interpretation. `features.csv` keeps the separate right-panel isolated markers,
overlap cluster, non-observation lines and missing dry reference visible. It is
not raw data. No times are snapped to an invented schedule. All24 left-panel
markers are retained. Right-panel repeated depictions are not pooled or counted
as independent measurements. `intake_freeze.json` binds the plan and readings
before derived comparisons and preserves any later corrections.

The ±4pixel marker and ±1pixel shared-axis allowances describe graphical reading
only. They are neither experimental uncertainty nor calibrated detection limits.
The source does not supply the experiment-specific optical inversion, concentration
calibration, replicate covariance or a dry baseline for Figure4. Laboratory-level
physical inference therefore remains conditional/unidentified even when the
restricted graphical representation is excluded.

## Rights and reproduction

No open reuse licence was stated in the inspected poster. Retained numeric facts,
coordinates and independently calculated tables carry full attribution; no source
PDF, source artwork, cropped image or private original is redistributed. They are
not relabelled as MIT-licensed source data. Repository-authored analysis software
retains the repository software licence. The thesis record specifies CC BY-NC-ND4.0;
the reproduced2021 artwork may retain separate original rights and is external.
This intake grants no new permission to distribute or adapt source artwork.

The2021 journal, poster and reproduced thesis frames are one study lineage.
Distinct depicted experiments have no authenticated replicate join. Maille2024
extraction CSVs and SCI-MD-MAILLE-TRANSFER-001 retain their original identity and
selected-maximum normalization limitation. New documents are not new experiments.

Offline derived reproduction:

```sh
python -m puckworks.analysis.maille2021_swelling_evidence --output /tmp/maille-replay --plot
python docs/analysis/sci_md_maille_swelling_evidence_001/review_check.py --output /tmp/maille-replay
```

Optional source reinspection requires the external PDFs and PyMuPDF: extract
poster xref36 to obtain the native Figure4 raster; xref30 contains Figure1.
Thesis PDFpage53/xref182 contains Figure2.5 (891×514). Its extracted JPEG hash is
`abf945929205b75e779ca4d16f874583d0b5e8dd1974943a15c7ede5c44ec4e4`.
These image identities authenticate which artwork was read; hashes alone do not
verify transcription. The independent review reopens the artwork.
