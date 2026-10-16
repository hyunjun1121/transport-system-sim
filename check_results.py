import os
d = 'results/paper_revision_top10_corridor_v4_20260721'
camps = [c for c in os.listdir(d) if os.path.isdir(os.path.join(d, c)) and not c.startswith('_')]
for camp in camps:
    smoke_dir = os.path.join(d, camp, 'smoke')
    if os.path.exists(smoke_dir):
        files = os.listdir(smoke_dir)
        print(f'{camp}: {files}')
    else:
        print(f'{camp}: MISSING smoke dir')
