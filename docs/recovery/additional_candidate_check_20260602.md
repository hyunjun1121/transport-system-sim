# Additional Candidate Check - 2026-06-02

## Scope

After the first recovery pass, additional `C:\project\contest*` directories
were visible outside the current repository. These were inspected as possible
sources for the missing event-transport contest artifacts.

## Candidate Directories

- `C:\project\contest`
- `C:\project\contest_recovery`
- `C:\project\contest_fresh_recovery_20260602`
- `C:\project\contest_clean_20260602`
- `C:\project\contest_recovery_backup`

## Commands and Findings

### Directory structure check

PowerShell/.NET enumeration showed:

- `C:\project\contest_recovery` contains `contest-clean`.
- `C:\project\contest_fresh_recovery_20260602` and
  `C:\project\contest_clean_20260602` contain separate public-contest folders.
- `C:\project\contest_recovery_backup` contains
  `kaist_ai_failure_20260602_001`.
- `C:\project\contest` is a normal directory, not a junction.

### Targeted file-name search

Targeted searches were run for:

- `철도`
- `물류`
- `교통`
- `event_transport`
- `event_realworld`
- `arrival_guarantee`
- `route_context`
- `BTS`
- `부산`

The searches found a separate 부산 public-data contest project and general
transport/open-data files under `C:\project\contest`, but they did not find the
missing target folder:

```text
국방AI_활용_아이디어_경연대회\2026 철도·교통·물류 대국민 아이디어 공모
```

They also did not find the missing target files:

```text
철도물류_이벤트수송_최종본.txt
run_event_realworld_simulation.py
make_event_realworld_figures.py
event_transport_summary.csv
event_route_context_map.png
event_arrival_guarantee_heatmap.png
event_ai_risk_or_bottleneck.png
```

## Decision

The `C:\project\contest*` directories are not direct recovery sources for the
missing event-transport artifacts from this repository. Do not copy them into
`C:\project\transport-system-sim`.
