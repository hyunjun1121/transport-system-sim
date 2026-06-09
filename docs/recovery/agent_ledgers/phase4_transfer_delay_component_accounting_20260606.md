# Phase 4 Transfer Delay Component Accounting

## Scope

This sprint adds component-level accounting for transfer-delay assumptions in
the core transfer helper. It does not change the existing fixed plus
per-passenger transfer-delay total, does not regenerate transfer review packet
rows, does not provide observed station transfer timing, and does not close
transfer, parameter, publication, formal acceptance, or final-study gates.

## Code Changes

- `src/transfers.py`
  - added `TransferDelayComponent` for named fixed or per-passenger delay
    components with source-class labels.
  - added `TransferDelayBreakdown` for component delay totals, component delay
    mapping, and source-class summaries.
  - added `default_transfer_delay_components()` to expose the existing two-term
    model as auditable components.
  - added `compute_transfer_delay_breakdown()` and
    `TransferDelayConfig.breakdown_for()`.
- `tests/test_transfers.py`
  - added checks that component accounting preserves the scalar total, exposes
    source classes, and rejects invalid component inputs.

## Tests And Checks

| Command | Result | Boundary |
| --- | --- | --- |
| `.\.venv\Scripts\python tests\test_transfers.py` | passed | Confirms scalar behavior is unchanged and component accounting is valid. |
| `.\.venv\Scripts\python -m py_compile src\transfers.py tests\test_transfers.py` | passed | Syntax check only. |

## Residual Blockers

- `data/parameters/transfer_evidence_review_packet.csv` still records current
  transfer evidence as review support only.
- Station-layout, observed transfer, or pedestrian-flow source evidence remains
  absent.
- `data/parameters/parameter_acceptance.csv` remains absent.
- Transfer component accounting is implementation support, not calibration or
  reviewer signoff.
