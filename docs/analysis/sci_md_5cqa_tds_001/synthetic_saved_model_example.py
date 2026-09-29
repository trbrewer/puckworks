"""Runnable SYNTHETIC example; these values do not reconstruct a physical shot.

Run from the repository root with PYTHONPATH=.; files live in a temporary directory.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from puckworks.analysis.conditional_5cqa_tds_delivery import EarlyInput, Model, State, synthetic_model


def main():
    with TemporaryDirectory(prefix='synthetic-five-cqa-') as directory:
        path = Path(directory)/'S2.json'
        synthetic_model('S2').save(path)
        model = Model.load(path)
        inputs = EarlyInput('S2', (.004, .006, .15, .10), input_class='SYNTHETIC')
        state = State.from_dict(model.condition(inputs).to_dict())
        prediction = state.remaining_5cqa(.06)
        print('SYNTHETIC_ONLY_NOT_A_PHYSICAL_SHOT')
        print(f'Modeled remaining 5-CQA: {prediction.five_cqa_mg:.6g} mg')
        print(f'Interval mean: {prediction.five_cqa_mg_g:.6g} mg/g')
        print(f'Numerical allowance: {prediction.allowance_kg:.6g} kg')
        print(f'Support: {prediction.support}; extrapolation: {prediction.feature_extrapolation}')


if __name__ == '__main__':
    main()
