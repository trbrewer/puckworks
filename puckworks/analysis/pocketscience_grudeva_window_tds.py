"""Source-only P/N transfer to Grudeva regular windows; private numerical outputs.

Attribution: Pocket Science Coffee (2024), Grudeva thesis/upstream (separate rights).
Vials define endpoints; only whole physical shots are bootstrap replicates.
"""
import time

import numpy as np

from puckworks.analysis import grudeva_clock as clock
from puckworks.analysis import pocketscience_cup_tds as source
from puckworks.analysis import pocketscience_cross_style_tds as pn
from puckworks.analysis import pocketscience_pooled_scaling as pooled

ARMS = ('P', 'N')
SEED = 20261027
THESIS_SHA = 'bbe73a303ab0b6838fe727f05d970438c7ba42576a9959f032aa63b88aff84e6'
MEMBERSHIP = '1b7863192edf7d4f672a71b5409d02004d72fb171da8d2581724427fb924f196'


def source_cohort(shots, reference, expected_membership=MEMBERSHIP):
    if shots != reference:
        raise ValueError('source observations/order drift')
    source.arrays(shots)
    retained = [s for s in shots if not s.source_excluded]
    if (len(shots) != 60 or len(retained) != 57
            or {s.identity for s in shots if s.source_excluded}
            != {('Sworks High Flow', row) for row in (7, 9, 23)}):
        raise ValueError('source observation/membership drift')
    if (len({s.condition for s in retained}) != 12
            or [sum(s.sheet == b for s in retained) for b in ('Sworks High Flow', 'VST18')] != [37, 20]
            or [sum(s.style == s0 for s in retained) for s0 in source.STYLES] != [29, 28]
            or source.membership_hash(retained) != expected_membership):
        raise ValueError('source membership/count/order drift')
    return retained


def nominal_dose(authority):
    if (authority.get('status') != 'QUALIFIED'
            or authority.get('pdf_sha256') != THESIS_SHA
            or authority.get('nominal_dose_kg') != .0185
            or authority.get('individual_doses_measured') is not False
            or not all(authority.get(k) for k in ('authority', 'dose_passage', 'scope_passage'))):
        raise ValueError('authenticated nominal dose authority required')
    return .0185


def aggregate(records, authority, literal_zero=False):
    """Use all sixteen masses; reject a whole endpoint if chemistry is missing."""
    dose = nominal_dose(authority)
    identities = [(r['shot'], r['vial']) for r in records]
    if len(set(identities)) != len(identities) or identities != sorted(identities):
        raise ValueError('rectangular identity/order drift')
    primary = clock.observations(records)
    missing = [(r['shot'], r['vial']) for r in primary if r['solute_g'] is None]
    if missing != [(6, 3), (13, 2)]:
        raise ValueError('primary chemistry exclusion drift')
    observations = clock.observations(records, zero='literal') if literal_zero else primary
    endpoints, excluded = [], []
    for shot in range(1, 14):
        rows = [r for r in observations if r['shot'] == shot]
        if [r['vial'] for r in rows] != list(range(1, 17)):
            raise ValueError('incomplete regular window')
        mass_g = np.array([r['mass_g'] for r in rows], dtype=float)
        if not np.all(np.isfinite(mass_g)) or np.any(mass_g < 0):
            raise ValueError('invalid recorded window mass')
        beverage = float(np.sum(mass_g/1000))
        if not np.isfinite(beverage) or beverage <= 0:
            raise ValueError('nonpositive complete-window beverage mass')
        if any(r['solute_g'] is None for r in rows):
            excluded.append(dict(shot=shot, reason='whole_shot_positive_mass_chemistry_gap',
                                 complete_beverage_kg=beverage))
            continue
        # Explicit structural-zero branch: never compute 0 * missing TDS.
        positive = [r for r in rows if r['mass_g'] > 0]
        solute = float(sum((r['mass_g']/1000)*r['tds_pct']/100 for r in positive))
        y = 100*solute/beverage
        independent = float(sum(r['mass_g']*r['tds_pct'] for r in positive)/mass_g.sum())
        error = abs(y-independent)
        if not np.isfinite(y) or error > 1e-10:
            raise ValueError('independent pooled-window observation check failed')
        endpoints.append(dict(shot=shot, vials=list(range(1, 17)), beverage_kg=beverage,
                              solute_kg=solute, target_pp=y, x=dose/beverage,
                              aggregation_check_pp=error, structural_zero_vials=sum(mass_g == 0).item(),
                              mass_authority='recorded Weight', window_s=[0, 32]))
    expected = list(range(1, 14)) if literal_zero else [j for j in range(1, 14) if j not in (6, 13)]
    if [e['shot'] for e in endpoints] != expected:
        raise ValueError('target membership/complete coverage drift')
    return dict(endpoints=endpoints, excluded=excluded, physical_n=len(endpoints),
                observation='literal_positive_mass_zero' if literal_zero else 'complete_chemistry',
                nominal_dose_kg=dose, terminal_and_extra_block_excluded=True)


def scores(y, predictions, weights=None):
    """Equal physical-shot loss; zero individual target multiplicities are valid."""
    y, p = np.asarray(y, dtype=float), np.asarray(predictions, dtype=float)
    w = np.ones(len(y)) if weights is None else np.asarray(weights, dtype=float)
    if (y.ndim != 1 or not len(y) or p.shape != (len(y), len(ARMS)) or w.shape != y.shape
            or not np.all(np.isfinite(y)) or not np.all(np.isfinite(p))
            or not np.all(np.isfinite(w)) or np.any(w < 0)
            or not np.isfinite(w.sum()) or w.sum() <= 0):
        raise ValueError('invalid target coverage or total scoring weight')
    result = {}
    for j, arm in enumerate(ARMS):
        e = p[:, j]-y
        result[arm] = dict(rmse=float(np.sqrt(np.sum(w*e*e)/w.sum())),
                           mae=float(np.sum(w*abs(e))/w.sum()), bias=float(np.sum(w*e)/w.sum()))
    if not all(np.isfinite(v) for row in result.values() for v in row.values()):
        raise ValueError('nonfinite scoring objective')
    return result


def support(x, endpoints):
    x = pn.predictor(x)
    tx = pn.predictor([e['x'] for e in endpoints])
    lo, hi = float(x.min()), float(x.max())
    return dict(source_range=[lo, hi], target_range=[float(tx.min()), float(tx.max())],
                targets=[dict(shot=e['shot'], x=float(v), extrapolated=bool(v < lo or v > hi))
                         for e, v in zip(endpoints, tx)],
                extrapolation_count=int(np.sum((tx < lo) | (tx > hi))))


def decision(comparison, incomplete=False):
    if incomplete:
        return 'INCOMPLETE_BOOTSTRAP'
    ci = comparison['P/N']['difference_ci95']
    if ci is None:
        return 'INCOMPLETE_BOOTSTRAP'
    if ci[1] < 0:
        return 'P_WINDOW_TRANSFER_ADDED_VALUE_OVER_N'
    if ci[0] > 0:
        return 'N_LOWER_WINDOW_TRANSFER_LOSS'
    return 'WINDOW_TRANSFER_COMPARISON_UNRESOLVED'


def source_fit_predict(x, y, target_x, weights=None):
    fit = pn.fit_source(x, y, weights, oracle=True)
    pred = pn.predict(fit['coefficients'], target_x)
    check = max(pn.oracle_error(fit, x), pn.oracle_error(fit, target_x))
    return fit, pred, check


def evaluate(shots, endpoints, observation='filtered', draws=2000, seed=SEED, deadline=None):
    if not isinstance(draws, int) or draws <= 0:
        raise ValueError('positive requested draw count required')
    x, y, _, groups = source.arrays(shots, observation)
    if not endpoints or len({e['shot'] for e in endpoints}) != len(endpoints):
        raise ValueError('duplicate or absent whole-shot target identities')
    tx, ty = np.array([e['x'] for e in endpoints]), np.array([e['target_pp'] for e in endpoints])
    fit, pred, check = source_fit_predict(x, y, tx)
    metric = scores(ty, pred)
    comparison = pn.contrasts(metric)
    source_seed, target_seed = np.random.SeedSequence(seed).spawn(2)
    srng, trng = np.random.default_rng(source_seed), np.random.default_rng(target_seed)
    samples, failures = [], []
    active, domain_draws = ({a: 0 for a in ARMS} for _ in range(2))
    for draw in range(draws):
        sw = source.bootstrap_weights(groups, srng)
        tw = np.bincount(trng.choice(len(ty), len(ty), replace=True), minlength=len(ty))
        try:
            if deadline is not None and time.monotonic() > deadline:
                raise ValueError('scientific computation budget exhausted')
            f, p, error = source_fit_predict(x, y, tx, sw)
            m = scores(ty, p, tw)
            domain = {a: int(np.sum((p[:, j] < 0) | (p[:, j] > 100))) for j, a in enumerate(ARMS)}
            samples.append(dict(draw=draw, source_multiplicities=sw.tolist(),
                                target_multiplicities=tw.tolist(), fit=f, scores=m,
                                contrasts=pn.contrasts(m), oracle_error_pp=error,
                                out_of_domain_predictions=domain))
            check = max(check, error)
            for a in ARMS:
                active[a] += int(f['active_bounds'][a])
                domain_draws[a] += int(domain[a] > 0)
        except (ValueError, np.linalg.LinAlgError, FloatingPointError) as exc:
            failures.append(dict(draw=draw, source_multiplicities=sw.tolist(),
                                 target_multiplicities=tw.tolist(), reason=str(exc)))
            break
    pooled.summarize_intervals(comparison, samples, failures)
    for quantity in ('difference', 'gain'):
        comparison['P/N'][quantity+'_undefined_draws'] = len(samples)-comparison['P/N'][quantity+'_defined_draws']
    for a in ARMS:
        metric[a]['rmse_ci95'] = (np.percentile([s['scores'][a]['rmse'] for s in samples], [2.5, 97.5]).tolist()
                                  if len(samples) == draws and not failures else None)
    ranges = support(x, endpoints)
    predictions = []
    for i, e in enumerate(endpoints):
        errors = pred[i]-ty[i]
        predictions.append(dict(e, predictions=dict(zip(ARMS, pred[i].tolist())),
                                errors=dict(zip(ARMS, errors.tolist())),
                                extrapolated=ranges['targets'][i]['extrapolated'],
                                adverse_P_vs_N=bool(abs(errors[0]) > abs(errors[1])),
                                out_of_domain={a: bool(pred[i,j] < 0 or pred[i,j] > 100)
                                               for j,a in enumerate(ARMS)}))
    return dict(source_n=len(shots), source_conditions=len(np.unique(groups)), target_n=len(ty),
                source_observation=observation, target_observation='Grudeva recorded TDS',
                source_fit=fit, scores=metric, contrasts=comparison,
                decision=decision(comparison, len(samples) != draws or bool(failures)),
                predictions=predictions, coverage_per_arm=len(ty), support=ranges,
                worst_absolute_errors={a: max(predictions, key=lambda p: abs(p['errors'][a])) for a in ARMS},
                out_of_domain_predictions={a: sum(p['out_of_domain'][a] for p in predictions) for a in ARMS},
                bounded_lsq_max_difference_pp=check,
                bootstrap=dict(requested=draws, completed=len(samples), failed=len(failures),
                               unattempted=draws-len(samples)-len(failures), failures=failures,
                               seed=seed, stream_spawn_keys=[list(source_seed.spawn_key), list(target_seed.spawn_key)],
                               active_bound_draws=active, out_of_domain_draws=domain_draws),
                bootstrap_samples=samples)


def influence(shots, endpoints, primary, deadline=None):
    x, y, _, groups = source.arrays(shots)
    tx, ty = np.array([e['x'] for e in endpoints]), np.array([e['target_pp'] for e in endpoints])
    conditions = sorted({s.condition for s in shots})
    deletions = []
    for side, n in (('source', len(conditions)), ('target', len(endpoints))):
        for i in range(n):
            if deadline is not None and time.monotonic() > deadline:
                raise ValueError('scientific computation budget exhausted')
            keep = groups != i if side == 'source' else np.ones(len(x), dtype=bool)
            held = np.ones(len(tx), dtype=bool) if side == 'source' else np.arange(len(tx)) != i
            if side == 'source':
                f, p, check = source_fit_predict(x[keep], y[keep], tx[held])
            else:
                f = primary['source_fit']
                p = pn.predict(f['coefficients'], tx[held])
                check = pn.oracle_error(f, tx[held])
            m = scores(ty[held], p)
            deletions.append(dict(side=side, deleted=conditions[i] if side == 'source' else endpoints[i]['shot'],
                                  source_n=int(keep.sum()), target_n=int(held.sum()), source_fit=f,
                                  scores=m, contrasts=pn.contrasts(m), oracle_error_pp=check))
    ranges = {}
    for side in ('source', 'target'):
        rows = [d['contrasts']['P/N'] for d in deletions if d['side'] == side]
        ranges[side] = {k: [min(v), max(v)] if len(v) == len(rows) else None
                        for k in ('difference', 'gain')
                        for v in [[r[k] for r in rows if r[k] is not None]]}
        ranges[side].update(sign_reversals=sum(r['difference']*primary['contrasts']['P/N']['difference'] < 0
                                              for r in rows), ties=sum(r['difference'] == 0 for r in rows))
    return dict(deletions=deletions, ranges_not_ci=ranges)
