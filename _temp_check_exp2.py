import csv, json
rows = list(csv.DictReader(open('data/manifests/experiment_design_decision_packet.csv')))
print(f'shipped count: {len(rows)}')
for r in rows:
    print(f"  id={r['decision_id']} status={r['decision_status']} choice={r.get('decision_choice','?')}")
manifest = json.load(open('data/manifests/experiment_design_decision_manifest.json'))
print(f'manifest blocking={manifest.get("blocking_decision_count")} human={manifest.get("human_review_decision_count")}')
