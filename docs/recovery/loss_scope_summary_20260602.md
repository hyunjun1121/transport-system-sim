# Loss Scope Summary - 2026-06-02

Generated: 2026-06-02 14:56:09 +09:00ST

## Confirmed by current filesystem

- Current Git repository is present.
- Git object check completed successfully if `current_git_state_20260602.md` reports no fsck output.
- `transport_simulation_core/` is absent in the current workspace.
- The event transport contest folder is absent in the current workspace.
- `results/realworld/` and `results/ai_analysis/` are absent in the current workspace.
- `web_demo/` and `kci/` are present and need integrity checks before reuse.

## Current interpretation

The repository appears restored to a clean committed state, while recent uncommitted local work and generated artifacts are not present. Missing untracked work must be searched in logs, temp folders, recovery CSV reports, candidate backup directories, and downloads before it is declared unrecoverable.

## Next step

Inspect candidate recovery locations and run present-file integrity checks. Do not rerun full experiments until scripts, inputs, and output directories are verified.
