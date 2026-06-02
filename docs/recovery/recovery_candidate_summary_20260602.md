# Recovery Candidate Summary - 2026-06-02

## Filesystem candidates

- `C:\tss99a63fe6`: exists, old 2026-05-08 copy; no high-risk path-name matches found in targeted search.
- `C:\tsscc`: exists but contains zero files.
- `C:\tsssrc40469350`: exists, old 2026-05-08 copy; no high-risk path-name matches found in targeted search.
- Recent `Temp\transport_system_*` directories are mostly May 9-16 clean-checkout/source-smoke folders; targeted search found no high-risk path-name matches.
- `C:\project\contest_clean_20260602`, `C:\project\contest_fresh_recovery_20260602`, and `C:\project\contest_recovery`: present, but targeted `rg --files` searches found no `철도`, `물류`, `교통`, `event_transport`, `event_realworld`, `arrival_guarantee`, or `route_context` files matching the missing event-transport target set.
- `C:\project\contest`: present and not a junction. Targeted search found a separate 부산 public-data contest project and general transport/open-data files, but did not find the missing rail/logistics event-transport folder or target files from this repository.

## Log candidates

- Codex session log `rollout-2026-06-02T03-05-57-019e845d-250e-7461-be51-873cb0dfaae4.jsonl` contains a prior `rg --files` output listing the event transport folder, scripts, results, AI analysis, figures, and `transport_simulation_core` paths.
- This proves those paths existed in a prior workspace listing, but the log alone is not a usable file-content backup.

## Recovery implication

- The best current evidence says recent missing work was untracked local work.
- No direct filesystem backup copy of the newest missing event-transport artifacts has been found yet.
- If no further candidate is found, the missing scripts/results/figures must be reconstructed from logs and regenerated from verified code.
- The `C:\project\contest*` directories should not be copied into this repository as recovery sources unless a later targeted inspection finds exact missing files.
