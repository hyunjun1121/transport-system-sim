# Present File Integrity Audit - 2026-06-02

Generated: 2026-06-02T15:10:10

## Scope

This audit checks active project files under `C:\project\transport-system-sim`, excluding `.git`, virtual environments, caches, and `cloned_repo/` reference clones. It does not prove missing untracked work has been recovered; it only checks files that are currently present.

TypeScript `tsconfig*.json` files are parsed as JSONC because comments are valid in TypeScript config files.

## Summary Counts

- csv_checked: 262
- csv_failed: 0
- docx_checked: 5
- docx_failed: 0
- json_checked: 290
- json_failed: 0
- jsonc_checked: 2
- pdf_checked: 1
- pdf_failed: 0
- png_checked: 79
- png_failed: 0
- python_checked: 866
- python_failed: 0
- text_checked: 380
- text_failed: 0
- yaml_checked: 9
- yaml_failed: 0
- zip_checked: 3
- zip_failed: 0

## Failure Count

- total failures: 0

## Failures

No integrity failures were found within this audit scope.

## Notes

- `web_demo\tsconfig.app.json` [jsonc_parse]: valid TypeScript JSONC config; strict JSON parse skipped because comments are expected
- `web_demo\tsconfig.node.json` [jsonc_parse]: valid TypeScript JSONC config; strict JSON parse skipped because comments are expected

## Next Step

Proceed to recover or regenerate missing untracked artifacts after candidate inspection. Current present files are not showing active-scope corruption after the rail schema text fixes.