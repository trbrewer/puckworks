# Grudeva EJAM reference fixtures

Grudeva, Y., Moroney, K. M., and Foster, J. M., *A multiscale model for espresso
brewing: Asymptotic analysis and numerical simulation*, EJAM 37(2), 496–519,
2026 (online 27 May 2025), DOI https://doi.org/10.1017/S095679252500018X.
Article and derived figure coordinates: **CC-BY-4.0**,
https://creativecommons.org/licenses/by/4.0/ . Changes: raster curves were
converted to selected numerical coordinates with explicit pixel uncertainties.
Authors do not endorse this implementation.

`publication_reference.json`: PDF embedded Figure 3 JPEG (1033x712) and Figure 4
PNG (900x640), extracted with PyMuPDF. The fixture records image/source hashes,
linear-axis pixel anchors, grayscale isolation method, selected columns,
centerline coordinates, curve identities and uncertainty. Figure 3 selected
unoccluded gray sections only; overlap and sharp jumps are excluded from smooth
comparison. Event-location error is separate. A digitized Figure 5 error curve
is deliberately not used as a test of the implementation; full spatial arrays,
exact full-model settings and author grid are unqualified.

`analytic_reference.json`: independent Python scalar `math.exp`/`math.fsum`
evaluation of 10000-term spherical Dirichlet analytic series, plus direct
constant-boundary front arithmetic. It never calls production code or the old
port. Initial singular flux is null, not a finite fabricated sample. Equations
are attributed to the article; numerical evaluations are original verification
fixtures, not measured espresso data.

Full article/supplement PDFs, private correspondence, upstream code, source
workbooks and large runs are not distributed here. The separate existing
upstream permission remains unchanged. See the task CONTRACT.md for derivation,
parameter mismatch, source access and reference-qualification limits.
