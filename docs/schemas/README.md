# Consolidated Schema Documents

Schema and schema-like reference artifacts were moved from `docs/*.md` into
`docs/schemas/` to reduce root-level clutter and make related contracts easier
to locate.

## Files

- `experiment_acceptance_schema.md`
- `final_audit_acceptance_schema.md`
- `graph_scale_acceptance_schema.md`
- `manuscript_acceptance_schema.md`
- `parameter_acceptance_schema.md`
- `pilot_acceptance_schema.md`
- `provenance_acceptance_schema.md`
- `rail_gtfs_cache_schema.md`
- `rail_shortest_path_cache_schema.md`
- `rail_station_cache_schema.md`
- `rail_timetable_cache_schema.md`
- `reproducibility_acceptance_schema.md`
- `road_class_override_schema.md`
- `sensitivity_acceptance_schema.md`
- `validation_acceptance_schema.md`

## Update rule

All generated artifacts, plan docs, and code paths now use:
`docs/schemas/<file>.md`.

If a consumer still needs the old location for backward compatibility, use a
forwarding stub in the legacy path rather than re-creating the old file.
