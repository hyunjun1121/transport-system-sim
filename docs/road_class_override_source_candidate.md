# Road Class Override Source Candidate

Road-class override source-candidate packet only; not a reviewed override table, not source-backed speed or capacity evidence, not calibrated disruption evidence, not proof that overrides were applied, and not publication, final-study, or formal acceptance evidence. The packet can support reviewer triage only.

## Verdict

- Publication ready: `false`
- Final study ready: `false`
- Formal acceptance evidence: `false`
- Formal target written: `false`
- Rows: 10
- Formal target path: `data/parameters/road_class_overrides.csv`

## Candidate Rows

| Highway | Priority | Current speed | Current capacity | Current base p_fail | Speed source scope | Capacity source scope | Remaining need |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| residential | high | 30 | 400 | 0.04 | Candidate is consistent with urban residential/local 30 km/h safety speed framing, but still needs road-class mapping review. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| tertiary | high | 40 | 800 | 0.03 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| secondary | high | 50 | 1000 | 0.025 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| primary | high | 60 | 1400 | 0.02 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| trunk | medium | 80 | 1800 | 0.015 | Candidate is bounded by motorway/controlled-access speed-limit rules, but exact free-flow speed still needs facility review. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm controlled-access class mapping, lane count, heavy-vehicle adjustment, and disruption source before formal override use. |
| trunk_link | medium | 50 | 1000 | 0.025 | Candidate is bounded by motorway/controlled-access speed-limit rules, but exact free-flow speed still needs facility review. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm controlled-access class mapping, lane count, heavy-vehicle adjustment, and disruption source before formal override use. |
| primary_link | medium | 45 | 800 | 0.03 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| secondary_link | medium | 40 | 700 | 0.035 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| unclassified | medium | 35 | 600 | 0.04 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |
| tertiary_link | medium | 35 | 500 | 0.04 | Candidate is bounded by Korean general-road speed-limit ranges, but exact free-flow speed remains a reviewed modeling assumption. | Screen current BPR capacity proxy against HCM-derived lane-capacity ranges; not Korean traffic-count calibration. | Confirm urban/rural context, lane count, signal/access effects, and disruption source before formal override use. |

## Source Constraints

- Speed rows use public legal speed-limit bounds as a candidate constraint, not a calibrated free-flow-speed estimate.
- Capacity rows use FHWA/HCM-derived capacity references as a proxy screen, not Korean road-class calibration.
- Base disruption probabilities remain sensitivity-only in every row.
- Do not copy this file to `data/parameters/road_class_overrides.csv` without review and accepted application evidence.
