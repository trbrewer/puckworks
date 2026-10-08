"""Small offline cell-average observation example; no production solve.

python examples/grudeva2026_baseline_observation_005.py
For a retained production capture, use Trajectory(path), evaluate(t), profiles(...).
"""
import json

import numpy as np

from puckworks.analysis.grudeva2026_baseline_observation_005 import cell_reconstruction


def main():
    # Manufactured field f(z)=.2+.3*z+.1*z^2 on a moving graded domain [0,.4].
    faces = .4*(1-(1-np.arange(9)/8)**2)
    a, b = faces[:-1], faces[1:]
    averages = .2+.3*(a+b)/2+.1*(a*a+a*b+b*b)/3
    z = np.array([0., .025, .1, .25, .4])
    observed = cell_reconstruction(faces, averages, z)
    exact = .2+.3*z+.1*z*z
    print(json.dumps({'kind': 'MANUFACTURED_OBSERVER_EXAMPLE_NOT_A_PRODUCTION_RUN',
                      'z': z.tolist(), 'concentration': observed.tolist(),
                      'maximum_error': float(np.max(abs(observed-exact))),
                      'physical_validation': 'NOT_ESTABLISHED'}, sort_keys=True))


if __name__ == '__main__':
    main()
