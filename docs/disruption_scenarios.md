# Disruption Scenario Library

Phase 6 disruption scenario library only; deterministic scenario-design metadata for decision-support stress testing, not observed disaster data, not calibrated disruption probabilities, not dynamic recovery modeling, not an operational route plan, not publication readiness, not final-study readiness, and not formal acceptance.

## Verdict

- Publication ready: `false`
- Final-study ready: `false`
- Row count: `22`
- Family counts: `{'access_road': 3, 'critical_link': 1, 'last_mile': 1, 'rail_service': 8, 'rail_station_access': 1, 'random': 2, 'spatial_hazard_overlay': 6}`
- Temporal scope counts: `{'metadata_only_not_dynamic_recovery': 22}`

## Family Checksums

- `access_road`: `153fc027985b1391fa865c3cada684494c9345827937075188addd30f3beec27`
- `critical_link`: `85920167e4f80fdf15c452ebf5beaaf834412cc3c6a5252891d15e5584669ce0`
- `last_mile`: `e134221ae30fe5f5e3a581e109e2f60ee55ca152ff75609328fb4898a091dd68`
- `rail_service`: `7237bf3978c48111f7fceba05df2c27388d2fa7c5f1005237e784f6d1b9650e4`
- `rail_station_access`: `1bb2b90b335d65850bc5926de07e43eb0a001f1d5122aa2c4d8c7a1609d64831`
- `random`: `5e690a7f5d085c1c1e5f744a18bbf2f7e44a9a0cd4148839cea30780d2d7d683`
- `spatial_hazard_overlay`: `e0bf801017bb6fb34e94ee4a330f2a5d8ad28512a5b6072fd845cd2785af449f`

## Selected Edge Summary

- `songpa_access_origin_to_destination`: 46 selected edges; checksum `b62ba3a315c31c9169ed8294b25cef7742d433734f143a9863ebe5b959f513d6`.
- `songpa_access_origin_to_station`: 60 selected edges; checksum `fffd83d2a1a0888097f977cb88d3239c7c10689bd205bc34174b325da653aa5f`.
- `songpa_combo_access_rail_capacity`: 46 selected edges; checksum `b62ba3a315c31c9169ed8294b25cef7742d433734f143a9863ebe5b959f513d6`.
- `songpa_combo_tancheon_rail_delay`: 6 selected edges; checksum `11e235509acf2db980da425965e35cbf09fd52da3ffc859baf24ab56d802ea8f`.
- `songpa_critical_link_blockage`: 3 selected edges; checksum `27c73810120b5384d88fd110233d4ebc9aea36ebb9a287dc788c5250ca6089b8`.
- `songpa_last_mile_station_to_destination`: 21 selected edges; checksum `2076e91e0fc975322ad73a5baddcef4744df14e68611b1618e15f4a3e4612b8a`.
- `songpa_rail_capacity_reduction`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_combined_stress`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_combined_stress_mild`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_combined_stress_severe`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_delay`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_delay_mild`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_delay_severe`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_rail_station_access`: 6 selected edges; checksum `16ff7bfec87493bbb0e571e1bb126b852bfb113f9c91f33c2cf55a9ce39648e1`.
- `songpa_rail_unavailable`: 0 selected edges; checksum `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
- `songpa_random_blockage`: 8 selected edges; checksum `87809ccacf20eb6a9ddb848e8c805c2222e91693efc967c35dfc4e2e36463303`.
- `songpa_random_capacity_reduction`: 8 selected edges; checksum `19eb223eac5508b38d80daa09348855dff47505aeda0a44d8a7ea59f74416b78`.
- `songpa_spatial_assembly_egress`: 6 selected edges; checksum `6b72e4344bd6b83845ccad936978a0536cc587b4758fdf7c36c0b198c026f301`.
- `songpa_spatial_feeder_east`: 3 selected edges; checksum `75c223a8b5216ec73145390e6aa26d3325eb2bf36a3d40a5086263d9e4b252cd`.
- `songpa_spatial_lastmile_west`: 7 selected edges; checksum `ffb08424615babca43d27b26e9ef8894567e3707e012d12800f24311f39fcf9d`.
- `songpa_spatial_tancheon_corridor`: 6 selected edges; checksum `11e235509acf2db980da425965e35cbf09fd52da3ffc859baf24ab56d802ea8f`.
- `songpa_transfer_point_blockage`: 4 selected edges; checksum `729cb546acbf76c30445cf6d9cf7276ceafbdb1dc273460b46730f6b14c31666`.

## Remaining Blockers

- scenario rows are not observed disaster or incident data
- duration and recovery columns are metadata only and are not dynamically applied by the scenario runner
- rail-headway disruption and multi-hazard composition are not first-class runtime disruption components
- formal parameter and final-study acceptance remain absent
