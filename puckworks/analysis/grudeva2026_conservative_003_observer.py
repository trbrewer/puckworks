"""Task-local raw baseline observation; never imported by the alternative core.

Captures solve_ivp RETURN objects, returns each identical object to the baseline,
and restores the temporary seam even on failure. No RHS or solver edits.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import numpy as np


@contextmanager
def capture_returns(module):
    original = module.solve_ivp
    captured = []
    def observe(*args, **kwargs):
        result = original(*args, **kwargs)
        captured.append({'start': float(args[1][0]), 'end': float(result.t[-1]),
                         'fixed': kwargs.get('events') is None, 'solution': result})
        return result
    with patch.object(module, 'solve_ivp', observe):
        yield captured


def evaluate(segments, t, *, side='right'):
    if side not in ('left', 'right'):
        raise ValueError('one-sided convention required')
    eligible = [s for s in segments if s['start'] <= t <= s['end']]
    if not eligible:
        raise ValueError('observation outside valid solution segments')
    segment = eligible[-1] if side == 'right' else eligible[0]
    return segment['solution'].sol(t), segment['fixed']


def observe_baseline(archive_path, controls, times, z):
    """Caller must first earn alternative qualification; this runs one baseline."""
    from puckworks.models.grudeva2026 import reduced
    archived = json.loads(Path(archive_path).read_text())['scientific_result']
    with capture_returns(reduced) as segments:
        original = reduced.simulate(controls=reduced.Controls(**controls),
                                    times=archived['time'], profile_z=archived['profile_z'])
    if original.status != 'COMPLETED':
        raise ArithmeticError('baseline execution failed: '+original.status)
    original_bytes = original.canonical_json().encode()
    n, modes = controls['cells'], controls['modes']
    # Independent observation weights/geometry, from the fixed baseline contract.
    weights = 6/(np.pi*np.arange(1., modes+1))**2
    weights = np.r_[weights, 1-sum(weights)]
    xi_faces = 1-(1-np.linspace(0., 1., n+1))**controls['front_mesh_power']
    xi_centers = (xi_faces[:-1]+xi_faces[1:])/2
    arrival = original.events['desaturation_exit']
    requested = sorted(set(times) | {1., arrival})
    records, snapshots = [], []
    raw_residual = shell_quadrature_error = 0.
    for t in requested:
        y, fixed = evaluate(segments, t)
        s, c, modal = y[0], y[1:n+1], y[n+1:-1].reshape(modes+1, n)
        physical_faces = s*xi_faces
        widths = np.diff(physical_faces)
        b = weights @ modal
        ic = float(widths @ c)
        ib = float(widths @ b)
        phases = np.array([ic+min(t, 1.)-s, 3.2*(ic+1.388*(1-s)), .8*(ib+1.388*(1-s))])
        residual = (sum(phases)+y[-1]-5.552)/5.552
        raw_residual = max(raw_residual, abs(residual))
        # Reordered modal/spatial integration, independent of Result inventories.
        independently_summed = sum(float(widths @ row)*weight for row, weight in zip(modal, weights))
        shell_quadrature_error = max(shell_quadrature_error, abs(ib-independently_summed))
        cf = c[-1]+(1-xi_centers[-1])*(c[-1]-c[-2])/(xi_centers[-1]-xi_centers[-2])
        outlet = 0. if t < 1 else (1. if t < arrival else cf)
        cp = np.where(z <= min(t, 1.), 1., 0.)
        bp = np.full(len(z), 1.388)
        active = z < s
        if s > 0:
            cp[active] = np.interp(z[active], np.r_[0., s*xi_centers, s], np.r_[0., c, cf])
            bp[active] = np.interp(z[active], s*xi_centers, b)
        cp[z == 0] = 0.
        if t >= arrival:
            cp[z == 1], bp[z == 1] = cf, b[-1]
        records.append([t, s, float(outlet), float(y[-1]), *phases.tolist(), float(residual)])
        snapshots.append({'t': t, 'side': 'right', 'faces': physical_faces.tolist(),
                          'liquid_cells': c.tolist(), 'modal_states': modal.tolist(),
                          'modal_weights': weights.tolist(), 'grain_integrals': (widths*b).tolist(),
                          'liquid_profile': cp.tolist(), 'grain_profile': bp.tolist()})
    expected = hashlib.sha256(json.dumps(archived, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    actual = hashlib.sha256(original_bytes).hexdigest()
    return {'controls': controls, 'status': original.status, 'arrival': arrival,
            'records': records, 'observations': snapshots, 'z': z.tolist(),
            'output_hash': actual, 'archived_identical_settings_hash': expected,
            'identical_settings': controls == archived['controls'],
            'output_hash_equal': actual == expected,
            'raw_state_max_normalized_residual': float(raw_residual),
            'independent_sum_error': float(shell_quadrature_error),
            'original_result': original.to_dict(), 'observer_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'physical_validation': 'NOT_ESTABLISHED'}
