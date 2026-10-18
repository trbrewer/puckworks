# Independently specified synthetic checks (before implementation)

These invented values are independent of the implementation and retained caffeine.

* Upper budget: (v,u,t)=(0.375,0.125,0.5) PASS;
  (0.625,0.125,0.5) unresolved; (0.75,0.125,0.5) FAIL.
  Missing value/allowance is incomplete. FAIL plus incomplete remains FAIL.
* Observed masses [0.001,0.003] kg, q=[0.001,0.001], retained predictions
  [2,0] mg/g: errors [+1,-1], weights [1/4,3/4], R=1, B=-0.5,
  absB=0.5 mg/g. Total allowances [1e-7,3e-7] kg give u_R=u_B=0.1 mg/g.
  A separate coordinate allowance must not be added again. Deliberately use
  retained mass/concentration coordinates that cannot be replaced by original
  interval division. Assayed interval mass RMSE=sqrt(5) mg; MAE=2 mg.
* Two shots with biases +1 and -1 have mean absB=1 and mean B=0.
* Two synthetic conditions with R [1,2,3] and [4,5,6] have balanced R=3.5.
  Deleting shot 1 gives ((2+3)/2+5)/2=3.75, not pooled 4.0.
* Incomplete three-shot condition with two complete R=0.9 and zero allowances
  has full-condition lower R=0.6 => FAIL despite the missing third. Two
  complete R=0.6 give lower R=0.4 => incomplete, never PASS from subset.
* Reference R=1e-12 and u=0 triggers relative FAIL even with candidate zero.
  Definite wins are strict: touching endpoints never definite; possible wins
  include definite wins. Two possible wins cannot satisfy required three.
* Baseline gain 0.02 allowance 0.001; deletions 0.01 +/-0.02 and 0.03 +/-0.001:
  deletion points all positive, deletion lower endpoints not all positive;
  deletion point range [0.01,0.03], all-scenario envelope [-0.01,0.031].
  Positive gain 0.02 still fails a 0.10 original gain requirement.
* [1,2,3] mg/g observations: n=3, mean=2, sample SD=1; support n=2
  remains two even though all three source observations are valid. n=1 SD=null.
* Full cohort fixtures use four primary and two temperature conditions with
  three unique identities each: exactly 12 and six paired whole-shot deletions.
  Every scenario retains all conditions; no arm-specific or fraction deletion.
* Reject duplicate/missing/incompatible identity, unequal arm support, NaN,
  negative allowance, malformed units and hash mismatch. Preserve a single
  unsupported flow slot and all original physical shots in its subset.
* Determinism, exclusive outputs, no writes into Git/source, no historical
  lifecycle imports/calls, no private paths/shot metrics/keyed deletion means
  in the public projection are structural checks.
