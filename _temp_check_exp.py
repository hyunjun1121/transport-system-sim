import sys, os, csv
sys.path.insert(0, 'C:\\project\\transport-system-sim')
from src.realworld.experiment_design_decision_packet import build_experiment_design_decision_rows
rows = build_experiment_design_decision_rows()
print("current rows:")
for r in rows:
    print(f"  id={r['decision_id']} status={r['decision_status']}")
shipped = list(csv.DictReader(open('data/parameters/experiment_design_decision_packet.csv')))
print("\nshipped rows:")
for r in shipped:
    print(f"  id={r['decision_id']} status={r['decision_status']}")
print(f"\ncurrent count: {len(rows)}, shipped count: {len(shipped)}")
