import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.parameter_review_packet import build_parameter_review_rows
rows = build_parameter_review_rows()
high = [r for r in rows if r['review_priority'] == 'high']
print(f'high count: {len(high)}')
for r in high:
    print(f"  {r['parameter']}: priority={r['review_priority']}")
print(f'medium count: {sum(1 for r in rows if r["review_priority"] == "medium")}')
print(f'low count: {sum(1 for r in rows if r["review_priority"] == "low")}')
