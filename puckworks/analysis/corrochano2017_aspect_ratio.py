"""Four exposed steady-permeability means and fixed consolidation scenarios.

Research-only representative-state arithmetic; no fit or physical validation.
Source reading bounds use exact rational arithmetic with a shared axis zero.
"""
from __future__ import annotations

import argparse
import csv
from fractions import Fraction
import hashlib
import itertools
import json
import math
from pathlib import Path

from .sci_val_tamped_k_001 import positive, porosity

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/romancorrochano2017/fig6_9_aspect_ratio'
OUTPUT = ROOT / 'docs/analysis/sci_md_corrochano_aspect_ratio_consolidation_001'
ALIASES = {'Psi_B': 'A', 'Psi_C': 'B', 'Psi_D': 'C', 'Psi_E': 'D'}
UNITS = {'coordinates': 'pt', 'permeability': 'm^2', 'density': 'kg/m^3',
         'length': 'm', 'area': 'm^2', 'S_geom': 'm', 'C_geom': 'm^3',
         'G': 'm^3/(Pa*s)', 'R_hyd': 'Pa*s/m^3'}


def exact(x):
    return Fraction(str(x))


def endpoints(center, guard):
    c, g = exact(center), exact(guard)
    if g < 0:
        raise ValueError('negative reading guard')
    return c-g, c+g


def initial_porosity(rho_bulk, rho_solid, particle_porosity):
    for x in (rho_bulk, rho_solid):
        positive(x)
    porosity(particle_porosity)
    value = 1-exact(rho_bulk)/(exact(rho_solid)*(1-exact(particle_porosity)))
    porosity(float(value))
    return value


def consolidated_porosity(epsilon0, lam):
    e, l = exact(epsilon0), exact(lam)
    if not 0 < e < 1 or not 0 <= l < e:
        raise ValueError('require 0 < epsilon0 < 1 and 0 <= lambda < epsilon0')
    return (e-l)/(1-l)


def kc_factor(epsilon):
    e = exact(epsilon)
    if not 0 < e < 1:
        raise ValueError('porosity outside physical domain')
    return e**3/(1-e)**2


def kc_ratio(epsilon0, lambda_2, lambda_6):
    return (kc_factor(consolidated_porosity(epsilon0, lambda_6)) /
            kc_factor(consolidated_porosity(epsilon0, lambda_2)))


def ordinate(y, zero, top, multiplier):
    y, z, t, m = map(exact, (y, zero, top, multiplier))
    if not z > t or m <= 0:
        raise ValueError('invalid axis calibration')
    return m*(z-y)/(z-t)


def reading(y, guard, cal):
    central = ordinate(y, cal['zero_y_pt'], cal['top_y_pt'], cal['published_multiplier_m2'])
    corners = [ordinate(v, z, t, cal['published_multiplier_m2'])
               for v, z, t in itertools.product(
                   endpoints(y, guard), endpoints(cal['zero_y_pt'], cal['anchor_guard_pt']),
                   endpoints(cal['top_y_pt'], cal['anchor_guard_pt']))]
    return {'central': central, 'bounds': [min(corners), max(corners)],
            'exact_bounds': [str(min(corners)), str(max(corners))]}


def shared_axis_ratio(y_numerator, y_denominator, guard, zero, zero_guard):
    """Exact extrema over one common zero and two ordinate intervals.

    For positive heights, monotonicity in each reading and the linear-fractional
    dependence on zero imply extrema at corners. Top/scale cancels identically.
    """
    zs = endpoints(zero, zero_guard)
    ns, ds = endpoints(y_numerator, guard), endpoints(y_denominator, guard)
    if min(zs) <= max(*ns, *ds):
        raise ValueError('ratio needs strictly positive bar heights')
    values = [(z-n)/(z-d) for z, n, d in itertools.product(zs, ns, ds)]
    z, n, d = map(exact, (zero, y_numerator, y_denominator))
    return {'central': (z-n)/(z-d), 'bounds': [min(values), max(values)],
            'exact_bounds': [str(min(values)), str(max(values))],
            'bound_semantics': 'JOINT_SHARED_AXIS_READING_BOUNDS_ONLY'}


def geometry(representation, contract, lambda_2, lambda_6):
    lengths, areas = {}, {}
    for chamber, alpha in [('2:1', 2), ('6:1', 6)]:
        if representation == 'equal_initial_volume':
            volume = positive(contract['condition']['initial_volume_m3'])
            length = (4*volume/(math.pi*alpha**2))**(1/3)
            diameter = alpha*length
        elif representation == 'printed_dimensions':
            dim = contract['printed_dimensions_m'][chamber]
            length, diameter = positive(dim['initial_length']), positive(dim['diameter'])
        else:
            raise ValueError('unknown deterministic geometry representation')
        lengths[chamber] = length
        areas[chamber] = math.pi*diameter**2/4
    for lam in (lambda_2, lambda_6):
        if not 0 <= lam < 1:
            raise ValueError('invalid length reduction')
    h0 = areas['6:1']*lengths['2:1']/(areas['2:1']*lengths['6:1'])
    adjustment = (1-exact(lambda_2))/(1-exact(lambda_6))
    current = {ch: lengths[ch]*(1-float(lam))
               for ch, lam in [('2:1', lambda_2), ('6:1', lambda_6)]}
    return dict(representation=representation, initial_length_m=lengths,
                area_m2=areas, consolidated_length_m=current,
                S_geom_m={ch: areas[ch]/current[ch] for ch in areas},
                H0=h0, bed_length_adjustment=adjustment, H=h0*float(adjustment))


def inferred_permeability(slope_qp, mu, length, area):
    return positive(mu)*positive(length)*positive(slope_qp)/positive(area)


def conductance(kappa, mu, length, area):
    return positive(kappa)*positive(area)/(positive(mu)*positive(length))


def csv_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(line for line in stream if not line.startswith('#')))


def analyze(data=DATA):
    contract = json.loads((data/'contract.json').read_text())
    if contract['schema_version'] != 1 or contract['units'] != UNITS:
        raise ValueError('unsupported contract or non-SI permeability')
    cal = contract['calibration']
    original = csv_rows(data/'source_coordinates.csv')
    coverage = {(r['grind'], r['chamber']) for r in original}
    if coverage != set(itertools.product(('Psi_B', 'Psi_E'), ('2:1', '6:1'))) or len(original) != 4:
        raise ValueError('require exactly four distinct conditions')
    observations = []
    for row in original:
        if ALIASES[row['grind']] != row['journal_grind']:
            raise ValueError('incorrect source alias')
        record = {k: row[k] for k in ('condition', 'grind', 'journal_grind', 'chamber')}
        for key, column, guard in [('mean', 'mean_y_pt', 'mean_guard_pt'),
                                   ('lower_endpoint', 'lower_endpoint_y_pt', 'endpoint_guard_pt'),
                                   ('upper_endpoint', 'upper_endpoint_y_pt', 'endpoint_guard_pt')]:
            record[key] = reading(row[column], cal[guard], cal)
        if not record['lower_endpoint']['central'] < record['mean']['central'] < record['upper_endpoint']['central']:
            raise ValueError('endpoint ordering')
        record['unit'] = 'm^2'
        record['displayed_minus'] = record['mean']['central']-record['lower_endpoint']['central']
        record['displayed_plus'] = record['upper_endpoint']['central']-record['mean']['central']
        observations.append(record)
    ratios = {}
    for grind in ('Psi_B', 'Psi_E'):
        r2, r6 = [next(r for r in original if r['grind'] == grind and r['chamber'] == ch)
                  for ch in ('2:1', '6:1')]
        ratio = shared_axis_ratio(r6['mean_y_pt'], r2['mean_y_pt'], cal['mean_guard_pt'],
                                  cal['zero_y_pt'], cal['anchor_guard_pt'])
        b2, b6 = [next(r for r in observations if r['grind'] == grind and r['chamber'] == ch)['mean']['bounds']
                  for ch in ('2:1', '6:1')]
        ratio['marginal_outer_bounds'] = [b6[0]/b2[1], b6[1]/b2[0]]
        ratio['marginal_outer_semantics'] = 'CONSERVATIVE_RELAXATION_NOT_ALL_COMBINATIONS_JOINTLY_ADMISSIBLE'
        ratios[grind] = ratio
    material_path = ROOT/contract['registered_material_input']
    material = json.loads(material_path.read_text())['initial_packing']
    scenarios = []
    for declared in contract['scenarios']:
        scenario = dict(declared)
        l2, l6 = scenario['lambda_2'], scenario['lambda_6']
        if scenario['particle_porosity_route'] == 'any_common_admissible_symbolic':
            if l2 != 0 or l6 != 0:
                raise ValueError('symbolic coarse scenario requires zero/zero')
            e0 = e2 = e6 = None
            prediction = Fraction(1)
        else:
            ep = (material['particle_porosity'] if scenario['particle_porosity_route'] == 'registered_adopted_average'
                  else scenario['particle_porosity'])
            scenario['particle_porosity'] = ep
            e0 = initial_porosity(contract['condition']['bulk_density_kg_m3'], material['solid_density_kgm3'], ep)
            e2, e6 = consolidated_porosity(e0, l2), consolidated_porosity(e0, l6)
            prediction = kc_ratio(e0, l2, l6)
        ratio = ratios[scenario['grind']]
        residual = {'central': ratio['central']/prediction,
                    'bounds': [b/prediction for b in ratio['bounds']]}
        residual['exact_bounds'] = [str(b) for b in residual['bounds']]
        residual['unity_in_reading_bounds'] = residual['bounds'][0] <= 1 <= residual['bounds'][1]
        scenario.update(epsilon0=e0, epsilon_2=e2, epsilon_6=e6, R_KC=prediction,
                        R_kappa=ratio, F_required=residual,
                        disposition='NOT_EXCLUDED_BY_READING_BOUNDS' if residual['unity_in_reading_bounds'] else 'NOMINAL_READING_MISMATCH',
                        physical_disposition='UNRESOLVED_UNQUANTIFIED_MEASUREMENT_AND_COHORT_JOINS')
        scenario['geometry'] = []
        for rep in ('equal_initial_volume', 'printed_dimensions'):
            geom = geometry(rep, contract, l2, l6)
            geom['viscosity_ratio_mu2_mu6'] = 1
            geom['viscosity_status'] = 'EXPLICIT_COMMON_VISCOSITY_SCENARIO'
            geom['observer_status'] = 'CONDITIONAL_VALID_DARCY_PRESSURE_AND_THROUGH_BED_FLOW_MAPPING'
            geom['G6_over_G2_equals_Rhyd2_over_Rhyd6'] = {
                'central': float(ratio['central'])*geom['H'],
                'bounds': [float(b)*geom['H'] for b in ratio['bounds']]}
            geom['C_geom_m3'] = {ch: float(next(r for r in observations if r['grind'] == scenario['grind'] and r['chamber'] == ch)['mean']['central'])*geom['S_geom_m'][ch]
                                  for ch in ('2:1', '6:1')}
            geom['aggregation'] = 'REPRESENTATIVE_STATE_NOT_MEAN_OF_BED_CONDUCTANCES'
            scenario['geometry'].append(geom)
        scenarios.append(scenario)
    h0 = 3**(4/3)
    checks = {'printed_10_6': {'epsilon0_0_23_reconstruction': kc_ratio(exact('0.23'), '0.13', 0),
                             'author_intermediate_input': 'UNAUTHENTICATED',
                             'registered_epsilon0_rounded_two_decimals': round(float(scenarios[0]['epsilon0']), 2)},
              'fine_prose_ratio': {'printed_approximation': 3, 'figure_ratio': ratios['Psi_B'],
                                   'status': 'LOOSE_PROSE_APPROXIMATION_NOT_REPLACEMENT_OBSERVATION'},
              'full_chamber_pressure_ratios': []}
    for grind, printed in [('Psi_B', 10.37), ('Psi_E', 4.06)]:
        b = [float(x)*h0 for x in ratios[grind]['bounds']]
        checks['full_chamber_pressure_ratios'].append({
            'grind': grind, 'printed': printed, 'printed_rounding_interval': [printed-.005, printed+.005],
            'reconstructed': float(ratios[grind]['central'])*h0, 'reading_bounds': b,
            'rounding_interval_overlaps_reading_bounds': b[0] <= printed+.005 and b[1] >= printed-.005,
            'implied_permeability_ratio': printed/h0,
            'status': 'DERIVED_SOURCE_ARITHMETIC_NOT_PRESSURE_OBSERVATION',
            'length_qualification': 'FULL_CHAMBER_VS_CONSOLIDATED_LENGTH_JOIN_UNRESOLVED' if grind == 'Psi_B' else 'NOMINAL_ZERO_CONSOLIDATION'})
    tick_checks = [{'mantissa': m, 'recovered': reading(y, cal['anchor_guard_pt'], cal),
                    'nominal_axis_residual_pt': y-(cal['zero_y_pt']-m*(cal['zero_y_pt']-cal['top_y_pt']))}
                   for m, y in zip(cal['tick_mantissas'], cal['tick_y_pt'])]
    paths = [data/name for name in ('contract.json', 'source_coordinates.csv', 'source_paths.json')]
    paths += [material_path, Path(__file__)]
    return dict(task=contract['task'], classifications=['G1', 'NO_GOVERNING_PHYSICS_CHANGE',
                'RESEARCH_ONLY', 'RETROSPECTIVE', 'TARGET_EXPOSED', 'SOURCE_INTERNAL'],
                status=contract['status'], units=contract['units'],
                input_sha256={str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else p.name:
                              hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
                coverage={'intended_means': 4, 'recovered_means': 4, 'recovered_error_endpoints': 8,
                          'paired_bed_ratios': 0, 'new_independent_campaigns': 0},
                observations=observations, ratios=ratios, scenarios=scenarios,
                source_arithmetic=checks, tick_checks=tick_checks)


def serial(value):
    if isinstance(value, Fraction):
        return float(value)
    raise TypeError(type(value).__name__)


def plot(result, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec = VizSpec(id='corrochano_fig6_9_reconstruction', title='Four steady-permeability means',
                   class_=1, producer=Producer(module='puckworks.analysis.corrochano2017_aspect_ratio', function='analyze', result_map={'observations': 'observations'}),
                   badge='OBSERVED', evidence_strength='reference', components=[],
                   fidelity_ceiling='Source-internal published means and displayed variability; graphic reading bounds only. Physical validation not established.',
                   render_fn='puckworks.analysis.corrochano2017_aspect_ratio:plot',
                   caption='Points reconstruct means; blue caps reconstruct displayed variability; orange segments are mean reading bounds.',
                   outputs=['reconstruction.svg'], used_in=result['task'])
    if spec.validate():
        raise ValueError(spec.validate())
    with matplotlib.rc_context({'svg.hashsalt': 'corrochano6-9', 'font.size': 10}):
        fig, ax = plt.subplots(figsize=(8, 5))
        for i, r in enumerate(result['observations']):
            values = [float(r[k]['central'])*1e14 for k in ('lower_endpoint', 'mean', 'upper_endpoint')]
            ax.errorbar(i, values[1], yerr=[[values[1]-values[0]], [values[2]-values[1]]],
                        fmt='o', color='#244b92', capsize=7)
            ax.plot([i-.12, i+.12], [float(r['mean']['bounds'][0])*1e14]*2, color='#bb6200', lw=2)
            ax.plot([i-.12, i+.12], [float(r['mean']['bounds'][1])*1e14]*2, color='#bb6200', lw=2)
            for key in ('lower_endpoint', 'upper_endpoint'):
                b = [float(x)*1e14 for x in r[key]['bounds']]
                ax.fill_between([i-.10, i+.10], b[0], b[1], color='#244b92', alpha=.18)
        ax.set_xticks(range(4), ['Psi B / 2:1', 'Psi B / 6:1', 'Psi E / 2:1', 'Psi E / 6:1'])
        ax.set_ylabel('Permeability (10⁻¹⁴ m²)')
        ax.set_ylim(0, 10.3)
        ax.grid(axis='y', alpha=.2)
        ax.set_title('Figure 6.9 reconstruction • OBSERVED / reference\nFour condition means; source-internal evidence')
        fig.text(.5, .035, 'Blue: displayed variability, not confidence limits. Orange: mean reading bounds.\nShading: endpoint reading bounds. PHYSICAL_VALIDATION=NOT_ESTABLISHED.', ha='center', fontsize=9)
        fig.tight_layout(rect=(0, .10, 1, 1))
        fig.savefig(output, metadata={'Date': None, 'Creator': 'Puckworks bounded Figure 6.9 producer'})
        plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--plot', action='store_true')
    args = parser.parse_args()
    result = analyze()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output/'RESULT.json').write_text(json.dumps(result, default=serial, indent=2, sort_keys=True)+'\n')
    rows = []
    for r in result['observations']:
        row = {k: r[k] for k in ('condition', 'grind', 'journal_grind', 'chamber')}
        for k in ('mean', 'lower_endpoint', 'upper_endpoint'):
            row[k+'_m2'] = float(r[k]['central'])
            row[k+'_lower_m2'], row[k+'_upper_m2'] = map(float, r[k]['bounds'])
        rows.append(row)
    with (args.output/'readings.csv').open('w') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    if args.plot:
        plot(result, args.output/'reconstruction.svg')


if __name__ == '__main__':
    main()
