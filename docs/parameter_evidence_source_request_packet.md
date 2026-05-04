# Parameter Evidence Source-Request Packet

This note documents
`data/parameters/parameter_evidence_source_request_packet.csv` and
`data/parameters/parameter_evidence_source_request_manifest.json`.

The packet does not contain reviewed parameter evidence. It names the source
inputs required before cross-cutting demand, fleet, dispatch, transfer,
disruption-scenario, and traffic/BPR assumptions can be strengthened.

## Scope

The packet records six request rows:

- demand, arrival-process, time-horizon, and censoring-penalty evidence,
- fleet size and vehicle-capacity evidence,
- dispatch interval and turnaround evidence,
- transfer-delay evidence,
- disruption probability, capacity-reduction, blockage-rule, and scenario-rule
  evidence,
- background-traffic, traffic rolling-window, and BPR calibration evidence.

Road-class speed/capacity override collection remains in the road evidence
source-request packet. Rail timing and capacity collection remains in the rail
timing source-request packet. This packet covers the cross-cutting parameter
gaps that remain visible in the 29-row parameter evidence review packet.

## Regeneration

```powershell
.\.venv\Scripts\python scripts\write_parameter_evidence_source_request_packet.py
```

Expected outputs:

- `data/parameters/parameter_evidence_source_request_packet.csv`
- `data/parameters/parameter_evidence_source_request_manifest.json`

The manifest should keep `publication_ready: false` because this packet is a
source-request worksheet, not evidence and not accepted calibration.

## Review Use

Use this packet before editing `data/parameters/parameter_sources.csv` or
`data/parameters/fleet_assumptions.csv` for stronger final-study claims. Each
row states:

- which parameters and evidence fields the source can support,
- which external source, reviewed file, or reviewer decision is required,
- which current artifact or diagnostic can help the review,
- which command or review step should be run next,
- why the row does not close a parameter-evidence or acceptance gate.

Do not use the packet as proof that current demand, fleet, dispatch, transfer,
disruption, background-traffic, or BPR assumptions are calibrated.
