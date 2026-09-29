"""Source-free saved research API example; illustrative inputs, not a source shot."""
from pathlib import Path

from puckworks.analysis.assay_conditioned_5cqa_delivery import EarlyInput, Model


def main():
    directory = Path(__file__).resolve().parent / 'models'
    for arm in ('A1', 'L1'):
        model = Model.load(directory / f'{arm}.json')
        state = model.condition(EarlyInput(.004, .006, .004, input_class='SYNTHETIC'))
        for p in state.predict_intervals([.01, .03], [.03, .05]):
            assert p.numerical_qualified
            print(arm, p.species, p.five_cqa_mg, 'mg', p.five_cqa_mg_g, 'mg/g',
                  p.allowance_kg, 'kg allowance', p.support, p.model_sha256)
        remaining = state.remaining_5cqa(.06)
        assert remaining.numerical_qualified
        print('Modeled delivery from anchor to 0.06 kg:', remaining.five_cqa_mg, 'mg')


if __name__ == '__main__':
    main()
