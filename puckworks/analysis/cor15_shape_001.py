"""Descriptive Fig.10 shape transfer; Q-space fits, no cohort calibration or gates.

Reading realizations are graphical sensitivity, NOT repeated beds or a population CI.
SI boundaries; form A alone converts Pa to bar internally.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.stats import qmc

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / 'puckworks/data/romancorrochano2015/fig10_shape'
OUTPUT = ROOT / 'docs/research/COR15_SHAPE_001'
MODELS = ('L0', 'L1', 'L2', 'FA', 'FA-S')
N = 2.4709360685491837
PD_BAR = 3.5633704054718103
PSTAR_BAR = 24.396659674282887
PREF_PA = 100000.0


def fa_shape(p_pa, inverse_pstar=1 / PSTAR_BAR):
    p_bar = np.asarray(p_pa) / 100000.0
    return PD_BAR * (-np.expm1(-(p_bar / PD_BAR) ** N)) * np.exp(-p_bar * inverse_pstar)


def amplitude_fit(y, shape):
    """Positive amplitude profiled in equally weighted, dimensional Q-space."""
    amp = np.dot(y, shape) / np.dot(shape, shape)
    pred = amp * shape
    return float(amp), pred, float(np.mean((pred - y) ** 2))


def profile_exponential(y, base, coordinate):
    """Global grid brackets + scalar refinements, including both domain limits.

    Shape = base*exp(-z*coordinate), z>=0. Increasing the upper search point
    stops only at the representable infinite-z limit, not at a scientific bound.
    """
    coordinate = np.asarray(coordinate)
    coordinate = coordinate - coordinate.min()
    positive = coordinate[coordinate > 0]
    if not len(positive):
        a, pred, mse = amplitude_fit(y, base)
        return 0.0, a, pred, mse, 'unidentified_constant_grid', 0
    upper = 40.0 / positive.min()
    grid = np.unique(np.r_[0, np.linspace(0, min(8, upper), 49),
                           np.geomspace(min(.01, upper), upper, 48)])
    scale = np.mean(y ** 2)

    def evaluate(z):
        return amplitude_fit(y, base * np.exp(-z * coordinate))

    def objective(z):
        return evaluate(z)[2] / scale

    scores = np.array([objective(z) for z in grid])
    trials = [(scores[0], 0.0, 'lower_boundary')]
    minima = []
    for j in range(1, len(grid) - 1):
        if scores[j] <= scores[j-1] and scores[j] <= scores[j+1] and (
                scores[j] < scores[j-1] or scores[j] < scores[j+1]):
            opt = minimize_scalar(objective, bounds=(grid[j-1], grid[j+1]),
                                  method='bounded', options={'xatol': 1e-10})
            minima.append((float(opt.fun), float(opt.x), 'interior'))
    trials.extend(minima)
    limit = base * (coordinate == 0)
    a_inf, pred_inf, mse_inf = amplitude_fit(y, limit)
    trials.append((mse_inf / scale, np.inf, 'infinite_boundary'))
    score, z, status = min(trials)
    if np.isinf(z):
        return z, a_inf, pred_inf, mse_inf, status, len(minima)
    a, pred, mse = evaluate(z)
    return z, a, pred, mse, status, len(minima)


def fit_threshold(p, q):
    """Exact active-set enumeration for G*(P-P0)+, including constant limit."""
    order = np.argsort(p)
    x, y = p[order], q[order]
    candidates = []
    # Unconstrained affine regression within each active set.
    for j in range(len(x)-1):
        xx, yy = x[j:], y[j:]
        slope = np.sum((xx-xx.mean())*(yy-yy.mean())) / np.sum((xx-xx.mean())**2)
        if slope > 0:
            p0 = xx.mean() - yy.mean() / slope
            lo = x[j-1] if j else -np.inf
            if lo <= p0 <= x[j]:
                pred = slope * np.maximum(p-p0, 0)
                candidates.append((float(np.mean((pred-q)**2)), slope, p0, pred, 'interior'))
    for p0 in np.r_[0.0, x[:-1]]:
        a, pred, mse = amplitude_fit(q, np.maximum(p-p0, 0))
        candidates.append((mse, a, p0, pred, 'active_set_boundary'))
    constant = np.full_like(q, q.mean())
    candidates.append((float(np.mean((constant-q)**2)), 0.0, -np.inf,
                       constant, 'constant_limit_P0_minus_infinity'))
    mse, g, p0, pred, status = min(candidates, key=lambda v: v[0])
    return dict(amplitude=g, P0_Pa=p0, pred=pred, mse=mse, status=status,
                local_minima=0)


def fit(p, q, model):
    p, q = np.asarray(p), np.asarray(q)
    if np.any(p <= 0) or np.any(q <= 0):
        raise ValueError('This recovered-observation contract requires positive P and Q')
    if model == 'L1':
        r = fit_threshold(p, q)
    elif model in ('L0', 'FA'):
        a, pred, mse = amplitude_fit(q, p if model == 'L0' else fa_shape(p))
        r = dict(amplitude=a, pred=pred, mse=mse, status='interior', local_minima=0)
    elif model == 'L2':
        m, a, pred, mse, status, minima = profile_exponential(q, np.ones_like(p), -np.log(p/PREF_PA))
        # Internal shape is (P/max(P))^m; restore amplitude at fixed Pref.
        qref = a * np.exp(-m*np.log(p.max()/PREF_PA)) if np.isfinite(m) else np.nan
        r = dict(amplitude=qref, m=m, pred=pred, mse=mse, status=status, local_minima=minima)
    elif model == 'FA-S':
        lam, a, pred, mse, status, minima = profile_exponential(q, fa_shape(p, 0), p/100000)
        c = a * np.exp(lam*p.min()/100000) if np.isfinite(lam) else np.nan
        r = dict(amplitude=c, inverse_Pstar_bar=lam, pred=pred, mse=mse,
                 Pstar_bar=1/lam if lam else np.inf, status=status, local_minima=minima)
    else:
        raise ValueError(model)
    r.update(model=model, parameter_count=1 if model in ('L0', 'FA') else 2,
             rmse=np.sqrt(r['mse']), mean_signed_residual=float(np.mean(r['pred']-q)),
             lowest_signed_residual=float((r['pred']-q)[np.argmin(p)]))
    return r


def predict(p, result):
    p = np.asarray(p)
    model, a = result['model'], result['amplitude']
    if model == 'L0':
        return a*p
    if model == 'L1':
        return a*np.maximum(p-result['P0_Pa'], 0)
    if model == 'L2':
        return a*(p/PREF_PA)**result['m']
    return a*fa_shape(p, result.get('inverse_Pstar_bar', 1/PSTAR_BAR))


def matched_contrast(q, fa_pred, l0_pred, central_s2):
    """S² is supplied from CENTRAL observations, never estimated per realization."""
    return (np.mean((fa_pred-q)**2) - np.mean((l0_pred-q)**2)) / central_s2


def read_inputs():
    contract = json.loads((DATA/'contract.json').read_text())
    coords = list(csv.DictReader((DATA/'coordinates.csv').open()))
    return contract, coords


def realize(contract, coords, unit_offsets=None):
    """Four anchors shared across all four series in each panel; per-mean offsets."""
    if unit_offsets is None:
        unit_offsets = np.zeros(12 + 2*len(coords))
    calibrated = {}
    for j, panel in enumerate('abc'):
        a = contract['axes'][panel]
        calibrated[panel] = np.array([a[k] for k in ('x0', 'x1', 'y0', 'y1')]) + (
            np.asarray(unit_offsets[4*j:4*j+4]) * a['anchor_guard_px'])
    result = []
    for j, r in enumerate(coords):
        x0, x1, y0, y1 = calibrated[r['panel']]
        x, y = np.array([float(r['x_px']), float(r['y_px'])]) + (
            np.asarray(unit_offsets[12+2*j:14+2*j]) * float(r['mean_guard_px']))
        result.append(((y-y0)/(y1-y0)*450000, (x-x0)/(x1-x0)*1.8e-5))
    return np.asarray(result)


def interval(values):
    return np.quantile(values, [.025, .975]).tolist()


def write_csv(path, rows):
    with Path(path).open('w') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n')
        w.writeheader()
        w.writerows(rows)


def json_safe(obj):
    if isinstance(obj, dict):
        return {k: json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple, np.ndarray)):
        return [json_safe(v) for v in obj]
    if isinstance(obj, (float, np.floating)) and not np.isfinite(obj):
        return str(obj)
    if isinstance(obj, np.generic):
        return obj.item()
    return obj


def analyze(output=OUTPUT, reading_power=None):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    contract, coords = read_inputs()
    central = realize(contract, coords)
    names = list(dict.fromkeys(r['series'] for r in coords))
    indices = {s: np.array([j for j, r in enumerate(coords) if r['series'] == s]) for s in names}
    s2 = {s: float(np.mean(central[ii, 1]**2)) for s, ii in indices.items()}
    fits, contrasts, residuals, readings = [], [], [], []
    all_fits = {}
    for s, ii in indices.items():
        p, q = central[ii].T
        all_fits[s] = {model: fit(p, q, model) for model in MODELS}
        mf = fit(p, fa_shape(p), 'L2')['m']
        for model, r in all_fits[s].items():
            fits.append(dict(series=s, n_observations=len(ii), **{k: v for k, v in r.items() if k != 'pred'}))
            for j, pr, obs, pressure in zip(ii, r['pred'], q, p):
                residuals.append(dict(series=s, point_id=coords[j]['point_id'], model=model,
                                      P_Pa=pressure, Q_m3_s=obs, predicted_Q_m3_s=pr,
                                      signed_residual_m3_s=pr-obs))
        contrasts.append(dict(series=s, n=len(ii), S2_m6_s2=s2[s],
                              D_series=matched_contrast(q, all_fits[s]['FA']['pred'], all_fits[s]['L0']['pred'], s2[s]),
                              L2_m=all_fits[s]['L2']['m'], FA_grid_m=mf,
                              m_minus_mFA=all_fits[s]['L2']['m']-mf))
    for j, r in enumerate(coords):
        a = contract['axes'][r['panel']]
        dx, dy = 1.8e-5/(a['x1']-a['x0']), 450000/(a['y0']-a['y1'])
        readings.append(dict(**r, P_Pa=central[j, 0], P_bar=central[j, 0]/100000,
            Q_m3_s=central[j, 1],
            Q_SD_minus_m3_s=(float(r['x_px'])-float(r['sd_left_px']))*dx if r['sd_left_px'] else '',
            Q_SD_plus_m3_s=(float(r['sd_right_px'])-float(r['x_px']))*dx if r['sd_right_px'] else '',
            P_SD_minus_Pa=(float(r['sd_bottom_px'])-float(r['y_px']))*dy if r['sd_bottom_px'] else '',
            P_SD_plus_Pa=(float(r['y_px'])-float(r['sd_top_px']))*dy if r['sd_top_px'] else ''))
    power = contract['reading_design']['power'] if reading_power is None else reading_power
    design = qmc.Sobol(12+2*len(coords), scramble=True, seed=contract['reading_design']['seed'])
    draws = design.random_base2(power)*2-1
    realization_rows, sample_fits, sample_exponents = [], {}, {}
    for draw_id, u in enumerate(draws):
        values = realize(contract, coords, u)
        ds = []
        for s, ii in indices.items():
            p, q = values[ii].T
            fitted = {model: fit(p, q, model) for model in MODELS}
            d = matched_contrast(q, fitted['FA']['pred'], fitted['L0']['pred'], s2[s])
            mf = fit(p, fa_shape(p), 'L2')['m']
            ds.append(d)
            realization_rows.append(dict(realization=draw_id, series=s, D_series=d,
                L0_MSE_m6_s2=fitted['L0']['mse'], FA_MSE_m6_s2=fitted['FA']['mse'],
                S2_central_m6_s2=s2[s], m=fitted['L2']['m'], m_FA=mf,
                m_minus_m_FA=fitted['L2']['m']-mf))
            sample_exponents.setdefault(s, []).append([d, fitted['L2']['m'], mf, fitted['L2']['m']-mf])
            for model, r in fitted.items():
                sample_fits.setdefault((s, model), []).append(r)
        realization_rows.append(dict(realization=draw_id, series='POOLED', D_series=np.mean(ds),
            L0_MSE_m6_s2='', FA_MSE_m6_s2='', S2_central_m6_s2='', m='', m_FA='', m_minus_m_FA=''))
        if (draw_id+1) % 512 == 0:
            print(f'reading realizations: {draw_id+1}/{len(draws)}', flush=True)
    keys = ['amplitude', 'P0_Pa', 'm', 'Pstar_bar', 'inverse_Pstar_bar', 'rmse',
            'mean_signed_residual', 'lowest_signed_residual']
    model_rows = []
    for r in fits:
        sample = sample_fits[(r['series'], r['model'])]
        row = {k: r.get(k, '') for k in ['series','model','parameter_count','n_observations','status','local_minima'] + keys}
        row['amplitude_units'] = {'L0':'m3/(s Pa)','L1':'m3/(s Pa)','L2':'m3/s','FA':'m3/(s bar)','FA-S':'m3/(s bar)'}[r['model']]
        for k in keys:
            vv = [x[k] for x in sample if k in x]
            lo, hi = interval(vv) if vv else ('', '')
            row[k+'_reading_lo'], row[k+'_reading_hi'] = lo, hi
        row['reading_boundary_count'] = sum(x['status'] != 'interior' for x in sample)
        model_rows.append(row)
    for r in contrasts:
        values = np.array(sample_exponents[r['series']])
        for k, col in zip(['D_series','L2_m','FA_grid_m','m_minus_mFA'], values.T):
            r[k+'_reading_lo'], r[k+'_reading_hi'] = interval(col)
    d_values = [r['D_series'] for r in realization_rows if r['series'] == 'POOLED']
    result = dict(task='PW-COR15-SHAPE-001', observed_points=len(coords), series=12,
        central_D=float(np.mean([r['D_series'] for r in contrasts])), D_reading_interval=interval(d_values),
        D_sampled_range=[min(d_values), max(d_values)], reading_realizations=len(draws),
        reading_interval_definition=contract['reading_design'],
        central_fits=all_fits,
        input_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in
                      [DATA/'coordinates.csv', DATA/'contract.json', Path(__file__)]})
    write_csv(output/'DIGITIZED.csv', readings)
    write_csv(output/'MODELS.csv', model_rows)
    write_csv(output/'RESIDUALS.csv', residuals)
    write_csv(output/'CONTRASTS.csv', contrasts)
    write_csv(output/'READING_REALIZATIONS.csv', realization_rows)
    table2_check(output, all_fits)
    (output/'RESULT.json').write_text(json.dumps(json_safe(result), indent=2, allow_nan=False)+'\n')
    plot(readings, all_fits, output)
    print(json.dumps({k:result[k] for k in ('central_D','D_reading_interval','D_sampled_range')}), flush=True)
    return result


def table2_check(output, all_fits):
    table = list(csv.DictReader((ROOT/'puckworks/data/romancorrochano2015/table2.csv').open()))
    consolidation = json.loads((ROOT/'docs/analysis/sci_val_tamped_k_001/SOURCE_CONSISTENCY.json').read_text())
    lam = {x['case']: x['lambda_average_read'] for x in consolidation['cases']}
    area = np.pi*.037**2/4
    rows = []
    for r in table:
        s = r['grind']+'-'+r['bulk_density_kgm3']
        length = .0185*(1-lam[s])
        g = all_fits[s]['L0']['amplitude']
        factor = g*length/area
        k = float(r['permeability_m2'])
        rows.append(dict(series=s, G_m3_s_Pa=g, initial_length_m=.0185,
            lambda_average=lam[s], reconstructed_consolidated_length_m=length, area_m2=area,
            k_over_mu_m2_Pa_s=factor, table2_k_m2=k, table2_k_SD_m2=r['permeability_sd_m2'],
            implied_mu_to_match_table2_Pa_s=k/factor, reconstructed_k_m2='',
            qualification='absolute_k_unresolved_source_numerical_mu_and_individual_Lactual_unavailable'))
    write_csv(output/'TABLE2_CHECK.csv', rows)


def plot(readings, all_fits, output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from puckworks.public.schema import Producer
    from puckworks.viz.spec import VizSpec
    spec = VizSpec(id='cor15_shape_001', title='Frozen D0 shape on Corrochano Fig.10', class_=1,
        producer=Producer(module='puckworks.analysis.cor15_shape_001', function='analyze', result_map={'fits':'central_fits'}),
        badge='OBSERVED', evidence_strength='post-fit reconstruction', components=[],
        fidelity_ceiling='Descriptive fit to recovered mean markers, not individual beds or universal permeability.',
        render_fn='puckworks.analysis.cor15_shape_001:plot',
        caption='Original axes; fitted Q conditional on P. Bars: recoverable source SD across three beds, not reading intervals.',
        outputs=['comparison.svg'], used_in='PW-COR15-SHAPE-001')
    if spec.validate():
        raise ValueError(spec.validate())
    colours = dict(L0='#222222', L1='#25915a', L2='#7860b5', FA='#d34124', **{'FA-S':'#187ba0'})
    with matplotlib.rc_context({'svg.hashsalt':'PW-COR15-SHAPE-001','font.size':9}):
        fig, axes = plt.subplots(3, 4, figsize=(13, 10), sharey=True)
        for i, density in enumerate((360,400,480)):
            for j, grind in enumerate('ABCD'):
                s, ax = f'{grind}-{density}', axes[i,j]
                rr = [r for r in readings if r['series'] == s]
                p = np.array([r['P_Pa'] for r in rr])
                for r in rr:
                    xerr = np.array([[r['Q_SD_minus_m3_s']], [r['Q_SD_plus_m3_s']]])*1e6 if r['Q_SD_minus_m3_s'] != '' else None
                    yerr = np.array([[r['P_SD_minus_Pa']], [r['P_SD_plus_Pa']]])/100000 if r['P_SD_minus_Pa'] != '' else None
                    ax.errorbar(r['Q_m3_s']*1e6, r['P_bar'], xerr=xerr, yerr=yerr,
                        fmt='o', mfc='white', mec='black', ms=3.5, ecolor='.55', capsize=2, lw=.7, zorder=5)
                grid = np.linspace(p.min(), p.max(), 300)
                for model in MODELS:
                    ax.plot(predict(grid, all_fits[s][model])*1e6, grid/100000,
                            color=colours[model], lw=1.5 if model in ('FA','L0') else 1,
                            ls='-' if model in ('FA','L0') else '--', label=model+(' (1)' if model in ('FA','L0') else ' (2)'))
                ax.set_title(f'{s} kg/m³ • {len(rr)} means')
                ax.set_ylim(0,4.6); ax.set_xlim(left=0); ax.grid(alpha=.15)
                if i == 2: ax.set_xlabel('Inlet-meter Q (10⁻⁶ m³/s)')
                if j == 0: ax.set_ylabel('Corrected bed ΔP (bar)')
        handles, labels = axes[0,0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', ncol=5, bbox_to_anchor=(.5,.963))
        fig.suptitle('Corrochano 2015 Fig.10: separate fits to each series', y=.99)
        fig.text(.02,.024, spec.badge_line()+' • Equal Q-space weights; curves shown only over retained pressure support.', fontsize=9)
        fig.text(.02,.007,'Bars: recoverable three-bed SD; missing bars are unresolved. Reading uncertainty is separate. Source CC BY 3.0, doi:10.1016/j.jfoodeng.2014.11.006.',fontsize=8)
        fig.tight_layout(rect=(0,.045,1,.93)); fig.savefig(output/'comparison.svg', metadata={'Date':None}); plt.close(fig)
        svg = output/'comparison.svg'
        svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    parser.add_argument('--reading-power', type=int, default=None, help='Verification override; report uses contract count')
    args = parser.parse_args()
    analyze(args.output, args.reading_power)
