# Reconstruction Decision Register - 2026-06-02

## Purpose

This register converts the recovery audit into executable decisions. It is not
a claim that missing artifacts have been recovered. It defines what can be used,
what must not be trusted, and what should be regenerated only after scripts and
inputs are verified.

## Decisions

| Area | State | Decision | Next action |
| --- | --- | --- | --- |
| Current root simulation code | Present, integrity-audited, and narrow smoke-tested | Treat the repository root as the authoritative simulation core | Do not duplicate the repository into `transport_simulation_core/` |
| `transport_simulation_core/` folder | Missing as an exact folder path | Treat as layout loss, not proof of total code loss | Restore only specific non-equivalent files if they remain required |
| Compact non-arrival scripts/tests | Six script/test paths are missing without root equivalents | Reimplement tests-first only if this scope is still needed | Search session content first; otherwise write new tests and scripts from current requirements |
| Old `gate2_20260601_232844` outputs | Generated artifacts are missing | Do not reconstruct from filenames | Regenerate only after inputs, scripts, and scope are verified |
| Event transport contest folder | Missing from current repo | Treat as not recovered | If still needed, rebuild and rerun; if submitted or abandoned, leave unavailable |
| `C:\project\contest*` candidates | Present, but targeted searches did not find the missing event-transport target files | Do not copy into this repo | Preserve as unrelated external candidate evidence only |
| `results/realworld` and `results/ai_analysis` | Missing | Treat old outputs as unavailable | Regenerate from verified scripts only |
| Rail schema docs | Present after replacement-character fixes | Keep the fixes | Include in the recovery commit |
| `docs/recovery/` artifacts | Present and untracked | Preserve as recovery evidence | Commit or archive before further reconstruction |

## Rationale

The prior `transport_simulation_core/` path list from session logs mostly maps
to files that already exist at the repository root. Bulk-recreating that folder
would create a second source of truth and increase recovery risk. The safer
path is to keep the current root repository authoritative and rebuild only
files that have no root equivalent.

The event-transport contest artifacts are different. Session logs show that
the paths existed, but the current filesystem and candidate searches do not
provide the file contents. Those outputs cannot be cited as current evidence.
They must be regenerated from verified scripts if the work is still needed.

## Immediate Execution Rule

Before any new full experiment:

1. Confirm the required scripts and inputs exist.
2. Run a compact profile.
3. Run the audit script for that profile.
4. Generate figures from audited outputs.
5. Record commands, checksums, and row counts.
6. Only then treat the regenerated outputs as usable evidence.
