# Final Audit Acceptance Schema

## Purpose

`data/manifests/final_audit_acceptance.json` is the explicit independent review
record that can close the final-study audit gate.

The final audit must be a prompt-to-artifact completion review. It cannot rely
on proxy signals such as passing tests, generated manifests, or substantial
implementation effort unless those artifacts cover every explicit requirement
in `plan.md`.

Do not create this file to make audits pass. Create it only after all pre-final
gates are genuinely ready and an independent audit has verified the evidence.

## Location

```text
data/manifests/final_audit_acceptance.json
```

The current scaffold intentionally does not include this file.

## Required Fields

| Field | Type | Requirement |
| --- | --- | --- |
| `region_id` | string | Non-empty pilot region identifier. |
| `accepted` | boolean | Must be `true` only after review. |
| `accepted_by` | string | Reviewer, group, or decision record identifier. |
| `accepted_date` | string | Review date in `YYYY-MM-DD` form where possible. |
| `final_study_ready` | boolean | Must be `true` only when every pre-final gate is ready. |
| `prompt_to_artifact_checklist_reviewed` | boolean | Must be `true` after explicit requirement-to-artifact review. |
| `all_gate_evidence_reviewed` | boolean | Must be `true` after every gate's evidence is inspected. |
| `no_proxy_completion_reviewed` | boolean | Must be `true` after proxy-only completion claims are rejected. |
| `expected_gate_count` | integer | Positive count matching the current pre-final gate count. |
| `reviewed_gate_ids` | array of strings | Must match the current pre-final gate IDs. |
| `ready_gate_ids` | array of strings | Must match the current ready pre-final gate IDs. |
| `blocked_gate_ids` | array of strings | Must be empty for final readiness and match current blocked pre-final gates when checked. |
| `claim_boundary` | string | Must include `not operational`. |
| `evidence_paths` | array of strings | Non-empty list of reviewed audit notes, readiness outputs, manifests, or reproduction records. |

## Example Shape

```json
{
  "region_id": "songpa_public_demo",
  "accepted": true,
  "accepted_by": "review record id",
  "accepted_date": "2026-05-04",
  "final_study_ready": true,
  "prompt_to_artifact_checklist_reviewed": true,
  "all_gate_evidence_reviewed": true,
  "no_proxy_completion_reviewed": true,
  "expected_gate_count": 14,
  "reviewed_gate_ids": [
    "pilot_region_accepted",
    "cached_osm_input"
  ],
  "ready_gate_ids": [
    "pilot_region_accepted",
    "cached_osm_input"
  ],
  "blocked_gate_ids": [],
  "claim_boundary": "Accepted for quasi-real decision-support analysis; not operational routing.",
  "evidence_paths": [
    "docs/final_study_audit.md",
    "data/manifests/final_audit_acceptance.json"
  ]
}
```

The short gate lists above are illustrative only. A real record must match the
current full pre-final gate list emitted by `scripts/audit_final_study_readiness.py`.

## Validation

The schema is enforced by:

```powershell
.\.venv\Scripts\python tests\test_realworld_final_audit_acceptance.py
.\.venv\Scripts\python tests\test_realworld_final_study_readiness.py
.\.venv\Scripts\python scripts\audit_final_study_readiness.py
```

The final-study readiness audit compares the accepted gate lists and counts
against the current pre-final gates. A stale or mismatched acceptance record
must keep the final-audit gate blocked.
