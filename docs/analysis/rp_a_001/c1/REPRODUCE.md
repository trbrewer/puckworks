# Reproduce C1

Use execution commit `8a4d2ffa35f45f9c44d0db0659ff0f1d469c8aa7`, tree
`94499f4f8f9a350894c60c1e23924e4d5644f874`, Python 3.12.3, NumPy 2.2.6,
and SciPy 1.15.3:

```bash
python -m puckworks.analysis.response_atlas validate
python -m puckworks.analysis.response_atlas run
python -m puckworks.analysis.response_atlas verify
python -m pytest tests/test_response_atlas.py tests/test_response_atlas_c1.py -q
```

`runtime.json` contains the sole normalized operational field,
`wall_time_seconds`. All scientific payload fields and the exact export consumed
downstream are byte-compared by `verify`.
