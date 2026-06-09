# Phase 8 Artifact Invalidation Matrix Ledger

## Objective

Implement Immediate Next Action 18 from `plan.md`: before Phase 9, apply an
artifact invalidation matrix so stale compact, statistics, ML, figure, report,
or review-package artifacts are regenerated, explicitly excluded, or marked
non-evidence before full-run promotion.

## Baseline Snapshot

- Command evidence captured before implementation:
  - `rg -n "Artifact Invalidation|invalidation|stale compact|stale|tracked artifact|review-package|review package|Immediate Next Actions|Before Phase 9" .\plan.md .\src .\scripts .\tests .\docs .\data`
  - `Get-ChildItem -Path .\src\realworld -Filter *artifact*`
  - `Get-ChildItem -Path .\scripts -Filter *artifact*`
  - `Get-ChildItem -Path .\tests -Filter *artifact*`
  - `git status --short --branch`
- Existing related guard inspected:
  - `src/realworld/tracked_artifact_audit.py`
  - `scripts/audit_tracked_artifacts.py`
  - `tests/test_realworld_tracked_artifact_audit.py`
  - `src/realworld/phase8_precompact_tables.py`
  - `scripts/write_phase8_precompact_tables.py`
- Baseline finding:
  - `tracked_artifact_audit` checks clean-checkout packaging risk.
  - `plan.md` Immediate Next Action 18 needs a separate stale downstream
    artifact classification guard before Phase 9.

## Dirty-Path Policy

The current worktree contains many modified and untracked paths unrelated to
this narrow task. Do not revert them. This phase owns only:

- `src/realworld/artifact_invalidation_matrix.py`
- `scripts/write_artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`
- `data/validation/artifact_invalidation_matrix.csv`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `docs/artifact_invalidation_matrix.md`
- this ledger
- narrowly required updates to `plan.md`, `agents.md`, or `status.md` if plan
  audit tests require command visibility.

## Agent Wave

Wave ID: `phase8_artifact_invalidation_explorers`

Main-thread task running in parallel:

- inspect existing audit modules and prepare the implementation scope.

Agents to spawn:

1. Artifact-audit design reviewer, GPT-5.5 xhigh, read-only.
2. Output-promotion and claim-boundary reviewer, GPT-5.5 xhigh, read-only.

Write scopes:

- none for read-only agents.

Wait barrier:

- main-thread synthesis before any implementation patch.

Missing or deferred roles:

- none planned. If agent capacity blocks a role, the main thread will either
  perform that review locally or defer it before gate closure.

## Verification Plan

Run narrow verification first:

```powershell
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --help
git diff --check -- src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py plan.md agents.md status.md
```

## Claim Boundary

This matrix is review support only. It does not regenerate stale artifacts by
itself, does not validate evidence quality, does not authorize Phase 9 full-run
promotion, and does not close publication, final-study, or formal-acceptance
gates.

## Implementation Summary

Implemented files:

- `src/realworld/artifact_invalidation_matrix.py`
- `scripts/write_artifact_invalidation_matrix.py`
- `tests/test_realworld_artifact_invalidation_matrix.py`
- `data/validation/artifact_invalidation_matrix.csv`
- `data/validation/artifact_invalidation_matrix_manifest.json`
- `docs/artifact_invalidation_matrix.md`
- `data/validation/artifact_invalidation_closeout_template.csv`
- `data/validation/artifact_invalidation_closeout_manifest.json`
- `docs/artifact_invalidation_closeout_template.md`
- `data/validation/artifact_invalidation_closeout_action_queue.csv`
- `data/validation/artifact_invalidation_closeout_action_queue_manifest.json`
- `docs/artifact_invalidation_closeout_action_queue.md`
- `data/validation/artifact_invalidation_quarantine_closeout_template.csv`
- `data/validation/artifact_invalidation_quarantine_closeout_manifest.json`
- `docs/artifact_invalidation_quarantine_closeout_template.md`
- `data/validation/artifact_invalidation_quarantine_scope_audit.csv`
- `data/validation/artifact_invalidation_quarantine_scope_audit_manifest.json`
- `docs/artifact_invalidation_quarantine_scope_audit.md`

Integrated preflight guard:

- `src/realworld/pilot_experiments.py` checks the artifact invalidation
  manifest and closeout manifest before non-sample Phase 9-style profiles.
- `scripts/run_pilot_experiments.py` exposes
  `--artifact-invalidation-manifest-path` and
  `--artifact-invalidation-closeout-manifest-path`.
- `tests/test_realworld_pilot_experiments.py` verifies that unresolved
  artifact invalidation blocks non-sample profiles while explicit
  engineering-only runs remain non-publication, non-final, non-operational,
  and non-acceptance.

Generated matrix state:

- row count: 51
- blocking row count: 51
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`

Generated closeout template state:

- row count: 51
- closed row count: 0
- pending or invalid row count: 51
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`

Generated closeout action queue state:

- row count: 51
- blocks Phase 9 rows: 51
- reviewer signoff required rows: 51
- action batches:
  - quarantine non-evidence: 6
  - upstream evidence and benchmarks: 10
  - compact outputs: 5
  - analysis outputs: 10
  - claims and packages: 20
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`

Generated quarantine closeout template state:

- source action batch: `quarantine_non_evidence`
- row count: 6
- closed row count: 0
- pending or invalid row count: 6
- included rows:
  - five stale `full_outputs` rows;
  - one `claim_boundary_or_readiness_logic->review_packages` row.
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`
- This six-row template is reviewer input only and must not be used as the
  main 51-row closeout manifest.

Generated quarantine scope/citation audit state:

- source action batch: `quarantine_non_evidence`
- expected quarantine row count: 6
- covered quarantine row count: 6
- finding row count: 793
- stale artifact candidate count: 69
- ZIP candidate count: 4
- reference hit count: 720
- unresolved current reference hit count: 677
- scan error count: 0
- `searched_scope_complete=true`
- `phase9_promotion_ready=false`
- `publication_ready=false`
- `final_study_ready=false`
- `formal_acceptance_evidence=false`
- `acceptance_ready=false`
- `must_not_be_used_as_closeout_manifest=true`
- This audit is finding-row support only. It does not provide reviewer signoff,
  does not remove references, does not close rows, and cannot clear Phase 9.

## Agent Findings Incorporated

Read-only artifact-audit reviewer findings incorporated:

- The matrix is not a duplicate `git status` or tracked-artifact audit.
- Rows are keyed by upstream change group and stale downstream group.
- Allowed dispositions are `regenerate`, `explicitly_exclude`, and
  `mark_non_evidence`.
- Statuses avoid acceptance-like wording.

Read-only output-promotion reviewer findings incorporated:

- Missing or unresolved artifact invalidation blocks non-sample Phase 9
  profiles.
- The runner manifest records the invalidation preflight state.
- Publication, final-study, formal-acceptance, and operational-use flags remain
  false.

Follow-on GPT-5.5 xhigh workflow reviewers found no blocker in the multi-agent
workflow. Their high/medium findings were incorporated by:

- making hardware and package facts explicitly preflight-refresh facts rather
  than permanent acceptance evidence;
- marking short sub-agent prompt shapes as shorthand that must be expanded
  before launch;
- clarifying that stage rosters use the stricter dependency/write-lock/test
  rule if tables drift;
- adding artifact invalidation as a Phase 9 precondition and validation command;
- recording the current 51-row/51-blocker artifact invalidation state in
  `status.md`;
- adding a future closeout-input requirement before the invalidation gate can
  stop blocking Phase 9.

Closeout schema reviewer findings incorporated:

- The closeout is a separate worksheet artifact, not a mutation of the static
  invalidation matrix.
- The closeout records row id, disposition, affected artifacts or exclusion
  scope, upstream/downstream artifact JSON, rerun/audit/test command and
  result fields, reviewer signoff, claim-boundary review result, invalidation
  gate flag, and non-acceptance flags.
- The template defaults every row to pending, unsigned, not-run, and
  non-acceptance.

Preflight/guard reviewer findings incorporated:

- `artifact_invalidation_blocks_phase9()` now fails closed if a manifest is
  hand-edited to set `phase9_promotion_ready=true` while coverage is missing or
  stale rows remain.
- A matrix that is otherwise ready still blocks if the closeout manifest is
  missing, incomplete, or pending.
- A valid closeout can only clear the invalidation blocker; it does not set
  publication readiness, final-study readiness, operational use, or formal
  acceptance.

Closeout action-queue reviewer findings incorporated:

- Pending closeout rows should be processed by dependency order rather than
  table order.
- Upstream evidence, benchmarks, compact outputs, analysis outputs, figures,
  reports, and review/readiness packages must be sequenced so downstream text
  cannot cite stale upstream artifacts.
- Full-output rows remain deferred and non-evidence until compact gates and
  Phase 9 preconditions pass.
- ML rows remain blocked until concrete producer commands and tests are
  identified from audited simulation outputs.
- The action queue is work-order guidance only; it cannot close rows, approve
  evidence, or authorize Phase 9.

Quarantine closeout reviewer findings incorporated:

- A separate six-row quarantine template is aligned with the plan if it remains
  pending, unsigned, non-acceptance reviewer input.
- Required non-closing fields remain `pending`, `not_run`, `unsigned`, or
  `false`; specifically it keeps `actual_disposition=pending`,
  `closeout_status=pending`, `rerun_result=not_run`, `audit_result=not_run`,
  `targeted_test_result=not_run`, `reviewer_signoff_status=unsigned`,
  `claim_boundary_review_result=pending`,
  `can_clear_invalidation_gate=false`, `publication_ready=false`,
  `final_study_ready=false`, and `formal_acceptance_evidence=false`.
- The quarantine manifest cannot substitute for the main closeout manifest
  because it covers only 6 of 51 invalidation rows and remains pending.

Quarantine scope/citation reviewer findings incorporated:

- Scope evidence is recorded one finding per row rather than one closeout row
  with nested JSON arrays.
- Row fields are limited to invalidation id, action batch, downstream group,
  scope id, finding type, searched glob/root, match path/detail, status, SHA256
  where applicable, suggested closeout field, and claim boundary.
- Closeout status, actual disposition, reviewer signoff, reviewed timestamp,
  gate-clearance flags, publication readiness, final-study readiness, and
  formal acceptance fields are intentionally excluded from finding rows.
- ZIP candidates are hashed and include ZIP member-count detail.
- The manifest includes fail-closed summary flags and explicitly records
  `must_not_be_used_as_closeout_manifest=true`.
- `artifact_invalidation_blocks_phase9()` now rejects a scope audit manifest if
  it is accidentally supplied as the closeout manifest.

## Verification Results

Commands run after implementation:

```powershell
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-quarantine-closeout-template
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --write-closeout-template --write-closeout-action-queue --write-quarantine-closeout-template --write-quarantine-scope-audit
.\.venv\Scripts\python -m py_compile src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py src\realworld\pilot_experiments.py scripts\run_pilot_experiments.py tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python tests\test_realworld_artifact_invalidation_matrix.py
.\.venv\Scripts\python tests\test_realworld_pilot_experiments.py
.\.venv\Scripts\python scripts\write_artifact_invalidation_matrix.py --help
.\.venv\Scripts\python scripts\run_pilot_experiments.py --help
.\.venv\Scripts\python tests\test_realworld_plan_audit.py
git diff --check -- src\realworld\artifact_invalidation_matrix.py scripts\write_artifact_invalidation_matrix.py tests\test_realworld_artifact_invalidation_matrix.py src\realworld\pilot_experiments.py scripts\run_pilot_experiments.py tests\test_realworld_pilot_experiments.py plan.md agents.md status.md data\validation\artifact_invalidation_matrix.csv data\validation\artifact_invalidation_matrix_manifest.json docs\artifact_invalidation_matrix.md
```

Observed results:

- artifact invalidation matrix tests passed, including finding-row scope audit,
  CLI write, and scope-manifest misuse rejection tests;
- pilot experiment preflight tests passed;
- plan audit test passed;
- help commands rendered expected CLI options;
- `git diff --check` reported only CRLF normalization warnings for existing
  text files.

## Remaining Blocker

The current invalidation matrix and closeout template intentionally block Phase
9 promotion. The closeout template still needs reviewer-completed regenerated,
excluded, or non-evidence dispositions, affected artifact or exclusion-scope
records, rerun/audit/test command evidence, hashes where applicable, and
non-acceptance reviewer signoff before a future matrix can stop blocking
promotion.
