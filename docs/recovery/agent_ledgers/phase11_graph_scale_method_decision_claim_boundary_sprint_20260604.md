# Phase 11 Graph-Scale Method Decision Claim-Boundary Sprint - 2026-06-04

## Objective

Reduce release-blocking lexical claim-language findings in
`docs/graph_scale_method_decision_packet.md` while preserving the graph-scale
method decision review boundary.

## Claim Boundary

This sprint is lexical claim-boundary cleanup and generated-packet alignment
only. It does not select a graph method, approve reduced-corridor use, approve
full-graph exclusion, create graph-scale acceptance, create publication
readiness, create study-closeout readiness, or create formal reviewer approval.

## Main-Thread Inspection

Inspected current blocker evidence and related owned paths:

- `data/validation/claim_language_guard_manifest.json`
- `docs/graph_scale_method_decision_packet.md`
- `src/realworld/graph_scale_method_decision_packet.py`
- `scripts/write_graph_scale_method_decision_packet.py`
- `tests/test_realworld_graph_scale_method_decision_packet.py`

Initial blocker slice for `docs/graph_scale_method_decision_packet.md`:

- `accepted` in reduced-corridor tolerance wording
- `accepted` in multi-corridor regeneration wording

## Edits

- `src/realworld/graph_scale_method_decision_packet.py`
  - replaced reduced-corridor `Accept` wording with `Retain`
  - replaced alternate-route `acceptable` wording with `review-scoped
    tolerances`
  - replaced `accepted output package` with `review-selected output package`
  - replaced accepted graph-choice/downstream wording with selected graph-choice
    wording
  - replaced `final claims` with `release-scope claims`
- regenerated:
  - `data/validation/graph_scale_method_decision_packet.csv`
  - `data/validation/graph_scale_method_decision_manifest.json`
  - `docs/graph_scale_method_decision_packet.md`

The generated packet still reports `publication_ready=false`,
`can_mark_complete=false`, `selected_graph_method_recorded=false`, and
`downstream_regeneration_decision_recorded=false`.

## Commands

| command | exit | evidence |
| --- | ---: | --- |
| `Get-Content docs\graph_scale_method_decision_packet.md` | 0 | inspected generated Markdown before editing |
| `Select-String src\realworld\graph_scale_method_decision_packet.py -Pattern 'accepted\|Accept\|accept\|final\|formal'` | 0 | located generated prose that could carry unbounded reserved terms |
| `Get-Content tests\test_realworld_graph_scale_method_decision_packet.py` | 0 | inspected touched test scope |
| `.\.venv\Scripts\python scripts\write_graph_scale_method_decision_packet.py` | 0 | regenerated graph-scale method CSV, manifest, and Markdown |
| `.\.venv\Scripts\python tests\test_realworld_graph_scale_method_decision_packet.py` | 0 | graph-scale method decision packet tests passed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py --scan-path docs\graph_scale_method_decision_packet.md --output data\validation\tmp_claim_language_guard_graph_scale_method_decision.csv --doc docs\tmp_claim_language_guard_graph_scale_method_decision.md --manifest data\validation\tmp_claim_language_guard_graph_scale_method_decision_manifest.json --fail-on-blockers` | 0 | focused guard reported 0 blocking findings for the document |
| `Remove-Item ...tmp_claim_language_guard_graph_scale_method_decision...` | 0 | temporary focused guard artifacts removed |
| `.\.venv\Scripts\python scripts\audit_claim_language.py` | 0 | full guard regenerated; blocking findings reduced from 44 to 42 |
| `.\.venv\Scripts\python tests\test_realworld_claim_language_guard.py` | 0 | claim-language guard tests passed |
| `git diff --check -- src\realworld\graph_scale_method_decision_packet.py docs\graph_scale_method_decision_packet.md data\validation\graph_scale_method_decision_packet.csv data\validation\graph_scale_method_decision_manifest.json` | 0 | whitespace check passed; CRLF warning only for the Python file |

## Results

- `docs/graph_scale_method_decision_packet.md` no longer appears in the full
  release-blocking claim-language blocker list.
- Full claim-language blocker count is now 42.
- Graph-scale method selection remains blocked for publication and
  study-closeout claims because reviewer decisions and
  `data/manifests/graph_scale_acceptance.json` remain absent.
- No phase gate or formal acceptance gate was closed.

## Remaining Blocker Direction

Next claim-language cleanup candidates include
`docs/reproducibility_decision_packet.md`,
`docs/reproducibility_review_packet.md`, `docs/rail_evidence.md`,
`docs/road_evidence_source_request_packet.md`,
`docs/source_provenance_decision_packet.md`, and related generated manifests.
