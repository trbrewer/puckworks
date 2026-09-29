"""Source-free synthetic save/load/condition example for all three contracts."""
from math import log
from pathlib import Path
from tempfile import TemporaryDirectory

from puckworks.analysis.early_assay_5cqa_delivery import (
    L1MInput, L2MInput, L12Input, Model, canonical, feature_names,
)


def main():
    inputs = {'L1M': L1MInput(.004, .006, .002, input_class='SYNTHETIC'),
              'L2M': L2MInput(.004, .006, .001, input_class='SYNTHETIC'),
              'L12': L12Input(.004, .006, .002, .001, input_class='SYNTHETIC')}
    with TemporaryDirectory() as directory:
        for arm, early in inputs.items():
            n = len(feature_names(arm))
            model = Model(arm, [[log(.001/.999)]+[0.]*n]*5,
                early.values, early.values, early.values, .06, .01,
                canonical({'species': '5CQA', 'scope': 'SYNTHETIC_NOT_FITTED'}),
                'SYNTHETIC_FIRST_PARTY')
            path = Path(directory)/(arm+'.json')
            model.save(path)
            state = Model.load(path).condition(early)
            for p in state.predict_intervals([.01, .03], [.03, .05]):
                assert p.numerical_qualified
                print(arm, p.species, p.five_cqa_mg, 'mg', p.five_cqa_mg_g, 'mg/g',
                      p.allowance_kg, 'kg numerical allowance', p.support)
            print(arm, 'modeled delivery from anchor to supplied 0.06 kg stop:',
                  state.remaining_5cqa(.06).five_cqa_mg, 'mg')


if __name__ == '__main__':
    main()
