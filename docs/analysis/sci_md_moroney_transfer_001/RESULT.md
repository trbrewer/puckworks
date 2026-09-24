# SCI-MD-MORONEY-TRANSFER-001 — preparation result

**BLOCKED_SOURCE_CONTRACT (figure-object confirmation only).** The analysis-only
conservative solver, initialization interface, two bounded empirical hypotheses,
calibration/prediction/scoring CLI and synthetic tests are implemented. There
has been **zero real-data calibration or target scoring**. The decision on
spatial extraction/storage advantage is NOT_ADJUDICATED.

The specific unresolved source item is access to the original 2015 PDF for
page-233 Figure 11 vector-object and visual inspection, and the analogous check
on the selected Figure 3 panels. The CSV metadata and public paper text do not
supply PDF coordinates. Public PDF endpoints returned 403/400; the configured
Moroney external inventory contains CSVs but no PDF. A local namesake was the
2017 well-mixed paper and was rejected. This is not a claim that experimental
replicates or exact wetting history are necessary to execute the conditional
comparison. Those omissions are handled by the protocol's finite sensitivity
family. Other data families were not reopened or rescanned.

The task-local view proposes 44 canonical deep observations (22 outlet, 22 pot)
and 28 shallow observations (14 outlet, 14 pot), excludes 44 duplicated deep
Fig11 symbols, and holds four proposed legend exclusions pending verification:
Fig11 data rows 7, 33, 45, 71 at (189.87,206.498), (190.06,161.812),
(179.87,201.501), (180.05,156.815), in g and mg/g. Original CSV bytes are
unchanged. No point was removed because of a residual. The manifest MEASURED
label describes extraction of plotted coordinates, not experimental uncertainty.

The implementation conserves mobile-liquid, internal-pore, finite surface-solid
and outlet-solute masses; pre-dissolved kernel mass and initial mobile mass are
allocated within the source inventory. Two explicit conditional volume bases
avoid forcing copied porosity, dry dose and geometry to agree. Initial uniform
and linear profiles are fixed families shared by deep and shallow conditions.
Only alpha, beta and surface/kernel split are material fit parameters. Pot and
outlet predictions share one mass-conserving observer. N_M and N_T share a finite
empirical cumulative model and differ only in the declared width transfer.

Synthetic checks cover observation units, conservation, exact upwind pure
advection, zero transfer/zero initial dissolved solute, closed exchange, finite
empirical inventory/derivative, invalid-state rejection and target-value leakage.
The exploratory three-grid controls conserved total solute to 4.3e-14 relative.
The shallow uniform startup transient required finer meshes before freezing;
its 240-to-480 observed-support outlet difference was 1.1543 mg/g. This
numerical warning is preserved rather than passed off as model failure. The
pre-scoring primary grid is 480/960/1920; final fit-specific numerical
qualification remains unexecuted.

The consequence for EWP is to keep integration **NOT_ADJUDICATED**, while making
the calculation reviewable and executable when this specific figure-object gate
is resolved. No generalized data-exhaustion or new-experiment recommendation
follows. Different eventual scoring outcomes have different development choices
in the frozen protocol. Fitted constants must not be promoted to defaults.

Primary 480/960/1920 controls, evaluated on concentration-free observed support,
have maximum adjacent-grid outlet difference 0.039440 mg/g and delivery difference
0.006842 EY pp; tightened-tolerance differences are <=0.000761 mg/g and
0.000062 EY pp. Conservation residual is <=6.12e-14. These representative
controls do not establish fit-specific numerical qualification. The four controls
used 16 solves / 33,274 RHS evaluations in 13.56 s in the recorded environment.

Independent review accepted the engineering thresholds but initially rejected
the executable freeze. Its bounded pipeline findings were corrected and tested
before any real fitting or scoring. Final independent preparation-review and CI
status are recorded with the linked open PRs. An independent
pre-scoring review must accept the source contract and engineering tolerances
before calibration/prediction/scoring; no author-written independent approval
is provided. No scientific advantage, transfer inadequacy or initialization
limitation has yet been inferred from target residuals.

Production/default/interface/registry/evidence-status/lock changes: **zero**.
Native builds/integrations: **zero**. New experiments, author contact and
successor execution: **zero**. PHYSICAL_VALIDATION remains NOT_ESTABLISHED.
