"""Frozen MASS-007 inputs to observed-boundary decisions; never scores outcomes."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from decimal import Decimal
import math
from pathlib import Path

from . import conditional_tail_stopping as stop
from . import grudeva_pooled_tail_delivery as parent

md = parent.md
ROOT = parent.ROOT
DOC = ROOT / 'docs/analysis/sci_md_mass_stop_decision_001'
TASK = 'SCI-MD-MASS-STOP-DECISION-001'
POLICIES = ('C2', 'C0', 'FIXED')
MODEL_IDS = {
    'C0': 'd486067fc8e8c381860f2473bfe0d14176f0a5abc3f8fed7cd75525923d82d86',
    'C2': '960e0c7dd37d3ba876f95a44c00c69f222e53c022a641e4b092a2af686fb9516',
}
RUNTIME_IDS = {
    'conditional_tail_delivery.py': '4fb20dd42e0ed7d5a758f549d616131988a1dab05ddc49b9253441606f155e33',
    'grudeva_pooled_tail_delivery.py': '75c84e716f66201cc8623b96ba903c20763299b1f2e511f043517e20fc247910',
    'conditional_tail_stopping.py': '6c8d25a062fd8175d8697cc9dd5e04b32840f90dce116a3c708a5f3d4a85f96a',
}
CLAIMS = ('RESEARCH_ONLY', 'TARGET_EXPOSED',
          'RETROSPECTIVE_OFFLINE_ASSAY_CONDITIONED_DECISION_REPLAY',
          'CONDITIONAL_ON_MEASURED_BEVERAGE_MASS', 'OBSERVED_BOUNDARY_ACTIONS_ONLY',
          'NO_REAL_TIME_ASSAY_CLAIM', 'NO_CONTINUOUS_PHYSICAL_STOPPING_CLAIM',
          'PHYSICAL_VALIDATION=NOT_ESTABLISHED')


@dataclass(frozen=True)
class Contract:
    name: str
    solute_min_kg: float
    tds_min_percent: float

    @property
    def nominal_delta_kg(self):
        return Decimal(str(self.solute_min_kg)) / (Decimal(str(self.tds_min_percent)) / 100)


CONTRACTS = (Contract('PRIMARY', .000100, 2.), Contract('S1', .000050, 2.),
             Contract('S2', .000150, 2.), Contract('S3', .000100, 1.5),
             Contract('S4', .000100, 2.5))
read, write, digest = parent.read, parent.write, parent.digest


def verify_models(models):
    if set(models) != set(MODEL_IDS) or any(models[a].sha256 != h for a, h in MODEL_IDS.items()):
        raise ValueError('BLOCKED_FROZEN_MODEL_IDENTITY')


def verify_dependencies():
    models, _, _ = parent.verify_dependencies()
    selected = {a: models[a] for a in MODEL_IDS}
    verify_models(selected)
    for name, h in RUNTIME_IDS.items():
        if digest(ROOT / 'puckworks/analysis' / name) != h:
            raise ValueError('BLOCKED_FROZEN_RUNTIME_IDENTITY')
    return selected


def verify_prior(prior, source_root):
    """Silent source/role QA; future assay values never leave this function."""
    models = verify_dependencies()
    prior = parent.private(prior)
    authority = read(parent.DOC / 'FREEZE.json')
    for name, h in authority['artifacts'].items():
        if digest(prior / name) != h:
            raise ValueError('BLOCKED_ACCEPTED_PRIVATE_EVIDENCE_IDENTITY')
    records = parent.gc.parse_source(parent.verify_source(source_root))
    early, queries, support, cohort, pools = parent.project(records, models['C2'].means[:2])
    for name, value in (('early_inputs.json', early), ('queries.json', queries),
                        ('support.json', support), ('cohort.json', cohort), ('pools.json', pools)):
        if md.canonical(value) != md.canonical(read(prior / name)):
            raise ValueError('BLOCKED_SOURCE_ROLE_RECONSTRUCTION')
    eligible = {r['shot'] for r in cohort if r['eligible']}
    counts = {
        'source_blocks': len({r['shot'] for r in records}),
        'qualified_physical_shots': len(cohort), 'eligible_physical_shots': len(eligible),
        'original_conditioning_assays': sum(p['original_assays'] for r in pools
                                            if r['shot'] in eligible for p in r['pools']),
        'pooled_early_summaries': sum(len(r['pools']) for r in pools if r['shot'] in eligible),
        'positive_suffix_windows': sum(q['mass_kg'] > 0 for q in queries),
        'zero_width_suffix_windows': sum(q['mass_kg'] == 0 for q in queries),
    }
    if tuple(counts.values()) != (14, 13, 11, 98, 22, 55, 0):
        raise ValueError('BLOCKED_COHORT_COUNT_CHECK')
    if any(s['chemistry_status'] != 'AVAILABLE' for s in support):
        raise ValueError('BLOCKED_SOURCE_SUPPORT')
    saved = read(prior / 'states.json')
    states = {a + '/' + str(s): md.State.from_dict(saved[a + '/' + str(s)])
              for a in MODEL_IDS for s in sorted(eligible)}
    inputs = parent.input_index(early)
    for key, state in states.items():
        arm, shot = key.split('/')
        if state.model.sha256 != MODEL_IDS[arm] or state.inputs != inputs[arm, int(shot)]:
            raise ValueError('BLOCKED_SAVED_STATE_IDENTITY')
    return queries, cohort, states, counts


def eligible_boundaries(queries, anchor):
    """Retain only complete recorded positive-mass vials; do not create stops."""
    if not queries or len({q['shot'] for q in queries}) != 1:
        raise ValueError('ONE_COMPLETE_SHOT_REQUIRED')
    for q in queries:
        parent.checked_query(q)
        if any(q[k] is None for k in ('mass_kg', 'start_kg', 'end_kg')):
            raise ValueError('BLOCKED_UNKNOWN_COORDINATE')
    if abs(queries[0]['start_kg'] - anchor) > 4 * math.ulp(anchor):
        raise ValueError('BLOCKED_ANCHOR_CONVENTION')
    for left, right in zip(queries, queries[1:]):
        if left['vial'] + 1 != right['vial'] or left['end_kg'] != right['start_kg']:
            raise ValueError('COMPLETE_CONTIGUOUS_OBSERVED_VIALS_REQUIRED')
    return [(q['vial'], q['end_kg']) for q in queries if q['mass_kg'] > 0]


def boundary_status(result, mass):
    """Membership in the point API's qualified set, never in a root enclosure."""
    md.number(mass)
    if not result.query.stop_min_kg <= mass <= result.query.stop_max_kg:
        raise ValueError('BOUNDARY_OUTSIDE_QUERY')
    for c in result.components:
        for e in (c.lower, c.upper):
            if (e.lower_kg == mass == e.upper_kg and
                    e.qualification in ('EXACT_STRUCTURAL_ROOT', 'QUALIFIED_QUERY_POINT')):
                return 'QUALIFIED'
        if c.interior_min_kg is not None and c.interior_max_kg is not None:
            lo = max(c.interior_min_kg, c.lower.upper_kg)
            hi = min(c.interior_max_kg, c.upper.lower_kg)
            if ((lo < mass or lo == mass and c.lower.qualification == 'QUERY_BOUNDARY') and
                    (mass < hi or mass == hi and c.upper.qualification == 'QUERY_BOUNDARY')):
                return 'QUALIFIED'
    if (any(u.lower_kg <= mass <= u.upper_kg for u in result.unresolved_regions) or
            any(c.lower.lower_kg <= mass <= c.upper.upper_kg for c in result.components)):
        return 'NUMERICALLY_UNRESOLVED'
    return 'EXCLUDED'


def choose_boundary(candidates):
    return next((r for r in candidates if r['status'] == 'QUALIFIED'), None)


def model_decision(state, queries, contract):
    boundaries = eligible_boundaries(queries, state.b_anchor)
    query = stop.StoppingQuery(boundaries[0][1], boundaries[-1][1],
                               solute_min_kg=contract.solute_min_kg,
                               suffix_tds_min_percent=contract.tds_min_percent)
    result = stop.solve_stopping_ranges(state, query)
    candidates = [{'vial': vial, 'mass_kg': mass, 'status': boundary_status(result, mass)}
                  for vial, mass in boundaries]
    chosen = choose_boundary(candidates)
    prediction = None
    if chosen:
        prediction = asdict(state.remaining_solute(chosen['mass_kg']))
        # Same MASS-007 shared-anchor reconciliation and numerical allowance.
        _, _, correction = parent.runtime_coordinates(queries[0], state.b_anchor)
        prediction['allowance_kg'] += correction
        prediction['coordinate_allowance_kg'] = correction
        prediction['solute_margin_kg'] = prediction['solute_kg'] - contract.solute_min_kg
        prediction['tds_margin_pp'] = prediction['tds_percent'] - contract.tds_min_percent
        error = prediction['allowance_kg']
        width = chosen['mass_kg'] - state.b_anchor
        if (not prediction['numerical_qualified'] or error > 1e-9 or
                prediction['solute_margin_kg'] < error or
                prediction['tds_margin_pp'] < 100 * error / width):
            chosen['status'] = 'NUMERICALLY_UNRESOLVED'
            chosen = None  # A consistency failure never triggers an alternative policy.
    status = ('QUALIFIED' if chosen else 'NUMERICALLY_UNRESOLVED'
              if any(c['status'] == 'NUMERICALLY_UNRESOLVED' for c in candidates) else 'ABSTAIN')
    return {'status': status, 'selected_vial': chosen['vial'] if chosen else None,
            'selected_mass_kg': chosen['mass_kg'] if chosen else None,
            'prediction': prediction, 'candidates': candidates,
            'feature_extrapolation': list(state.feature_extrapolation), 'inverse': result.to_dict()}


def fixed_decision(queries, contract):
    anchor = queries[0]['start_kg']
    boundaries = eligible_boundaries(queries, anchor)
    target = Decimal(str(anchor)) + contract.nominal_delta_kg
    selected = next(((v, b) for v, b in boundaries if Decimal(str(b)) >= target), None)
    return {'status': 'QUALIFIED' if selected else 'ABSTAIN',
            'selected_vial': selected[0] if selected else None,
            'selected_mass_kg': selected[1] if selected else None, 'prediction': None,
            'nominal_delta_kg': str(contract.nominal_delta_kg), 'feature_extrapolation': []}


def construct(queries, cohort, states):
    shots = sorted(r['shot'] for r in cohort if r['eligible'])
    decisions = []
    for contract in CONTRACTS:
        for shot in shots:
            qs = [q for q in queries if q['shot'] == shot]
            c = next(c for c in cohort if c['shot'] == shot)
            if [q['vial'] for q in qs] != list(range(c['k2'] + 1, 17)):
                raise ValueError('EXACT_MASS_007_SUFFIX_REQUIRED')
            for policy in POLICIES:
                d = (fixed_decision(qs, contract) if policy == 'FIXED' else
                     model_decision(states[policy + '/' + str(shot)], qs, contract))
                decisions.append({'contract': contract.name, 'policy': policy, 'shot': shot, **d})
    return decisions


def prepare(prior, source_root, out):
    out = parent.private(out, create=True)
    queries, cohort, states, counts = verify_prior(prior, source_root)
    write(out / 'queries.json', queries)
    write(out / 'cohort.json', cohort)
    write(out / 'states.json', {k: s.to_dict() for k, s in states.items()})
    write(out / 'counts.json', counts)
    decisions = construct(queries, cohort, states)
    write(out / 'decisions.json', decisions)
    if any(d['status'] == 'NUMERICALLY_UNRESOLVED' or any(
            c['status'] == 'NUMERICALLY_UNRESOLVED' for c in d.get('candidates', [])) for d in decisions):
        raise ValueError('BLOCKED_NUMERICALLY_UNRESOLVED_OBSERVED_BOUNDARY')
    write(out / 'decision_manifest.json', {
        'task': TASK, 'contracts': [asdict(c) for c in CONTRACTS], 'policies': list(POLICIES),
        'models': MODEL_IDS, 'source_sha256': parent.gc.SOURCE_SHA,
        'parent_freeze_sha256': digest(parent.DOC / 'FREEZE.json'),
        'parent_artifacts': read(parent.DOC / 'FREEZE.json')['artifacts'],
        'files': {n: digest(out / n) for n in
                  ('queries.json', 'cohort.json', 'states.json', 'counts.json', 'decisions.json')},
        'outcome_joins': 0, 'new_fits': 0, 'optimizer_calls': 0,
    })


def freeze(out):
    out = parent.private(out)
    verify_dependencies()
    if parent.git(ROOT, 'status', '--porcelain'):
        raise ValueError('CLEAN_COMMITTED_CANDIDATE_REQUIRED')
    manifest = read(out / 'decision_manifest.json')
    for name, h in manifest['files'].items():
        if digest(out / name) != h:
            raise ValueError('DECISION_ARTIFACT_DRIFT')
    bound = [p.relative_to(ROOT).as_posix() for p in DOC.iterdir() if p.is_file()]
    bound += ['puckworks/analysis/' + n for n in (*RUNTIME_IDS, 'grudeva_clock.py',
              'grudeva_stopping_decision.py', 'grudeva_stopping_decision_scoring.py')]
    bound += ['tests/test_grudeva_stopping_decision.py',
              'docs/analysis/sci_md_mass_delivery_007/FREEZE.json',
              'docs/analysis/sci_md_mass_delivery_007/PARENT_006_HANDOFF.json']
    bound += [f'docs/analysis/sci_md_mass_delivery_006/models/{a}.json' for a in MODEL_IDS]
    write(out / 'freeze.json', {'task': TASK,
        'head': parent.git(ROOT, 'rev-parse', 'HEAD'),
        'tree': parent.git(ROOT, 'rev-parse', 'HEAD^{tree}'),
        'bases': read(DOC / 'BASES.json'),
        'code_and_protocol': {n: digest(ROOT / n) for n in sorted(bound)},
        'artifacts': {n: digest(out / n) for n in (*manifest['files'], 'decision_manifest.json')},
        'primary': 'C2', 'required_shots': 11, 'minimum_decisions': 9,
        'minimum_successes': 9, 'maximum_false_feasible': 1,
        'outcome_joins_allowed': 1, 'claims': list(CLAIMS)})


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('operation', choices=('prepare', 'freeze'))
    cli.add_argument('--out', type=Path, required=True)
    cli.add_argument('--prior', type=Path)
    cli.add_argument('--source-root', type=Path)
    args = cli.parse_args()
    try:
        if args.operation == 'prepare':
            prepare(args.prior, args.source_root, args.out)
        else:
            freeze(args.out)
    except (ValueError, OSError, TypeError, KeyError) as exc:
        cli.error('Preparation blocked; retained private evidence must be inspected: ' +
                  (str(exc) if isinstance(exc, ValueError) else type(exc).__name__))


if __name__ == '__main__':
    main()
