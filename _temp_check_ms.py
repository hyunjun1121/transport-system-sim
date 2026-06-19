import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.manuscript_report_decision_packet import build_manuscript_report_decision_rows
rows = build_manuscript_report_decision_rows()
by_id = {r['decision_id']: r for r in rows}
print(f'count: {len(rows)}')
print(f'can_support values: {set(r["can_support_manuscript_acceptance"] for r in rows)}')
for did, r in sorted(by_id.items()):
    print(f"  {did}: status={r['decision_status']}")
