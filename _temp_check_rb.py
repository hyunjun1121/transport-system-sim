import sys, os, json
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.rail_bounded_treatment_audit import build_rail_bounded_treatment_audit
audit = build_rail_bounded_treatment_audit()
written = json.load(open('data/rail/rail_bounded_treatment_audit.json'))
# Compare top-level keys
print('=== Top-level diffs ===')
for k in written:
    if k == 'results':
        continue
    if k not in audit:
        print(f"  '{k}' only in written")
    elif written[k] != audit[k]:
        print(f"  '{k}': written={written[k]!r} vs audit={audit[k]!r}")
for k in audit:
    if k not in written:
        print(f"  '{k}' only in audit")

print(f'\n=== Results counts ===')
print(f"written results: {len(written['results'])}")
print(f"audit results: {len(audit['results'])}")

if len(written['results']) == len(audit['results']):
    for i in range(len(written['results'])):
        w = written['results'][i]
        a = audit['results'][i]
        if w != a:
            print(f"diff at index {i}:")
            for k in set(list(w.keys()) + list(a.keys())):
                if w.get(k) != a.get(k):
                    print(f"  {k}: w={w.get(k)} a={a.get(k)}")
