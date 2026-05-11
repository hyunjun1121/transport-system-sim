# KCI Implementation Plan — From Resolved Decisions to Submitted Manuscript

**Document role:** HOW. Step-by-step implementation plan that executes the research described in `kci/research_plan.md` using the file decisions in `kci/repo_assets_audit.md`, the locked decisions in `kci/agents.md` §7, and the format spec in `kci/submission_format.md`.
**Last updated:** 2026-05-11.
**Status:** Draft v0.1 — ready to execute. Per-phase decision points are flagged with `🟡 IN-PHASE DECISION`.

---

## 0. Read-first

| If you're asking… | Read |
|---|---|
| Why this study? | `research_plan.md` §1–§3 |
| What's in/out of scope? | `research_plan.md` §4 |
| What is the research design? | `research_plan.md` §6–§7 |
| What's the framing rule (military, virtual corridor, IE)? | `agents.md` §2, §6 |
| What's already locked? | `agents.md` §7 |
| Which upstream files do we reuse? | `repo_assets_audit.md` |
| What format does KCI demand? | `submission_format.md` |
| **What do I run, in what order?** | **This document.** |

---

## 1. Phase overview

| Phase | Goal | Output | Blocks next phase? |
|---|---|---|---|
| **0** | Bootstrap `kci/` directory and slim package skeleton | Working `kci/` tree, simulator imports succeed | YES |
| **1** | Build the Songpa↔양주 major-arterial corridor network | `data/cache/songpa_yangju_corridor.graphml` + region YAML | YES |
| **2** | Adapt simulator code, config, scenarios | `kci/main.py`, `config.yaml`, scenario CSVs ready to run | YES |
| **3** | Smoke runs | One paired smoke (~minutes), end-to-end validates | YES |
| **4** | Full experiment runs | Phase 1 + Phase 2 + Morris CSVs in `kci/results/` | YES |
| **5** | Analysis, CIs, figures | Tables + figures sized for the manuscript | YES |
| **6** | Manuscript draft (`.hwp` via hwpx skill) | `manuscript.hwp` in KCI 편집양식 | YES |
| **7** | Submission package | Anonymized `.hwp` + similarity report + 보안성 검토 + 저작권 동의서 + JAMS upload | END |

Each phase has prerequisites, tasks, validation gate, and rollback note.

---

## 2. Phase 0 — Bootstrap

### 2.1 Prerequisites

- `kci/agents.md`, `research_plan.md`, `repo_assets_audit.md`, `submission_format.md` present (already done as of 2026-05-11).
- Python 3.11+, `git`, network access for `osmnx` if Phase 1 needs a fresh extraction.

### 2.2 Tasks

```
1.  Create kci/ subdirectories per repo_assets_audit.md §4
    kci/{src/{experiment,visualize,realworld},data/{cache,regions,scenarios,parameters,manifests,validation},results,scripts,tests,docs,manuscript/figures}
2.  Touch __init__.py files where needed (src/, src/experiment/, src/visualize/, src/realworld/, tests/)
3.  COPY simulator-core files from upstream src/ into kci/src/ per audit §1 ("Simulator core" + "Experiment runner" + "Visualization" rows)
4.  COPY realworld subset (osm_network.py, zones.py, regions.py, types.py, validation.py)
5.  ADAPT realworld/__init__.py — write a slim init that re-exports ONLY the modules in §1 "Real-world adapter subset" with COPY/ADAPT decisions:
      from .types import RegionSpec, ZoneSpec, RailPointSpec
      from .regions import load_region
      from .zones import nearest_node, add_connectors
      from .osm_network import extract_bbox_graph, save_graphml, load_graphml, normalize
      from .attributes import HIGHWAY_DEFAULTS
      from .adapter import build_simulator_graph
      from .validation import assert_graph_ready
      from .accessibility import accessibility_loss
      from .disruption_scenarios import load_scenarios
      from .sensitivity import morris_problem, run_morris
6.  ADAPT realworld/adapter.py — change ROUTEABLE_HIGHWAY_CLASSES to:
      {"motorway", "motorway_link", "trunk", "trunk_link",
       "primary", "primary_link", "secondary", "secondary_link"}
7.  ADAPT realworld/sensitivity.py — strip imports of pilot_experiments / policy_alternatives;
    rewrite run_morris() to invoke src.scenario.run_scenario() directly with KCI configs.
8.  COPY tests per audit §2 (simulator-core + adapter / scenario / sensitivity / e2e / reproducibility)
9.  COPY 국방.md and 전시_예비군_수송체계_시뮬레이션_개념도.png into kci/manuscript/figures/
10. ADAPT requirements.txt — add osmnx, drop python-docx
11. Write kci/main.py with PROJECT_ROOT pointing at kci/
12. Write kci/README.md (light, points to research_plan.md / agents.md / submission_format.md)
```

### 2.3 Validation gate

```bash
cd kci
python -c "import sys; sys.path.insert(0, '.'); from src import scenario, network, metrics; from src.realworld import adapter, osm_network; print('imports ok')"
pytest tests/test_models.py tests/test_dispatch.py tests/test_metrics.py -q
```

Expected: imports succeed, three smoke tests pass.

### 2.4 Rollback

If imports fail (most likely the slim `realworld/__init__.py` is missing a needed re-export), revert by adding the missing symbol. **Do not** copy the upstream `__init__.py` — it eagerly loads the entire deferred-acceptance scaffold.

---

## 3. Phase 1 — Network construction

### 3.1 Prerequisites

- Phase 0 complete.
- Decision A.1 (final OSM bbox) confirmed by extraction sanity check below.

### 3.2 Tasks

```
1.  Write data/regions/songpa_yangju_corridor.yaml with these fields:

    region_id: songpa_yangju_kci
    name: Songpa-gu to 72사단 부곡리 KCI Corridor
    boundary:
      type: bbox
      north: 37.78    # tighten after sanity check
      south: 37.46
      east:  127.20
      west:  126.85
    assembly_zones:
      - id: A   # 송파구청 일자리센터 앞
        name: Songpa-gu Office Job Center
        lat: 37.5147
        lon: 127.1057
        metadata: {coordinate_class: public, role: assembly_primary,
                   source: "Hankyung 2024-02-29 + 송파구 조례 2023-09-14"}
      - id: B   # 삼전동 구민회관 앞
        name: Samjeon-dong Community Hall
        lat: 37.5036
        lon: 127.0857
        metadata: {coordinate_class: public, role: assembly_alt,
                   source: "Hankyung 2024-02-29"}
      - id: C   # 장지역 4번 출구 앞
        name: Jangji Station Exit 4
        lat: 37.4784
        lon: 127.1262
        metadata: {coordinate_class: public, role: assembly_alt,
                   source: "Hankyung 2024-02-29"}
      - id: D   # 잠실종합운동장 (사용자 working hypothesis, 출처 미확인)
        name: Jamsil Sports Complex (assembly variant — unverified source)
        lat: 37.5159
        lon: 127.0727
        metadata: {coordinate_class: public, role: assembly_unverified,
                   source: "user-supplied, no public 동원수송 source confirmed"}
    destination_zones:
      - id: T   # 72사단 부곡리 동원훈련장
        name: 72사단 부곡리 동원훈련장
        lat: 37.7400   # to be refined to 부곡리 산 6-17 centroid in extraction
        lon: 126.9500
        metadata: {coordinate_class: public, role: mobilization_destination,
                   source: "병무청 찾아가는길 (mma.go.kr/contents.do?mc=mma0002106)",
                   address: "경기 양주 장흥 부곡리 산 6-17"}
    rail:
      access:  {id: S, name: rail-access-stub,  lat: ?, lon: ?}    # finalize in Phase 1.4
      egress:  {id: R, name: rail-egress-stub,  lat: ?, lon: ?}
      travel_time_min: 60     # placeholder; treated as documented assumption
      headway_min:    30
      capacity_pax_per_train: 500
      metadata:
        source_class: documented_assumption
        operational_claim: abstract_long_distance_proxy_no_real_timetable
    metadata:
      kci_status: corridor_for_kci_submission
      data_sensitivity: public_open_data_only

2.  Run an OSMnx extraction smoke (one-shot, save to cache):

    python -c "
    import sys; sys.path.insert(0, '.')
    from src.realworld.osm_network import extract_bbox_graph, save_graphml
    g = extract_bbox_graph(north=37.78, south=37.46, east=127.20, west=126.85)
    save_graphml(g, 'data/cache/songpa_yangju_corridor.graphml')
    print('nodes', g.number_of_nodes(), 'edges', g.number_of_edges())
    "

3.  🟡 IN-PHASE DECISION (final bbox): if the extraction is smaller than ~5,000 nodes,
    extract was probably too tight; widen +0.05 deg in the limiting axis.
    If larger than ~30,000 nodes, runtime will be costly; trim away dead corners.
    Target: 5,000–20,000 nodes pre-filter (post-arterial-filter ~500–2,000).

4.  Build the simulator-compatible graph:

    python -c "
    import sys; sys.path.insert(0, '.')
    from src.realworld import adapter, regions, validation
    region = regions.load_region('data/regions/songpa_yangju_corridor.yaml')
    g = adapter.build_simulator_graph(region,
        cache_path='data/cache/songpa_yangju_corridor.graphml')
    validation.assert_graph_ready(g, region)
    print('built sim graph:', g.number_of_nodes(), 'nodes')
    "

5.  Confirm reachability for every (origin, destination) pair via shortest-path probe:
    A→T, B→T, C→T, D→T must all return finite distance.
    Same for A→S→R→T multimodal path. If any pair is unreachable, add explicit
    connector edges in zones.add_connectors() or widen bbox.

6.  Generate accessibility-loss diagnostic:

    python scripts/run_accessibility_loss_analysis.py \
      --region data/regions/songpa_yangju_corridor.yaml \
      --cache  data/cache/songpa_yangju_corridor.graphml \
      --output data/validation/accessibility_loss.csv

    Inspect: confirm 올림픽대로 / 강변북로 / 외곽순환 each show single-edge-removal
    impact (these are the expected single-points-of-failure on the corridor).

7.  Write data/cache/songpa_yangju_corridor_manifest.json with extraction parameters,
    OSM snapshot hash, node/edge counts pre and post filter, timestamp.
```

### 3.3 Validation gate

- Graph nodes (post-filter) within 500–2,000 range.
- All four origins + destination + rail access/egress reachable.
- accessibility-loss CSV shows ≥3 critical edges identifiable on the connecting expressways.

### 3.4 Rollback

If OSMnx is unavailable or rate-limited, the upstream cache `data/cache/pilot_region_road.graphml` (Songpa-only) cannot substitute — the corridor goes outside its bbox. Wait and retry, or use a saved offline OSM snapshot.

---

## 4. Phase 2 — Code adaptation

### 4.1 Prerequisites

- Phase 1 complete; corridor cache + region YAML usable.

### 4.2 Tasks

```
1.  ADAPT data/scenarios/disruption_scenarios.csv:
    - Remap every `D` reference to `T` (the new destination ID).
    - Add new scenario rows for arterial blockages on the connecting expressways:
        kci_olimpic_blockage      blocked        olympic_dae-ro_link_id
        kci_gangbyeon_blockage    blocked        gangbyeon-buk-ro_link_id
        kci_outer_loop_blockage   capacity_30%   outer_loop_link_id
    - Drop scenarios outside the corridor (none should remain).

2.  COPY data/scenarios/policy_alternatives.csv as-is.
3.  COPY data/scenarios/sensitivity_design.csv as-is.

4.  ADAPT data/parameters/fleet_assumptions.csv:
    - Strip source_url_or_citation columns of empirical-evidence values.
    - Set source_class = expert_assumption_virtual_study for every row.
    - Verify bus.fleet_size, shuttle, last-mile, capacity values are 23/23/23/45.

5.  ADAPT data/parameters/rail_assumptions.csv:
    - Strip Seoul Open Data plaza URLs; rephrase as documented assumptions.
    - Mark as abstract_long_distance_proxy_no_real_timetable.

6.  ADAPT config.yaml:
    - personnel.total: 1000
    - origin: A   (default; cycled to B/C/D in Phase 4 robustness)
    - destination: T
    - network.region_yaml: data/regions/songpa_yangju_corridor.yaml
    - network.cache_path: data/cache/songpa_yangju_corridor.graphml
    - bus.fleet_size: 23
    - multimodal.shuttle_fleet_size: 23
    - multimodal.lastmile_fleet_size: 23
    - multimodal.lastmile_vehicle_capacity: 45
    - rail.headway_min: 30
    - rail.capacity_pax_per_train: 500
    - rail.travel_time_min: 60
    - failure.* : preserve upstream defaults
    - phase1: preserve upstream grid; ADD origin as 5th factor — see 4.3 decision
    - phase2: preserve upstream grid

7.  ADAPT main.py:
    - PROJECT_ROOT = pathlib.Path(__file__).parent
    - sys.path.insert(0, str(PROJECT_ROOT))
    - --phase 1 / --phase 2 / --quick paths preserved.

8.  ADAPT generate_report_figures.py:
    - Korean axis labels; English legends per submission_format.md §7.
    - Drop figure 0 pipeline overview.
    - Bind to kci/results/ output directory.
```

### 4.3 🟡 IN-PHASE DECISION: origin treatment in Phase 1

Two options, pick one before §5 Phase 3 smoke:

| Option | Cell count vs upstream | Pros | Cons |
|---|---|---|---|
| **(a) Full 5-factor sweep** | 4× Phase 1 cells (≈ 33,600 paired runs) | Clean robustness story; per-origin CIs | Runtime ↑ |
| **(b) Focused robustness** | Phase 1 with origin=A only (≈ 8,400) + a 4-origin × small-cell robustness check | Faster; manuscript still gets per-origin comparison | Two-stage analysis to write up |

**Default if undecided at smoke time: (b)**, with a Phase 4.5 "origin robustness" sub-run after the main Phase 1 completes.

### 4.4 Validation gate

```bash
cd kci
python main.py --quick --config config.yaml --origin A
```

Expected: a single Phase-1 cell completes end-to-end in <2 min, writes `results/quick_check.csv`.

### 4.5 Rollback

If a config or scenario column mismatch breaks runs, diff against upstream `config.yaml` to see what schema field changed. Do NOT re-introduce upstream calibration columns (parameter_evidence_review_packet etc.) — they are EXCLUDE per audit.

---

## 5. Phase 3 — Smoke validation

### 5.1 Tasks

```
1.  Quick smoke (single config):
    python scripts/run_pilot_smoke.py --config config.yaml --origin A --seeds 5

2.  Confirm:
    - both modes (bus_only, multimodal) produce non-empty trajectories
    - censoring_rate not 100% (fleet not absurdly undersized for 40 km)
    - penalized_makespan finite for both

3.  Run reproducibility smoke:
    python scripts/run_reproducibility_smoke.py
    python scripts/run_clean_checkout_smoke.py

4.  Repeat the single-cell smoke for origins B, C, D to confirm reachability:
    for O in B C D; do
      python scripts/run_pilot_smoke.py --config config.yaml --origin $O --seeds 5
    done
```

### 5.2 Validation gate

All four origins return finite penalized_makespan. Reproducibility manifest matches upstream pattern (deterministic seeds, identical results across runs).

### 5.3 🟡 IN-PHASE DECISION: rail leg (audit §6 #2 still open)

If multimodal smoke shows rail+bus dramatically slower than bus-only at all origins (the 강변북로/외곽순환 expressway path dominates), consider:

| Sub-option | When |
|---|---|
| **(i) Keep abstract long-distance rail** | Default — multimodal is a clean comparator |
| **(ii) Demote rail to alternative scenario** | If rail is structurally never competitive but interesting under specific disruptions |
| **(iii) Drop rail entirely** | If rail makes no sense at any disruption intensity (last resort — would weaken the contribution) |

**Default if undecided: (i)**. Document the rail-leg framing more explicitly in `research_plan.md` §6 if (ii) or (iii) is taken.

---

## 6. Phase 4 — Full experiment runs

### 6.1 Tasks

```
1.  Phase 1 (paired CRN, disruption sweep), per the chosen origin treatment (§4.3):

    # Option (b) baseline — origin = A
    python main.py --phase 1 --config config.yaml --origin A
    # Output: results/phase1_results.csv, phase1_summary.csv, phase1_ci.csv

2.  Phase 2 (assembly delay × policy):
    python main.py --phase 2 --config config.yaml --origin A
    # Output: results/phase2_results.csv, phase2_ci.csv

3.  Morris sensitivity:
    python scripts/run_sensitivity.py --config config.yaml \
      --output results/morris_sensitivity.csv \
      --output-summary results/morris_summary.csv

4.  Origin-robustness sub-run (Option (b) only):
    for O in B C D; do
      python main.py --phase 1 --config config.yaml --origin $O \
        --grid focused --seeds 10  # smaller cells
    done
    # Output: results/phase1_origin_{B,C,D}_robustness.csv

5.  Accessibility-loss diagnostic (regenerated for the corridor):
    Already produced in Phase 1 §3.2.6. Re-confirm.
```

### 6.2 Validation gate

- Phase 1 paired-run rows match the cell count expected from the design.
- All cells have non-null censoring_rate.
- Morris `mu_star` finite for the parameters that should be active (disruption probability, capacity-reduction depth, fleet size, dispatch headway).
- Origin-robustness sub-run completes for B, C, D.

### 6.3 Runtime budget

| Run | Estimate (single-machine, 8 cores) |
|---|---|
| Phase 1 (origin=A only, ~8,400 paired) | 2–6 hours (corridor-dependent) |
| Phase 2 (~840 paired) | 0.5–1 hour |
| Morris (~4,320 evaluations) | 1–3 hours |
| Origin-robustness (3 origins × focused) | 1–2 hours total |
| **Total** | ~5–12 hours wall-clock |

Use `--workers N` (if exposed) or split runs. If runtime exceeds budget, tighten the disruption-intensity grid in Phase 1 first; do not reduce seeds (paired CIs need the seeds).

---

## 7. Phase 5 — Analysis, CIs, figures

### 7.1 Tasks

```
1.  CI tables and paired-delta tables:
    python scripts/make_pilot_statistics.py --results results/ \
      --output-dir results/tables/

2.  Figures (Korean axis labels per submission_format.md §3):
    python scripts/make_pilot_figures.py --results results/ \
      --output-dir manuscript/figures/

    Required figures (5 ± 1 for the manuscript):
      figure1_concept.png         <- COPY 전시_예비군_수송체계_개념도.png
      figure2_corridor_map.png    <- NEW; map of the Songpa↔양주 arterial corridor
      figure3_breakeven.png       <- delta_makespan(disruption) heatmap
      figure4_miss_rate.png       <- censoring rate vs disruption intensity
      figure5_origin_robustness.png <- per-origin penalized_makespan boxplot

3.  Generate Figure 2 (corridor map):
    python scripts/make_corridor_map.py \
      --region data/regions/songpa_yangju_corridor.yaml \
      --cache  data/cache/songpa_yangju_corridor.graphml \
      --output manuscript/figures/figure2_corridor_map.png

    (write this small helper as a one-off matplotlib + osmnx plot of nodes/edges
     with origin markers A/B/C/D and destination T)

4.  Tables (English captions per submission_format.md §7):
    table1_design_summary.csv         <- Phase 1 + Phase 2 cell summary
    table2_phase1_paired_delta.csv    <- bus_only - multimodal, with 95% CI
    table3_phase2_policy.csv          <- STRICT vs GRACE comparison
    table4_morris_top10.csv           <- top 10 parameters by mu_star
    table5_origin_robustness.csv      <- origin A/B/C/D penalized makespan summary
```

### 7.2 Validation gate

- Every figure renders without error and is ≤ A4-half page.
- All table headers in English.
- Number of figures ≤ 5, tables ≤ 5 (KCI 30-page budget).

---

## 8. Phase 6 — Manuscript draft (`.hwp` via hwpx skill)

### 8.1 Authoring strategy

**Use the hwpx skill, Workflow F (clone-form).** The official `한국군사학논집 논문편집양식.hwp` is already in `kci/학회_관련_정보/`. Cloning preserves 100% of layout, table styling, font slots, and outline levels — there is no defensible reason to rebuild from scratch.

```
1.  Author the manuscript text in Markdown first:
    kci/manuscript/manuscript_ko.md     <- Korean primary
    kci/manuscript/abstract_en.md       <- English abstract (≤ 200 words)
    kci/manuscript/references.md        <- APA references list
    kci/manuscript/captions.md          <- figure / table captions (English)

2.  Mirror the section structure from submission_format.md §4:
    1. 서론
       1.1. 연구배경 및 목적
       1.2. 연구 질문
    2. 선행연구 고찰
    3. 연구방법
       3.1. 시뮬레이션 모형 (paired CRN, censoring-aware metrics)
       3.2. 가상 통로 구축 (Songpa↔양주 major-arterial)
       3.3. 실험설계 (Phase 1, Phase 2, Morris)
    4. 결과 및 분석
       4.1. Phase 1 결과
       4.2. Phase 2 결과
       4.3. 민감도 분석
       4.4. 출발지 강건성
    5. 결론
       5.1. 시사점
       5.2. 한계 및 향후 연구

3.  Build the replacements map for clone_form.py:

    {
      "키케로의 최고선악론에 관한 고찰": "<Korean title>",
      "A Study on Cicero's De Finibus Bonorum et Malorum": "<English title>",
      "홍길동(Gildong Hong)": "<author KO>(<Romanized>)",
      "장길산(Gilsan Jang)": "",   # 2nd author placeholder if single-author
      "1. 한국국방연구원 군사발전연구센터": "<affiliation 1>",
      "2. 육군사관학교 경제법학과": "",
      "kmajc@kma.c.kr": "<corresponding email>",
      "본 연구는 화랑대연구소 국고학술과제 26-A1234-01의 지원을 받아 작성된 논문임.":
          "<funding statement or 'no external funding'>",
      "Lorem ipsum, Lorem, ipsum, cicero, lipsum": "<5 English keywords, comma-separated>",
      "양식, 채우기 텍스트, 로렘 입숨, 키케로": "<5 Korean keywords, comma-separated>",
      "<English ABSTRACT placeholder>": "<200-word English abstract>",
      "1. 서론": "1. 서론",         # placeholder rows (kept identical)
      "1.1. 연구배경 및 목적": "1.1. 연구배경 및 목적",
      ...
    }

4.  Run clone_form.py:

    python "C:/Users/User/.claude/skills/hwpx/scripts/clone_form.py" \
      "학회_관련_정보/한국군사학논집 논문편집양식.hwp" \
      "manuscript/manuscript.hwpx" \
      --map manuscript/replacements.json \
      --validate

    Note: clone_form operates on .hwpx. Use the converted
    "학회_관련_정보/한국군사학논집_논문편집양식.hwpx" if the .hwp variant fails.

5.  Post-process namespaces (REQUIRED):
    python "C:/Users/User/.claude/skills/hwpx/scripts/fix_namespaces.py" \
      manuscript/manuscript.hwpx
    python "C:/Users/User/.claude/skills/hwpx/scripts/validate.py" \
      manuscript/manuscript.hwpx

6.  Insert figures and tables manually in 한컴오피스 한글:
    - The clone_form output retains the template's table styles. Open the .hwpx
      in 한글, replace placeholder body content with the manuscript prose, and
      import figure PNGs from manuscript/figures/.
    - Rebuild tables using the template's existing borderFill IDs (preserves
      look-and-feel without manual styling).

7.  Convert to .hwp for submission:
    한컴오피스 한글 → 다른 이름으로 저장 → .hwp
    (KCI accepts .hwp only per submission_format.md §1.)
```

### 8.2 Validation gate (per submission_format.md §9)

- Body font is Pretendard 10 pt 160 % JUSTIFY in random-spot-check.
- Korean section headings present at OUTLINE level 0/1/2.
- All figures / tables / abstract / references in English.
- English abstract word count ≤ 200.
- Total pages ≤ 30 in 한글 print preview.
- Reference list is APA, internet-searchable, English-titled where available.

### 8.3 🟡 IN-PHASE DECISION: figures inserted programmatically vs manually

`clone_form.py` text-only replacement is deterministic and safe; figure insertion via XML is fragile (per hwpx skill SKILL.md "이미지 `<hp:pic>` 구조가 불완전하면 한컴오피스가 크래시한다"). **Default: insert figures manually in 한글.** Reserve programmatic insertion for camera-ready if requested.

---

## 9. Phase 7 — Submission package

### 9.1 Pre-submission checklist (per submission_format.md §1, §9)

```
[ ]  manuscript.hwp in 편집양식 (Pretendard 10pt, A4, ≤ 30 pages)
[ ]  All figures / tables / abstract / references in English (APA)
[ ]  English abstract ≤ 200 words, includes necessity/results/significance
[ ]  Author info STRIPPED from filename and document body
[ ]  KCI similarity report < 10% (run KCI 문헌유사도 검사)
[ ]  보안성 검토완료 문서 obtained from KMA (mandatory for ax_01@kma.ac.kr)
[ ]  저작권 양도 및 활용 동의서 자필 서명 후 jpg 스캔
       파일명: 저작권 양도 및 활용 동의서(<저자명>).jpg
[ ]  Funding statement decided (real grant or "no external funding")
[ ]  Cover-letter positioning paragraph invokes 투고규정 §2-나-5
       "첨단 과학기술의 군사적 응용"
```

### 9.2 JAMS upload sequence

```
1. Login to https://kjmac.jams.or.kr
2. 학술지 → 논문제출 → 한국군사학논집 클릭
3. 연구 윤리 서약 (모든 저자 서명)
4. 논문관련 정보 입력
   - 원문파일: manuscript.hwp (anonymized filename)
5. 첨부파일 업로드
   a) 이미지파일: 저작권 양도 및 활용 동의서(<저자명>).jpg
   b) 첨부파일: 보안성 검토완료 문서 (KMA institutional doc)
   c) KCI 문헌유사도 결과 (PDF)
6. "다음 단계로" 클릭
7. 저자 등록 (공동저자 포함, 체크리스트, CCL 동의)
8. "제출" 클릭
9. 접수 확인 메일 수신 → received 날짜 기록
```

### 9.3 Post-submission

- Track received → accepted → published timeline. Next publication windows: Feb 28, Jun 30, Oct 31.
- If reject ("게재불가"), 6-month re-submission lock starts immediately. Use the time to address review comments and re-run experiments if needed.
- If revise ("수정후 재심"), follow the editor-issued deadline; rerun any affected analyses; resubmit via JAMS revision workflow.

---

## 10. Open items that block submission (NOT block running experiments)

These can be parked until Phase 6/7 but must close before Phase 7 final submit:

| Item | Owner | Source |
|---|---|---|
| Authorship and affiliation | User | `agents.md` §7 #12 |
| Funding statement | User | `submission_format.md` §10 |
| 보안성 검토완료 문서 발급 | User (KMA institutional process) | `submission_format.md` §1 #4 |
| Final Korean and English titles | User + author | `submission_format.md` §10 |
| 5 + 5 keyword sets | User + author | `submission_format.md` §10 |
| English abstract (≤ 200 words) | Author at draft freeze | `submission_format.md` §10 |
| KCI 문헌유사도 < 10% | Author at submission | `submission_format.md` §1 |

Phases 0–5 (code, data, runs, figures) can complete without any of these. Phase 6 can be drafted with placeholders. Phase 7 cannot proceed until **all** are closed.

---

## 11. Decision points summary (where this plan branches)

| § | Decision | Default | Trigger to revisit |
|---|---|---|---|
| 3.3 | Final OSM bbox | lat 37.46–37.78, lon 126.85–127.20 | Node count outside 5,000–20,000 pre-filter |
| 4.3 | Phase 1 origin treatment | (b) Focused robustness | If runtime budget allows full 5-factor sweep, switch to (a) |
| 5.3 | Rail leg framing | (i) Abstract long-distance rail | If multimodal is structurally never competitive |
| 8.3 | Figure insertion method | Manual via 한글 | Camera-ready may use programmatic |

---

## 12. Roll-back and recovery notes

- **Phase 0 imports break:** restore `kci/src/realworld/__init__.py` from upstream and re-prune. Do not delete `kci/src/`.
- **Phase 1 OSM extraction fails / rate-limited:** retry with smaller bbox, then stitch. Do not commit a partial cache; the manifest hash will be wrong.
- **Phase 2 schema mismatch:** diff `config.yaml` against upstream — usually a renamed `policy.* → dispatch.policy.*` style change. Do not bring the upstream parameter-evidence review columns back.
- **Phase 4 runtime overrun:** tighten Phase 1 disruption-intensity grid first; preserve seeds. Do not drop CRN pairing.
- **Phase 5 figures cluttered:** consolidate to ≤ 5; KCI 30-page limit is tight.
- **Phase 6 clone_form coverage low (< 60 %):** the template's text differs more than expected; re-analyze with `clone_form.py --analyze` and rebuild the map JSON. Do not edit `<hp:t>` nodes by hand.
- **Phase 7 보안성 검토 delayed:** all of Phases 0–6 can wait; this is the most likely real bottleneck.

---

## 13. What this plan does NOT do

- Re-litigate the 16 resolved decisions in `agents.md` §7. If a decision needs to change, edit `agents.md` first, then update this plan.
- Pursue the 12 deferred formal-acceptance gates (`pilot_region_accepted`, `validation_package`, `manuscript_report_alignment`, etc.). Those belong to the follow-up calibration paper.
- Author the manuscript prose itself. Phase 6 builds the layout shell; the user (with author input) writes the body content into the placeholders.
- Bind to a specific submission target issue. The journal accepts rolling submissions; the issue assignment happens at acceptance.
