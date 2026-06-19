import sys, os
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.final_audit_decision_packet import build_final_audit_decision_rows
rows = build_final_audit_decision_rows()
by_id = {r['decision_id']: r for r in rows}
print(f'count: {len(rows)}')
for did, r in sorted(by_id.items()):
    print(f"  {did}: status={r['decision_status']}")
