# Source interpretation (no hydraulic evaluation)

Public Visualizer source was inspected at
[`9ef3d0de47b438fb55a44aed80e646b1deef37d8`](https://github.com/miharekar/visualizer/tree/9ef3d0de47b438fb55a44aed80e646b1deef37d8).
Its OpenAPI version is **1.21.0**; the retained July snapshot's provenance cited
1.13.0. This is a current public source candidate, not authentication of the
deployed server revision, uploading software version or hardware.

| Field or route | What the inspected code establishes | What remains unresolved |
|---|---|---|
| `brewdata.parser` | The parser base writes its class name when saving shot information. This is software-written format provenance. | Parser identity is not machine or sensor identity. |
| Default shot response | For chart-data uploads, the serializer returns common `timeframe`/`data` fields instead of native `brewdata`. `ShotInformation.chart_data?` selects this route for non-Beanconqueror parsers. | The common arrays do not disclose which parser produced them or preserve native sensor-selection branches. |
| Beanconqueror response | Native `brewdata`, including its parser label, is returned. Preparation name supplies a profile title; it is not an authenticated hardware label. | A user preparation label cannot establish machine, sensor or controller identity. Native pressure/weight names alone do not authenticate the instrument. |
| `profile_url` and `/shots/{id}/profile?format=json` | The documented public route returns profile configuration when available. JSON structures may include steps, pump/control settings and limiter containers. | A saved configuration is not authenticated execution timing, stage assignment, inactive flow limiting or a hardware/sensor record. |
| GaggiMate common weight/flow channels | Weight selects native `v` when any sample has positive `v`, otherwise estimated `ev`. Flow independently selects `vf` when any sample has positive `vf`, otherwise estimated `pf`. | Common `espresso_weight` and `espresso_flow_weight` names cannot distinguish these branches. No branch is inferred for an unresolved upload. |
| Decent JSON | Maps native `flow.by_weight` and `flow.by_weight_raw`, totals, goals and state-change arrays to common channels; stores profile data separately. | A generic output channel does not authenticate that this parser, a connected scale or a particular state convention produced a selected record. |
| Meticulous / Gaggiuino | Maps native `gravimetric_flow` / `weightFlow` and weight channels, with source-specific setpoint/state handling. | A mapping in a public parser is not shot-specific proof of measured origin or verified hardware. |

Primary source files:
[serializer](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/shot/jsonable.rb),
[information model](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/shot_information.rb),
[parser base](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/base.rb),
[GaggiMate](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/gaggimate.rb),
[Beanconqueror](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/beanconqueror.rb),
[Decent JSON](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/decent_json.rb),
[Meticulous](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/meticulous.rb),
[Gaggiuino](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/parsers/gaggiuino.rb),
[profile export](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/app/models/shot_information/profile.rb),
and [OpenAPI](https://github.com/miharekar/visualizer/blob/9ef3d0de47b438fb55a44aed80e646b1deef37d8/openapi.yaml).

The existing Puckworks harvester preserves `brewdata.parser` in privacy-filtered
Bronze, but `_integration_source` does not promote that nested path into the
normalized integration label. Calling this “dropped from the snapshot” would be
incorrect. Conversely, `_strip_pii` deliberately removes profile titles/URLs
and user IDs; user linkage is salted. The old normalized `profile_present` flag
can prove a profile title existed before privacy stripping. A newly returned
field without that historical support is source-changed or historical-loss
UNKNOWN, not automatically a harvester defect. The old harvester did not request
the separate profile endpoint; its result is supplemental API evidence.

The probe retains allowlisted native field paths and value types, not values.
Unknown dictionary keys can themselves be user text and are not persisted.
Empty containers are structurally present; they are not proof of usable metadata.
Nulls and missing keys are counted separately. Configuration values are not used
to select shots or assign active stages. Absent, null, zero and -1 goals cannot
establish an inactive flow limiter. Source-code interpretation alone cannot
qualify a shot for #419's window comparisons.

Data source: Visualizer; collective thanks to the contributing users.
