# Recovery Test Ladder Results - 2026-06-02

## Scope

This is a minimal current-state smoke check after the workspace was restored and
after `plan.md` was replaced with the recovery plan. It does not test missing
untracked work such as `transport_simulation_core/` or the event-transport
contest folder, because those paths are currently absent.

## Commands Run

### `py -3 tests\test_config.py`

Result: pass.

Observed checks:

- operational namespaces exist;
- failure-rate levels are multipliers;
- network variants are declared and routable;
- failure sensitivity levels are explicit;
- legacy keys remain available;
- operational values are in valid ranges.

### `py -3 tests\test_scenario.py`

Result: pass.

Observed checks:

- origin schedule defaults;
- explicit first departures;
- strict/grace dispatch behavior;
- fleet overlap and bottleneck behavior;
- fixed-headway rail behavior;
- finite last-mile fleet behavior;
- censoring and penalized KPI exposure.

### `py -3 main.py --test`

Result: pass.

Observed output:

- built the abstract seven-node test network;
- bus-only scenario completed 1,000/1,000 passengers;
- multimodal scenario completed 1,000/1,000 passengers;
- bus-only completion rate: `1.0`;
- multimodal completion rate: `1.0`;
- bus-only penalized makespan: `645.029769019392`;
- multimodal penalized makespan: `675.0291392474074`;
- reported delta makespan: `-30.00 min`.

## Interpretation

The restored Git-tracked core at the repository root is executable for narrow
abstract-network smoke tests. This does not prove recovery of recent untracked
real-world/event-transport work. It only supports that the committed baseline
can still run.

## Remaining Test Gaps

- No test has been run for `transport_simulation_core/`, because that directory
  is currently absent.
- No test has been run for the event-transport contest pipeline, because that
  folder, scripts, results, and figures are currently absent.
- No full experiment should be run until missing scripts and inputs are
  reconstructed or intentionally abandoned.
