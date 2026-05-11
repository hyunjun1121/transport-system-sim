# Doc Cleanup Status (2026-05-11)

## Applied

- Moved `docs/doc_cleanup_consolidation_plan.md` out of root and archived it as
  `docs/archive/2026-05-11/consolidation/doc_cleanup_consolidation_plan.md` after it
  became a historical record.
- Confirmed schema docs are consolidated under `docs/schemas/`.
- Confirmed packet hub is centralized in `docs/review_packets/README.md`.

## Retention rule

- Keep active review and runbook files in root `docs/` only when they are required
  by audit scripts, manifest checks, or current operational guidance.
- Move historical planning artifacts to `docs/archive/*` so we keep traceability without
  expanding root-level `docs` noise.

## Current check result

- A dependency scan (`doc_cleanup_reference_check_20260511.md`) shows no obvious
  additional root `docs/*.md` files that are unreferenced by active code/tests and
  can be safely removed immediately.
