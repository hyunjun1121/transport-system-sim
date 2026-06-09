# Disruption Scenario Library

Phase 6 disruption scenario library only; deterministic scenario-design metadata for decision-support stress testing, not observed disaster data, not calibrated disruption probabilities, not dynamic recovery modeling, not an operational route plan, not publication readiness, not final-study readiness, and not formal acceptance.

## Verdict

- Publication ready: `false`
- Final-study ready: `false`
- Row count: `8`
- Family counts: `{'access_road': 2, 'critical_link': 1, 'last_mile': 1, 'rail_station_access': 1, 'random': 2, 'spatial_hazard_overlay': 1}`
- Temporal scope counts: `{'metadata_only_not_dynamic_recovery': 8}`

## Family Checksums

- `access_road`: `98eeda03c69e4e8e7ee3cf33c41c8b2d52a304b3942c276fcc19e4d5b11fd771`
- `critical_link`: `8de6a17b8737d957fe22e5211ceb0a98ffe754002d953bfe408eac1dbe4c1ab3`
- `last_mile`: `c261fde7e109f4a7590c9c5161678e5232dba46827883e2226fca4e9cb604b76`
- `rail_station_access`: `efaaa0591109ef544a1ff3d8096e0ceb2c625e899d73d9c66a301cd4874e118a`
- `random`: `9280c985a11b1b11d3c38113418d20eed52ff2789e099b58d9eab48cd1fa7456`
- `spatial_hazard_overlay`: `d44f5b66a0a5090f562a03f76a219af08aa5078d9e1bf8b9ae6c6edabdf9a625`

## Selected Edge Summary

- `songpa_access_origin_to_destination`: 46 selected edges; checksum `b62ba3a315c31c9169ed8294b25cef7742d433734f143a9863ebe5b959f513d6`.
- `songpa_access_origin_to_station`: 60 selected edges; checksum `fffd83d2a1a0888097f977cb88d3239c7c10689bd205bc34174b325da653aa5f`.
- `songpa_critical_link_blockage`: 3 selected edges; checksum `27c73810120b5384d88fd110233d4ebc9aea36ebb9a287dc788c5250ca6089b8`.
- `songpa_last_mile_station_to_destination`: 21 selected edges; checksum `2076e91e0fc975322ad73a5baddcef4744df14e68611b1618e15f4a3e4612b8a`.
- `songpa_rail_station_access`: 6 selected edges; checksum `16ff7bfec87493bbb0e571e1bb126b852bfb113f9c91f33c2cf55a9ce39648e1`.
- `songpa_random_blockage`: 2 selected edges; checksum `f98ccab1208d761d9e03cb04e6caa408003acbd26ba5253bb277d6941d4a89f3`.
- `songpa_random_capacity_reduction`: 4 selected edges; checksum `8089d802f9a45bc3339dde4762417387d7bc453d35abe5dd7916e3defd9b5511`.
- `songpa_spatial_tancheon_corridor`: 6 selected edges; checksum `11e235509acf2db980da425965e35cbf09fd52da3ffc859baf24ab56d802ea8f`.

## Remaining Blockers

- scenario rows are not observed disaster or incident data
- duration and recovery columns are metadata only and are not dynamically applied by the scenario runner
- rail-headway disruption and multi-hazard composition are not first-class runtime disruption components
- formal parameter and final-study acceptance remain absent
