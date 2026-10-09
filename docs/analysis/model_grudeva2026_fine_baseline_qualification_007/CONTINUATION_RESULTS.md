# 007 continuation result

**FINE_BASELINE_QUALIFICATION_INCOMPLETE**

The owner override continues the original qualification with no task time budget, attempt quota or application memory ceiling. Original timeout and accounting remain unchanged in [RESULTS.md](RESULTS.md) and [ACCOUNTING.json](ACCOUNTING.json).

G1 / NO_GOVERNING_PHYSICS_CHANGE. **PHYSICAL_VALIDATION=NOT_ESTABLISHED.**

Declared baseline: canonical physical parameters, 512 cells / 32 resolved modes plus unchanged production tail, mesh power 2, rtol=2e-8, atol=2e-10, max_step=.05, horizon=8. Original PLAN and mathematical observer remain unchanged.

The combined production solve completed through horizon 8, but segment 2 failed the unchanged accepted-state/dense-replay agreement gate: **5.401235014801387e-13 > 4.547473508864641e-13**. All three segment archives passed file integrity and returned-array fidelity; segments 0/1 passed replay. Segment 2's live/offline dense difference was zero, while agreement with the accepted solver states exceeded the separate allowance. [CONTINUATION_FAILURE.json](CONTINUATION_FAILURE.json) binds the saved receipts and exact predicate. The receipt records 818 accepted states and 1,637 replay points on [6.504309539469248, 8], but does not retain the exact time/state index of the maximum. That location is unavailable; it has not been invented or recomputed.

The combined 22 individual audits and 11 comparison families were not evaluated after this required replay failure. Their unavailable results do not establish measured refinement inadequacy or a production coding defect. No retry, retuning, tolerance change or extra numerical reduction followed.

## Reuse and prerequisite evidence

Original `006-spatial-512` is reused with its original task, attempt, source and PLAN identity. All 22 original individual gates pass. Passing [READOUT.json](READOUT.json) was reused without another fixture campaign: each family has 139 requested / 84 eligible / 55 younger / 0 unavailable, 18 independent reference checks at 32 modes and 24 at 64 modes. Eligible, younger and raw-endpoint results remain separate.

| Stage | Execution | Status | Pass | Exit |
|---|---|---|---|---|
| 007-pilot | 007-pilot-0001 | ROW_PASSED | True | 0 |
| 007-control_512 | 007-control_512-0001 | ROW_PASSED | True | 0 |
| 007-repeat_512 | 007-repeat_512-0001 | ROW_PASSED | True | 0 |
| 007-modes_fine | 007-modes_fine-0001 | ROW_PASSED | True | 0 |
| 007-time_fine | 007-time_fine-0001 | ROW_PASSED | True | 0 |
| 007-bed_fine | 007-bed_fine-0001 | ROW_PASSED | True | 0 |
| 007-combined | 007-combined-0001 | EXECUTION_INCOMPLETE | False | 1 |

All six declared full rows executed. The combined row is incomplete at replay admission; its subsequent audits and comparison are unavailable. All saved failures and unavailable requirements remain in [CONTINUATION_RESULTS.json](CONTINUATION_RESULTS.json).

## Neutrality and repeatability

- 007-control_512: {"left_sha256": "84a42781d60c2fb5df10a82a7db9663177db96eb21a1e8f9ab57cf86a2dd15e6", "passed": true, "right_sha256": "84a42781d60c2fb5df10a82a7db9663177db96eb21a1e8f9ab57cf86a2dd15e6"}
- 007-repeat_512: {"fields": {"complete_observations_and_audits": {"left_sha256": "20815a7dd6256267cd84fc2187dd2028eaefe73eb2b33a39d31601a8e2d1cb75", "passed": true, "right_sha256": "20815a7dd6256267cd84fc2187dd2028eaefe73eb2b33a39d31601a8e2d1cb75"}, "controls": {"left_sha256": "219b2c62563556c979cafeb4a50d46461047bb46db656a8d5de0d47f15b91a93", "passed": true, "right_sha256": "219b2c62563556c979cafeb4a50d46461047bb46db656a8d5de0d47f15b91a93"}, "environment": {"left_sha256": "753a9b0908d45d5c97af39a90f453d7aec634e8585fcf118955aeb7d97cd995f", "passed": true, "right_sha256": "753a9b0908d45d5c97af39a90f453d7aec634e8585fcf118955aeb7d97cd995f"}, "geometry": {"left_sha256": "bce6a5119f6b97e0eb9bb25a9d2d8dab5ea8ca47f2192f352e33a6ed407c1555", "passed": true, "right_sha256": "bce6a5119f6b97e0eb9bb25a9d2d8dab5ea8ca47f2192f352e33a6ed407c1555"}, "parameters": {"left_sha256": "3f232116bb2aee01f1c3faa90f5f3b0e734f8ff33923cc0240d7cf1d05a2caea", "passed": true, "right_sha256": "3f232116bb2aee01f1c3faa90f5f3b0e734f8ff33923cc0240d7cf1d05a2caea"}, "public_result": {"left_sha256": "84a42781d60c2fb5df10a82a7db9663177db96eb21a1e8f9ab57cf86a2dd15e6", "passed": true, "right_sha256": "84a42781d60c2fb5df10a82a7db9663177db96eb21a1e8f9ab57cf86a2dd15e6"}, "requests": {"left_sha256": "751bbda6fa1ed937f2cfbae594ca768ef2ae0c07830fb4f1c6dd37695bdbbeb1", "passed": true, "right_sha256": "751bbda6fa1ed937f2cfbae594ca768ef2ae0c07830fb4f1c6dd37695bdbbeb1"}, "retained_scientific_state": {"left_sha256": "959bc7b3caba24783f817dff0e0b1449f4f48075c68647b66628e8500cf84901", "passed": true, "right_sha256": "959bc7b3caba24783f817dff0e0b1449f4f48075c68647b66628e8500cf84901"}, "sources": {"left_sha256": "f9eedbafa463436c1caba50c92bf327c004d82bf085b2c651f8e0d1c66615cc7", "passed": true, "right_sha256": "f9eedbafa463436c1caba50c92bf327c004d82bf085b2c651f8e0d1c66615cc7"}, "state_layout": {"left_sha256": "84d910587d6e3dcd9056a24f1f885ffa7614eba8012a34aa9a95ca6497a1afd4", "passed": true, "right_sha256": "84d910587d6e3dcd9056a24f1f885ffa7614eba8012a34aa9a95ca6497a1afd4"}}, "passed": true}

## Four mandatory refinement comparisons

| Baseline versus | Family | Requested | Included | Excluded | Unavailable | Maximum | Exact location | Allowance | Pass |
|---|---|---:|---:|---:|---:|---|---|---|---|
| bed_fine | activation | 220 | 220 | 0 | 0 | 1.310299016399341e-06 | `{"index": [124], "z": 0.58}` | 0.001 | True |
| bed_fine | arrival | 1 | 1 | 0 | 0 | 1.0648704993343472e-06 | `{"normal_t": 6.504308470045491, "refined_t": 6.504309534915991, "z": 1.0}` | 0.001 | True |
| bed_fine | boulder_inventory | 395 | 395 | 0 | 0 | 1.58756734120781e-07 | `{"index": [335], "t": 6.675}` | 5e-05 | True |
| bed_fine | cup | 395 | 395 | 0 | 0 | 1.1359537293031963e-06 | `{"index": [318], "t": 6.6}` | 5e-05 | True |
| bed_fine | fines_inventory | 395 | 395 | 0 | 0 | 7.719664158554324e-07 | `{"index": [315], "t": 6.585}` | 5e-05 | True |
| bed_fine | front | 395 | 395 | 0 | 0 | 2.000138394908646e-07 | `{"index": [152], "t": 3.75}` | 0.001 | True |
| bed_fine | grain_histories | 2765 | 1794 | 971 | 0 | 2.2238686942011032e-05 | `{"index": [241, 5], "t": 5.975, "z": 0.9}` | 0.00023 | True |
| bed_fine | grain_profiles | 86900 | 56541 | 30359 | 0 | 2.838995476062145e-05 | `{"index": [300, 218], "t": 6.515, "z": 0.995}` | 0.00023 | True |
| bed_fine | liquid_inventory | 395 | 395 | 0 | 0 | 2.412395050388483e-07 | `{"index": [315], "t": 6.585}` | 5e-05 | True |
| bed_fine | liquid_profiles | 86900 | 85676 | 1224 | 0 | 1.0955429761455582e-05 | `{"index": [304, 215], "t": 6.535, "z": 0.9852289512555391}` | 0.001 | True |
| bed_fine | outlet | 395 | 381 | 14 | 0 | 5.153306481819886e-06 | `{"index": [303], "t": 6.53}` | 0.001 | True |
| combined | activation | 220 | 0 | 0 | 220 | None | `null` | 0.001 | False |
| combined | arrival | 1 | 0 | 0 | 1 | None | `null` | 0.001 | False |
| combined | boulder_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | cup | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | fines_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | front | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| combined | grain_histories | 2765 | 0 | 0 | 2765 | None | `null` | 0.00023 | False |
| combined | grain_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.00023 | False |
| combined | liquid_inventory | 395 | 0 | 0 | 395 | None | `null` | 5e-05 | False |
| combined | liquid_profiles | 86900 | 0 | 0 | 86900 | None | `null` | 0.001 | False |
| combined | outlet | 395 | 0 | 0 | 395 | None | `null` | 0.001 | False |
| modes_fine | activation | 220 | 220 | 0 | 0 | 1.3299318091242185e-08 | `{"index": [218], "z": 0.995}` | 0.001 | True |
| modes_fine | arrival | 1 | 1 | 0 | 0 | 1.3036094870244597e-08 | `{"normal_t": 6.504308470045491, "refined_t": 6.504308483081586, "z": 1.0}` | 0.001 | True |
| modes_fine | boulder_inventory | 395 | 395 | 0 | 0 | 1.0331853150802317e-09 | `{"index": [19], "t": 0.45}` | 5e-05 | True |
| modes_fine | cup | 395 | 395 | 0 | 0 | 9.253069421788496e-10 | `{"index": [299], "t": 6.51}` | 5e-05 | True |
| modes_fine | fines_inventory | 395 | 395 | 0 | 0 | 1.2712542130088877e-09 | `{"index": [28], "t": 0.675}` | 5e-05 | True |
| modes_fine | front | 395 | 395 | 0 | 0 | 2.0315269466664176e-09 | `{"index": [289], "t": 6.465}` | 0.001 | True |
| modes_fine | grain_histories | 2765 | 1794 | 971 | 0 | 1.6162857963131216e-07 | `{"index": [302, 6], "t": 6.525, "z": 1.0}` | 0.00023 | True |
| modes_fine | grain_profiles | 86900 | 56541 | 30359 | 0 | 2.7875144559263987e-07 | `{"index": [11, 6], "t": 0.25, "z": 0.03}` | 0.00023 | True |
| modes_fine | liquid_inventory | 395 | 395 | 0 | 0 | 9.199391248770894e-10 | `{"index": [248], "t": 6.15}` | 5e-05 | True |
| modes_fine | liquid_profiles | 86900 | 85676 | 1224 | 0 | 2.6220855875447313e-08 | `{"index": [37, 30], "t": 0.9, "z": 0.135}` | 0.001 | True |
| modes_fine | outlet | 395 | 381 | 14 | 0 | 1.4131903813829894e-08 | `{"index": [303], "t": 6.53}` | 0.001 | True |
| time_fine | activation | 220 | 220 | 0 | 0 | 9.623954966286874e-09 | `{"index": [219], "z": 1.0}` | 0.001 | True |
| time_fine | arrival | 1 | 1 | 0 | 0 | 9.623954966286874e-09 | `{"normal_t": 6.504308470045491, "refined_t": 6.504308460421536, "z": 1.0}` | 0.001 | True |
| time_fine | boulder_inventory | 395 | 395 | 0 | 0 | 2.2257204829179145e-09 | `{"index": [247], "t": 6.125}` | 5e-05 | True |
| time_fine | cup | 395 | 395 | 0 | 0 | 1.2943076832527822e-08 | `{"index": [386], "t": 7.8}` | 5e-05 | True |
| time_fine | fines_inventory | 395 | 395 | 0 | 0 | 8.652416783050398e-09 | `{"index": [250], "t": 6.2}` | 5e-05 | True |
| time_fine | front | 395 | 395 | 0 | 0 | 1.4638704692870874e-09 | `{"index": [297], "t": 6.50125313283208}` | 0.001 | True |
| time_fine | grain_histories | 2765 | 1794 | 971 | 0 | 1.4304369788664673e-07 | `{"index": [10, 0], "t": 0.225, "z": 0.025}` | 0.00023 | True |
| time_fine | grain_profiles | 86900 | 56541 | 30359 | 0 | 2.852371735473369e-07 | `{"index": [11, 6], "t": 0.25, "z": 0.03}` | 0.00023 | True |
| time_fine | liquid_inventory | 395 | 395 | 0 | 0 | 2.1725500287672617e-09 | `{"index": [252], "t": 6.25}` | 5e-05 | True |
| time_fine | liquid_profiles | 86900 | 85676 | 1224 | 0 | 4.0774566389956135e-08 | `{"index": [306, 219], "t": 6.545, "z": 1.0}` | 0.001 | True |
| time_fine | outlet | 395 | 381 | 14 | 0 | 4.077456572382232e-08 | `{"index": [306], "t": 6.545}` | 0.001 | True |

Comparisons retain each actual pair’s unchanged masks, all seven histories, event-side semantics and allowances. Unavailable maxima/locations are not zero error.

## Individual audits

For diagnostic bounds, the displayed maximum is the observed value, not an error. Grain gates require the minimum to be at least -1e-8; liquid also requires the maximum to be at most 1+1e-8. Their full minima and locations are retained in JSON. Categorical gates have no physical maximum.

### baseline_512 (original 006 reuse)

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 3039/3039/0/0 | 3.037545239352549e-09 | `{"provenance": "accepted", "segment": 1, "t": 6.155460976930302}` | 1e-06 | True |
| cup_quadrature | 3686/3686/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 3686/3686/0/0 | 3.1560185576040567e-09 | `{"t": 7.547969439045619}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.025}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.0}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 1.5171920852152798e-06 | `{"t": 0.175, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 0.0, "z": 0.0}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 6074/6074/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 3039/3039/0/0 | 0.00018310546875 | `{"provenance": "accepted", "segment": 0, "t": 0.46325122333617424}` | 1.0 | True |
| phase_bounds | 3039/3039/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 4.440892098500626e-16 | `{"field": "grain", "t": 6.451127819548873, "z": 0.99}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 33/33/0/0 | 0.0 | `{"rate_mode_index": 0, "tail_index": 32, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

### 007-bed_fine

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 6287/6287/0/0 | 3.620055081340113e-14 | `{"cell": 230, "provenance": "accepted", "segment": 1, "t": 6.504309534915991, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 6287/6287/0/0 | 3.872336329273135e-10 | `{"provenance": "accepted", "segment": 2, "t": 6.526092038838937}` | 1e-06 | True |
| cup_quadrature | 6934/6934/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 6934/6934/0/0 | 3.771564394128291e-09 | `{"t": 7.98978315529864}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 6.32, "z": 0.25}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 6.51, "z": 0.29}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 4.4068166296651334e-07 | `{"t": 0.175, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 6.504309534915991, "z": 0.4}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 12570/12570/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 6287/6287/0/0 | 7.070254363963802e-15 | `{"cell": 160, "provenance": "accepted", "segment": 2, "t": 6.506374464664728}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 6287/6287/0/0 | 0.00018310546875 | `{"provenance": "accepted", "segment": 0, "t": 0.21725553939803435}` | 1.0 | True |
| phase_bounds | 6287/6287/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 2.220446049250313e-16 | `{"field": "grain", "t": 0.0, "z": 0.0}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 33/33/0/0 | 0.0 | `{"rate_mode_index": 0, "tail_index": 32, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

### 007-modes_fine

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 3306/3306/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 3306/3306/0/0 | 2.9872638144754732e-09 | `{"provenance": "accepted", "segment": 2, "t": 6.505158318528766}` | 1e-06 | True |
| cup_quadrature | 3953/3953/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 3953/3953/0/0 | 3.434713846672821e-09 | `{"t": 7.5029039252146}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000006 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.025}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000006 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.0}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 1.491649935542183e-06 | `{"t": 0.2, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 0.0, "z": 0.0}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 6608/6608/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 3306/3306/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 3306/3306/0/0 | 0.0001220703125 | `{"provenance": "accepted", "segment": 0, "t": 0.12957523985775227}` | 1.0 | True |
| phase_bounds | 3306/3306/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 6.661338147750939e-16 | `{"field": "grain", "t": 0.0, "z": 0.0}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 65/65/0/0 | 2.220446049250313e-16 | `{"rate_mode_index": 64, "tail_index": 64, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

### 007-repeat_512

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 3039/3039/0/0 | 3.037545239352549e-09 | `{"provenance": "accepted", "segment": 1, "t": 6.155460976930302}` | 1e-06 | True |
| cup_quadrature | 3686/3686/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 3686/3686/0/0 | 3.1560185576040567e-09 | `{"t": 7.547969439045619}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.025}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.0}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 1.5171920852152798e-06 | `{"t": 0.175, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 0.0, "z": 0.0}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 6074/6074/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 3039/3039/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 3039/3039/0/0 | 0.00018310546875 | `{"provenance": "accepted", "segment": 0, "t": 0.46325122333617424}` | 1.0 | True |
| phase_bounds | 3039/3039/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 4.440892098500626e-16 | `{"field": "grain", "t": 6.451127819548873, "z": 0.99}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 33/33/0/0 | 0.0 | `{"rate_mode_index": 0, "tail_index": 32, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

### 007-time_fine

| Gate | Requested/included/excluded/unavailable | Maximum | Location | Allowance | Pass |
|---|---|---|---|---|---|
| activation_support | 227/227/0/0 | 0 | `null` | 0 | True |
| aqueous_bounds | 4105/4105/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0, "trace": false}` | 1e-08 | True |
| complete_status | 1/1/0/0 | 0 | `null` | 0 | True |
| conservation | 4105/4105/0/0 | 7.060256957999683e-10 | `{"provenance": "accepted", "segment": 1, "t": 6.424846125056525}` | 1e-06 | True |
| cup_quadrature | 4752/4752/0/0 | 0.0 | `{"t": 0.0}` | 1e-10 | True |
| cup_state_integral | 4752/4752/0/0 | 2.992877057295118e-10 | `{"t": 6.917565034089554}` | 5e-05 | True |
| diagnostic_grain_history_bounds | 4326/4326/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.025}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.025}}` | 1e-08 | True |
| diagnostic_grain_profile_bounds | 135960/135960/0/0 | 1.3880000000000001 | `{"maximum": {"provenance": "required", "t": 0.0, "z": 0.0}, "minimum": {"provenance": "required", "t": 8.0, "z": 0.0}}` | 1e-08 | True |
| diagnostic_inlet | 395/395/0/0 | 1.5185224956359988e-06 | `{"t": 0.2, "z": 0.0}` | 2e-05 | True |
| diagnostic_liquid_profile_bounds | 135960/135960/0/0 | 1.0 | `{"maximum": {"provenance": "required", "t": 0.01, "z": 0.005}, "minimum": {"provenance": "required", "t": 0.0, "z": 0.0}}` | 1e-08 | True |
| events | 2/2/0/0 | 0 | `null` | 0 | True |
| front_support | 8206/8206/0/0 | 0.0 | `{"provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-10 | True |
| grain_bounds | 4105/4105/0/0 | 0.0 | `{"cell": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| horizon | 1/1/0/0 | 0 | `null` | 0 | True |
| independent_inventory_sums | 4105/4105/0/0 | 0.0001220703125 | `{"provenance": "accepted", "segment": 0, "t": 0.22313331206092152}` | 1.0 | True |
| phase_bounds | 4105/4105/0/0 | 0.0 | `{"phase": 0, "provenance": "accepted", "segment": 0, "t": 0.0}` | 1e-08 | True |
| public_cup_outlet_reconstruction | 150/150/0/0 | 0.0 | `{"field": "cup", "t": 0.0}` | 2.2737367544323206e-13 | True |
| public_inventory_algebra | 225/225/0/0 | 0.0009381003842459175 | `{"phase": 1, "t": 0.0}` | 1.0 | True |
| public_profile_reconstruction | 18000/18000/0/0 | 4.440892098500626e-16 | `{"field": "grain", "t": 6.421052631578947, "z": 0.9852289512555391}` | 2.2737367544323206e-13 | True |
| required_times | 614/614/0/0 | 0 | `null` | 0 | True |
| solver_segments | 3/3/0/0 | 0 | `null` | 0 | True |
| tail_weights_rates | 33/33/0/0 | 0.0 | `{"rate_mode_index": 0, "tail_index": 32, "weight_mode_index": 0}` | 5.684341886080802e-14 | True |

### 007-combined: not evaluated after replay failure

| Required gate | Status | Support / maximum / location | Allowance |
|---|---|---|---|
| activation_support | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| aqueous_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| complete_status | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| conservation | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-06 |
| cup_quadrature | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-10 |
| cup_state_integral | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 5e-05 |
| diagnostic_grain_history_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| diagnostic_grain_profile_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| diagnostic_inlet | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 2e-05 |
| diagnostic_liquid_profile_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| events | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| front_support | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-10 |
| grain_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| horizon | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| independent_inventory_sums | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1.0 |
| phase_bounds | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1e-08 |
| public_cup_outlet_reconstruction | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 2.2737367544323206e-13 |
| public_inventory_algebra | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 1.0 |
| public_profile_reconstruction | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 2.2737367544323206e-13 |
| required_times | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| solver_segments | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 0 |
| tail_weights_rates | NOT_EVALUATED_AFTER_REPLAY_FAILURE | unavailable | 5.684341886080802e-14 |

Pilot-specific gates and audit values (horizon .4, legitimate dry activation support, no full-horizon event requirements):

```json
{
  "activation_support": true,
  "aqueous_bounds": true,
  "complete_status": true,
  "conservation": true,
  "cup_quadrature": true,
  "cup_state_integral": true,
  "diagnostic_grain_history_bounds": true,
  "diagnostic_grain_profile_bounds": true,
  "diagnostic_inlet": true,
  "diagnostic_liquid_profile_bounds": true,
  "events": true,
  "front_support": true,
  "grain_bounds": true,
  "horizon": true,
  "independent_inventory_sums": true,
  "phase_bounds": true,
  "public_cup_outlet_reconstruction": true,
  "public_inventory_algebra": true,
  "public_profile_reconstruction": true,
  "required_times": true,
  "solver_segments": true,
  "tail_weights_rates": true
}
```

## Accounting and stop reasons

| Execution | Kind | Seconds | Exit | Classification | Maximum observed virtual bytes | Maximum observed resident high-water bytes |
|---|---|---:|---:|---|---:|---:|
| 007-pilot-0001 | short | 2737.3964768830047 | 0 | none | 26274754560 | 26023190528 |
| 007-control_512-0001 | full | 101.15584233999834 | 0 | none | 2079502336 | 1692459008 |
| 007-repeat_512-0001 | full | 160.48480794299394 | 0 | none | 3691864064 | 3369435136 |
| 007-modes_fine-0001 | full | 642.6270315209986 | 0 | none | 7247208448 | 6945710080 |
| 007-time_fine-0001 | full | 194.03008122299798 | 0 | none | 4956700672 | 4528271360 |
| 007-bed_fine-0001 | full | 591.8545508550014 | 0 | none | 13936336896 | 13461852160 |
| 007-combined-0001 | full | 2927.887513309979 | 1 | integrity_or_scientific | 35203231744 | 34917076992 |
| 007-reduction-0001 | short | 3.0351945370202884 | 2 | incomplete_reduction | 20848640 | 9621504 |

Continuation: **6 full / 2 short / 7358.471498611994 seconds**. Original: **0 full / 3 short / 308.8221942020173 seconds**. Combined 007: **6 full / 5 short / 7667.293692814012 seconds**. Closed accounting has no unresolved starts. Actual limits/usage and every operational incident are retained; no arbitrary application ceiling was assigned. Memory maxima come from 15-second OS sampling and may omit a higher peak after the final sample.

```json
{
  "individual_audits": {},
  "integration_software": [],
  "neutrality_repeatability": [],
  "persistence_replay_observation": [
    {
      "attempt": "007-combined",
      "category": "persistence_replay_observation",
      "classification": "integrity_or_scientific",
      "reason": "inherited capture checks failed",
      "type": "ValueError"
    }
  ],
  "refinements": {
    "combined": [
      "outlet",
      "liquid_profiles",
      "front",
      "arrival",
      "activation",
      "grain_profiles",
      "grain_histories",
      "cup",
      "liquid_inventory",
      "fines_inventory",
      "boulder_inventory"
    ]
  },
  "resources_execution": [
    "007-combined: EXECUTION_INCOMPLETE"
  ],
  "source_environment_rights": []
}
```

005 remains incomplete/inlet-blocked, 7 full / 21 short / 727.042119908976 seconds. 006 retains conclusion A, 1 full / 2 short / 166.21631713100942 seconds. Historical corruption remains unresolved. No production-versus-004 comparison, continuum extrapolation, inter-backend agreement, publication rescore, physical validation, adoption or production-default change is established. PR #329 remains draft/unmerged, auto-merge disabled, issue #67 open; EWP/lock unchanged.
