# Active Recovery Scope - 2026-06-02

## Decision

The active recovery scope is the reusable transport simulation repository, not
the already-finished event contest package.

## Scope In

- Preserve and use the current repository root as the authoritative simulation
  codebase.
- Keep the recovery plan, audits, candidate search records, and baseline bundle
  under `docs/recovery/`.
- Use the rail schema corruption fixes already committed in the recovery
  baseline.
- Continue future real-world simulation work only after compact tests and
  traceable run manifests are in place.

## Scope Out Unless Explicitly Requested Again

- Rebuilding the missing event-transport contest folder.
- Recreating old event-transport figures.
- Recreating missing event-transport result tables.
- Reclaiming old event-transport claims from session-log path names.

## Rationale

The event-transport files are missing from the current repository and no direct
backup copy has been found. Session logs only prove that prior paths existed;
they do not preserve file contents or output data. Because the contest work had
already been treated as finished before the recovery work began, rebuilding it
is not the default recovery path.

The current root repository has passed the present-file integrity audit and a
minimal smoke ladder. It is therefore the safer base for continuing simulation
engineering work.

## Remaining Risk

Some old generated artifacts and compact non-arrival files remain missing. They
should be regenerated or reimplemented only when their research scope becomes
active again.
