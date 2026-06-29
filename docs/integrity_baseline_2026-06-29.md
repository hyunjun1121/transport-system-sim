# integrity_baseline_2026-06-29 — results provenance ledger

> Phase 0.7 deliverable. A sha256 snapshot of the result CSVs present in the repo
> **as of 2026-06-29**, before the Phase-6 full rerun. This is a **provenance record
> only** — not acceptance evidence, not calibrated results, not a reproduction of the
> submitted planning-doc figures. `final_study_ready = false`.

## 1. Purpose

Record what result artifacts exist NOW so that, after the defect-free rebuild +
Phase-6 rerun, the superseded set is identifiable and checksummed. Every file below
carries `claim_scope = engineering-only / quasi-real decision-support` (see each
manifest's `claim_scope`). None is publication, operational, or final-study evidence.

## 2. Ledger (sha256, computed locally 2026-06-29)

| Path | Bytes | Rows | sha256 |
|---|---|---|---|
| `results/goseong_pilot/pilot_sample_results.csv` | 21,659 | 32 | `1c63581b1a1327261affa512e4098a5f7c76650298c00ec12fd31806bd95f3e7` |
| `results/goseong_pilot/pilot_sample_summary.csv` | 6,124 | 16 | `bf39274311a59abb825ba612b2dd48c26f4136123ca1469d72dd94b11f4e915c` |
| `results/realworld_pilot/pilot_full_results.csv` | 12,725,731 | 15,870 | `beb6aca8021d2e44a65d8fab346eaa16b902095ba61fd68b534ff79f17231901` |
| `results/realworld_pilot/pilot_full_summary.csv` | 244,176 | 529 | `05943092b646a8d9af5b41a8ae3e24d3ef6e1e80a35a6ec55d1d5b303b8e4aa2` |
| `results/realworld_pilot/pilot_multi_corridor_full_results.csv` | 2,217,854 | 1,890 | `bc3468737d49dd74ae046c6fbaeb144ddabd20e6998f3703c58c12dab168a750` |
| `results/realworld_pilot/pilot_multi_corridor_full_summary.csv` | 45,310 | 63 | `4f524bbeb29be7910a8e2fb72d4819bb5e0ac595b7be5c0605985964d55be543` |
| `results/realworld_pilot/pilot_full_graph_results.csv` | 16,667,780 | 15,870 | `4532056ff757eb34c2bc934ede12c87caa23e8950ecee016e71eb9211b21aa5f` |
| `results/realworld_pilot/morris_results.csv` | 33,578,149 | 37,536 | `d0adc4da36c9e7e342b4ddee6a75ac948ef0ef7e3554e505c8eeee842ea40f16` |
| `results/phase1_results.csv` | 4,130,920 | 8,400 | `7795817546d8bcc4f3dffb1e3edfacc8d93485778131987084cf85e2e6c6a38b` |
| `results/phase2_results.csv` | 397,096 | 840 | `dce63b84c04a632a49f56858832e5064350ef68e97a3c8b861c260992f184454` |

Row counts are data rows (header excluded). Manifests and per-run
`*_output_lock_receipt.json` accompany each results CSV in-tree.

## 3. Canonical path roles

Two result trees exist; they come from **different runner invocations**, not
newer/older versions of the same run:

- **`results/goseong_pilot/`** — output of `scripts/run_pilot_experiments.py
  --sample --region ...goseong_mobilization.yaml` (the CLAUDE.md-documented Goseong
  case-study command). The `--sample` profile = 4×4×2 = **32 rows** (smoke scale).
  `--staged` / `--full` / `--multi-corridor` / `--full-graph` write larger profiles
  here under the same dir. **This is the intended case-study output path.**
- **`results/realworld_pilot/`** — output of the broader realworld pilot runner.
  Holds `pilot_full_results.csv` (23 policy × 23 scenario × 30 seed = **15,870**),
  the `full_graph` variant (15,870), `multi_corridor_full` (**1,890** = 7×9×30),
  Morris sensitivity (37,536), and legacy `sample`/`staged` profiles.
- **`results/phase1_*.csv`, `phase2_*.csv`** — legacy **abstract-network** (H/A/S/R/D)
  experiment, not the OSM/Goseong real-world pipeline. Kept for historical
  continuity; superseded by the real-world pilot for the case study.

## 4. Reproducibility of the submitted planning-doc figures (84 / 52 / 36 %)

The planning-doc design is **7 policy × 9 scenario × 30 seed = 1,890 rows** — which
matches `pilot_multi_corridor_full_results.csv` (1,890). However that CSV reports
`censored_count = 0` throughout, so it does **not** reproduce the 84 / 52 / 36 %
completion figures (those were a post-hoc 5 h-deadline view on the reset-prior
codebase). See `docs/deadline_mechanism.md` §5: the planning-doc numbers are
**superseded, not chased**; the rebuild regenerates an authoritative
completion-vs-deadline curve. No current CSV is acceptance evidence.

## 5. Schema note (post-0.2)

Future Phase-6 reruns write a new `seed_stream_id` column (`RESULT_COLUMNS`,
proven by `tests/test_realworld_crn_seed_stream.py`). The CSVs above predate that
column, so they are schema-stale relative to current code. The Phase-6 rerun
regenerates them with the new column; this ledger fixes the pre-rerun state.

## 6. Deferred: the "archive 32-row scaffold" move — NOT performed (needs user)

`high_level_plan.md` Phase 0 listed moving `results/goseong_pilot/` to
`results/_archived_smoke/`. **Not performed**, three reasons:

1. `results/goseong_pilot/` is the **CLAUDE.md-documented** case-study output path
   (`--output-dir results/goseong_pilot`) and is referenced in `config.yaml:154`.
   Moving it breaks the documented run command.
2. The tree is **git-tracked** (143 files under `results/`); a move churns tracked
   files into a large rename diff.
3. This work did **not create** that tree, and the codebase's own docs treat it as
   canonical — so the "misleading scaffold" premise is contested. Per
   look-before-destruct: surface rather than move.

**Decision needed (user):** is `results/goseong_pilot/` (a) the canonical
case-study path to KEEP (regenerate in place at Phase 6), or (b) legacy to archive
to `results/_archived_smoke/` (requires updating CLAUDE.md + config.yaml refs)?

## 7. `INTEGRITY_BASELINE` git tag — prepared, not applied

The tag `INTEGRITY_BASELINE` would mark this provenance snapshot in git history.
**Not applied** — per project convention, tags/commits only on explicit user
request. Prepared; applies on explicit request.

## 8. 0.7 exit

- [x] sha256 ledger of canonical result CSVs (above)
- [x] canonical path roles documented (goseong_pilot vs realworld_pilot vs legacy)
- [x] planning-doc reproducibility gap recorded (1,890 CSV ≠ figures; superseded)
- [x] schema-stale note (seed_stream_id column arrives at Phase 6)
- [ ] scaffold-move decision: **deferred to user** (§6)
- [ ] `INTEGRITY_BASELINE` tag: **prepared, pending user** (§7)

**0.7 status: provenance recorded; two sub-items held for user decision (move +
tag), neither blocking G1–G7.**
