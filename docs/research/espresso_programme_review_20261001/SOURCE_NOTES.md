# Producer and source locators

These are logical source labels for the evidence map, not accessible raw-file links.
Absolute workstation mappings are retained only in the private publication note.
All identities below concern the completed studies; this documentation stage did
not reopen restricted original observations or repeat scientific computations.

| Map producer | Exact local evidence-directory label |
|---|---|
| audit | local-audit-20260930T165034Z |
| closeout | integration-closeout-20260930T182113Z/package |
| ci | pw-pr304-ci-20260930T201909Z |
| c01 | absolute-benchmark-20261001T004537Z |
| dense | author-runtime-followon-20261001T015434Z/cameron/execution-20261001T124658.426064Z |
| sparse | author-runtime-followon-20261001T015434Z/cameron/sparse-execution-20261001T133411Z |
| balance | author-runtime-followon-20261001T015434Z/cameron/balance-attribution-20261001T144045Z |

The earlier closeout's unchanged ZIP and the later balance ZIP remain external;
they are not repository payloads. The later acceptance scope is owner-reported in
the main report, not an invented independent approval of this new documentation.
Original failed runs and superseded statements remain in the identified originals.

## Literature versions actually inspected by the producers

Cameron et al., *Matter*2,631–648, DOI10.1016/j.matt.2019.12.019:

| Version / SHA-256 | Location used |
|---|---|
| Final publisher + complete SI, 85c8f50a3b8baa5ccdf1253b65df0dd4080776cfa573e056d2acff94d50410e5 |27-page combined file; Fig.5 PDFp13/printed642; Eq.24–26 PDFp9/printed638; SI Eq.3 PDFp22/SIp2; S1/S2 PDFp23/SIp3 |
| Accepted manuscript, 2696a36248f0e066b4626a37c82cd245b6d42002658a69079632e6de13639418 |20 pages, Figure5 p19; [institutional copy](https://pure.port.ac.uk/ws/portalfiles/portal/18602212/Manuscript.pdf) |
| OSTI publisher, 0fa006c50429cab73e8d53840d39d9a058718129cca62d31d9305c29d6b22673 |20 pages; [OSTI copy](https://www.osti.gov/pages/servlets/purl/1973594) |
| Article in press, 422810de752db7e260c07136d0c3070a40806d90162c71d274f143ee771e03be |19 pages; placeholder caption, not the final digitisation authority |

The audit's `cameron/REPORT.md` and original source-hash/pixel records identify
these versions; the papers and rendered crops are omitted. This publication did
not reinspect their images or independently redigitise them.

Pannusch J.FoodEngineering367,111887 (DOI10.1016/j.jfoodeng.2023.111887), reprinted
in the retained thesis SHA-256
`62a79ef16dd675894e59c27dbb2bc67b36f45c2340902c330bc4c7068ac5d339`:
PDFp128=articlep1,p129=p2,p133=p6. Schmieder *Foods*12,2871
(DOI10.3390/foods12152871), published PDF SHA-256
`6ed07972d1ae989f7ffd9f98782178ca42c4b5f7209bfebed1ad89494d4faae3`,
pp3–4 methods. C01 source archive/version and workbook-cell locators are in §E
of the main report. Different article titles or identical thesis copies do not
supply independent experiments. No copied C01 assay/telemetry table is included.

Roman-Corrochano2015 publisher source SHA-256
`fc5a41225359993da86a7ef3504ea6bbdf2be99811f266e20e55e4156d914d5e`:
methods PDFp4/printed108,Table2 PDFp9/printed113,porosity discussion PDFp10/printed114.
Perticarini primary thesis Table4.1 was visually inspected in the native audit at
PDFp99/printed87 and its methods at PDFp98/printed86. The native report identity
is in the evidence map; its external `geometry/source-identities.json` records the
thesis hash. No source table image is redistributed here.

## Code and arithmetic inspection levels

`replay/` retains the qualified sparse adapter, both original N40 templates and
one early-output template, original reducers, source-parameter hashes and author
MIT notice. New `prepare_replay.py` and `reduce_balance.py` only provide explicit
portable paths/fresh destinations; their preparation/static checks are not numerical
qualification or a new solve. The original reducers' arithmetic is unchanged.

`archived_checks/` preserves the original operator/functional check code for
inspection. It expects the original logical layout and omitted full snapshots;
it is **not executable from aggregate records alone**. Its recorded outputs are
included under `balance/`. In particular, all seventeen original-operator checks
are producer evidence, not new Octave calls in this publication.

`check_aggregates.py` and its six adversarial tests are newly written standard-library
publication checks. They do not import an espresso model or the original reducer;
they check identities and arithmetic relationships among the included aggregate
fields. Tampering rejection demonstrates a check contract, not physical validity.
