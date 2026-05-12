# KCI Implementation Plan — From Resolved Decisions to Submitted Manuscript (Optimized for Claude Code)

**Document role:** HOW. Step-by-step implementation plan that executes the research described in `research_plan.md` using the locked decisions in `agents.md` §7.
**Last updated:** 2026-05-11 (v0.6 — Bootstrap completeness, flag-matrix specification, Morris stream correction).
**Status:** Ready to execute.
**Working Directory:** All commands must be run from `C:\Users\User\Downloads\transport-system-sim\kci` (use `../` to reference upstream assets in the parent repo).

---

## 1. Execution model — Parallelization, sub-agents, critical path

### 1.1 Critical path (longest dependency chain)
```
[Bootstrap dirs + script/scenario copies + imports OK]
   → [OSM extract] → [graph build] → [config wired]
   → [smoke A passes]
   → [LONGEST Phase-4 run (Phase 1 paired CRN, ~2–6h)]
   → [analysis + figure assembly]
   → [Phase 6 drafting (6 parallel + 1 integration)]
   → [Manual HWP formatting]
   → [USER-SIDE 보안성 검토 발급]   ← real bottleneck for submission
   → [JAMS upload]
```
The wall-clock computational bottleneck is **Phase 4**. The real-world bottleneck is **보안성 검토 (Security Review)** at KMA. Request this at the start of Phase 1.

### 1.2 Parallelization rules per phase
| Phase | Parallel-within opportunities | Speedup vs serial | How to parallelize in Claude Code |
|---|---|---|---|
| 0 Bootstrap | File copies + dir creation + adapts | ~3–5× | Multiple Edit / Bash calls in one turn |
| 1 Network | OSM extract is sequential; diagnostics parallelizable | ~1.5× | Single `bash -c` for diagnostic step |
| 2 Code adapt | Code edits | ~5× | Parallel Edit calls in one turn |
| 3 Smoke | 4 origin smokes | ~3× | `bash -c "python ... & python ... & wait"` |
| **4 Full runs** | **4 experiment families** | **~2×** | **`bash -c "python ... & ... & wait"`** |
| **5 Analysis** | **5 figures + 5 tables** | **~3–5×** | **6 parallel Agent tool calls** |
| **6 Manuscript** | **6 sections drafted → 1 integration** | **~3–5×** | **6 parallel Agent tool calls → 1 sequential Agent** |
| 7 Submission | None (sequential JAMS form) | 1× | — |

---

## 2. Phase overview (Time Budget)

| Phase | Goal | Wall-clock (parallel) |
|---|---|---|
| 0 | Bootstrap `kci/` directory, slim package, scripts, scenario CSVs | ~30 min |
| 1 | Build corridor network + **trigger 보안성 검토 request** | ~1 h (+ user-side started) |
| 2 | Adapt simulator CLI flags, configs | ~30 min |
| 3 | Smoke runs | ~15 min |
| **4** | **Full experiment runs (4 concurrent)** | **~3–6 h** |
| 5 | Analysis, CIs, figures (6 parallel sub-agents) | ~30 min |
| 6 | Manuscript draft (6 parallel + 1 integration sub-agent) | ~1–2 h |
| 7 | Submission package + JAMS upload | User-side; days–weeks |

> **Total plan-side wall-clock estimate: ~7–11 hours.**

---

## 3. Phase 0 — Bootstrap

**[Claude Code Prompt]**
```text
Run all commands from: C:\Users\User\Downloads\transport-system-sim\kci
Execute these bootstrap tasks using parallel tool calls where possible:

1. CREATE DIRECTORIES (use Bash mkdir -p or multiple file writes):
   src/, src/experiment/, src/visualize/, src/realworld/, tests/, manuscript/figures/, manuscript/sections/,
   scripts/, results/, results/sensitivity/,
   data/, data/regions/, data/cache/, data/scenarios/, data/validation/.
   Add empty __init__.py in every Python package directory (src/, src/experiment/, src/visualize/, src/realworld/, tests/).

2. COPY SIMULATOR CORE FILES from ../src/ into kci/src/:
   network.py, scenario.py, dispatch.py, disruptions.py, fleet.py, metrics.py, models.py, policies.py, rail.py, sim_types.py, traffic.py, transfers.py, experiment/*, visualize/*.

3. COPY REALWORLD SUBSET from ../src/realworld/ into kci/src/realworld/:
   osm_network.py, zones.py, regions.py, types.py, validation.py, adapter.py, disruption_scenarios.py, pilot_experiments.py, policy_alternatives.py, sensitivity.py.

4. MODIFY kci/src/realworld/adapter.py to set ROUTEABLE_HIGHWAY_CLASSES to exactly:
   {"motorway", "motorway_link", "trunk", "trunk_link", "primary", "primary_link", "secondary", "secondary_link"}.

5. WRITE slim kci/src/realworld/__init__.py that ONLY re-exports the symbols listed in repo_assets_audit.md.

6. COPY SCRIPTS from ../scripts/ into kci/scripts/:
   run_pilot_smoke.py, run_sensitivity.py, run_accessibility_loss_analysis.py.

7. COPY SCENARIO CSVs from ../data/scenarios/ into kci/data/scenarios/:
   disruption_scenarios.csv, policy_alternatives.csv, sensitivity_design.csv.

8. COPY REQUIRED TESTS from ../tests/ to kci/tests/: test_models.py, test_dispatch.py, test_metrics.py (and any direct dependencies).

9. COPY FIGURE ASSET: ../전시_예비군_수송체계_시뮬레이션_개념도.png → kci/manuscript/figures/.

10. CREATE kci/main.py: copy ../main.py verbatim, then patch the top so that PROJECT_ROOT points at kci/ (i.e. PROJECT_ROOT = Path(__file__).resolve().parent) and sys.path is prepended with that path. Do NOT delete original CLI handlers; Phase 2 will extend them.

11. VALIDATE imports:
    python -c "import sys; sys.path.insert(0, '.'); from src import scenario, network, metrics; from src.realworld import adapter, osm_network; print('imports ok')"
```

---

## 4. Phase 1 — Network construction

**[Claude Code Prompt]**
```text
Execute network construction sequentially:

1. Create kci/data/regions/songpa_yangju_corridor.yaml with:
   - bbox: north 37.78, south 37.46, east 127.20, west 126.85
   - 4 origins (A=송파구청 일자리센터, B=삼전동 구민회관, C=장지역 4번 출구, D=잠실종합운동장 *unverified*)
   - destination T (72사단 부곡리 동원훈련장, ≈37.74N 126.95E).

2. Extract OSMnx graph (run only once; cached): write a short helper that calls osmnx.graph_from_bbox with the bbox above and saves to kci/data/cache/songpa_yangju_corridor.graphml.

3. Build the simulator-compatible graph using adapter.build_simulator_graph and validate (assert_graph_ready).

4. Diagnostics (use the Bash tool, single command):
   bash -c "python scripts/run_accessibility_loss_analysis.py --region-path data/regions/songpa_yangju_corridor.yaml --cache-path data/cache/songpa_yangju_corridor.graphml --output-path data/validation/accessibility_loss.csv --summary-path data/validation/accessibility_loss_summary.csv"

   NOTE: run_accessibility_loss_analysis.py uses its NATIVE flag names (--region-path, --cache-path, --output-path, --summary-path). Phase 2 only re-flags main.py and the simulation scripts, not this diagnostic.
```
*(USER ACTION — kick off in parallel with Phase 1: Request KMA 보안성 검토 발급 immediately).*

---

## 5. Phase 2 — Code adaptation, configs, smoke

**[Claude Code Prompt]**
```text
CRITICAL: Upstream main.py, scripts/run_pilot_smoke.py, and scripts/run_sensitivity.py do NOT accept the unified flags this plan depends on. Adapt each per the matrix below, then run smokes.

1. ADAPT CLI FLAGS (in parallel via multiple Edit calls). The semantics of --config is: it overrides path defaults defined inside each script. Existing native flags remain usable for backwards compatibility.

   | Script                                | Existing flags                                                              | ADD                                                |
   |---------------------------------------|-----------------------------------------------------------------------------|----------------------------------------------------|
   | kci/main.py                           | --phase, --quick, --test                                                    | --config, --origin, --grid, --seeds, --output      |
   | kci/scripts/run_pilot_smoke.py        | --region, --cache                                                           | --config, --origin, --seeds                        |
   | kci/scripts/run_sensitivity.py        | --region-path, --cache-path, --output-dir, --method, --trajectories, ...   | --config, --output (alias for --output-dir)        |

   Behaviour requirements:
   - --config <path>: load YAML; populate any path/seed defaults the script needs (region, cache, output, seeds count, etc.). Explicit native flags WIN over config.
   - --origin {A,B,C,D}: select which origin record from the region YAML to use as the assembly origin.
   - --seeds <int>: number of paired-CRN seeds for that invocation (overrides config.experiment.R if present).
   - --grid {pilot, focused, full}: density preset for the DoE grid (Phase 4 stream 4 uses 'focused').
   - --output <path>: where to write the primary CSV result for this invocation.
   - main.py.load_config() must accept the path passed via --config (currently hardcodes CONFIG_PATH).

2. UPDATE SCENARIO CSV:
   Edit kci/data/scenarios/disruption_scenarios.csv: remap any cell value 'D' (when it refers to the prior destination column) to 'T' so it matches the new destination keyed in region YAML. Do NOT touch policy_alternatives.csv or sensitivity_design.csv.

3. WRITE kci/config.yaml with:
   - region_path: data/regions/songpa_yangju_corridor.yaml
   - cache_path: data/cache/songpa_yangju_corridor.graphml
   - scenarios_path: data/scenarios/disruption_scenarios.csv
   - policies_path: data/scenarios/policy_alternatives.csv
   - design_path: data/scenarios/sensitivity_design.csv
   - output_dir: results/
   - experiment.R: 30 (default seed count)
   - experiment.seed_base: 1

4. RUN SMOKES (use the Bash tool, single command):
   bash -c "python scripts/run_pilot_smoke.py --config config.yaml --origin A --seeds 5 & python scripts/run_pilot_smoke.py --config config.yaml --origin B --seeds 5 & python scripts/run_pilot_smoke.py --config config.yaml --origin C --seeds 5 & python scripts/run_pilot_smoke.py --config config.yaml --origin D --seeds 5 & wait"

   Report when all 4 smokes return successfully (success_count > 0 in each JSON output).
```

---

## 6. Phase 4 — Full experiment runs (★ LONGEST PATH)

**Origin D Caveat:** Origin D (잠실종합운동장) is unverified in public sources. Results from this origin must carry an explicit caveat through Phases 5 and 6.

**[Claude Code Prompt]**
```text
Launch the 4 main experiment families concurrently. Use the Bash tool with `bash -c` to ensure background jobs work on Windows. Note the escape `\$O` so the OUTER PowerShell shell does not expand the loop variable.

bash -c "
  python main.py --phase 1 --config config.yaml --origin A --seeds 30 --output results/phase1_origin_A.csv > phase1.log 2>&1 &
  python main.py --phase 2 --config config.yaml --origin A --seeds 30 --output results/phase2_origin_A.csv > phase2.log 2>&1 &
  python scripts/run_sensitivity.py --config config.yaml --method morris --trajectories 200 --levels 4 --output results/morris_sensitivity.csv > morris.log 2>&1 &
  ( for O in B C D; do python main.py --phase 1 --config config.yaml --origin \$O --grid focused --seeds 10 --output results/phase1_origin_\$O.csv; done ) > phase1_robustness.log 2>&1 &
  wait
"

Notes:
- Stream 3 (Morris) MUST pass --method morris explicitly; the script default is 'auto' = deterministic OAT, which would silently produce non-Morris output despite the filename.
- Stream 4 (origin robustness B/C/D) runs sequentially inside its own subshell so it counts as one background job and respects the --grid focused budget.

Tell me when launched. I will notify you when completion logs appear.
```

---

## 7. Phase 5 — Analysis & Figures (★ PARALLEL AGENTS)

**[Claude Code Prompt]**
```text
Invoke 6 parallel sub-agents (Claude Code's Agent tool) to process the CSVs concurrently:
- Agent 1: Figure 2 (corridor map). Input: region.yaml, graphml. Include physical scale bar, mark A/B/C/D and T, highlight expressways.
- Agent 2: Figure 3 (break-even heatmap). Input: results/phase1_origin_A.csv.
- Agent 3: Figure 4 (miss-rate vs disruption). Input: results/phase1_origin_A.csv.
- Agent 4: Figure 5 (origin robustness). Input: results/phase1_origin_{B,C,D}.csv. *Must apply Origin D caveat (mark/footnote unverified).*
- Agent 5: All 5 tables (APA-style English headers) derived from results. Check submission_format.md for asset limits.
- Agent 6: Cross-reference audit — verify table↔figure consistency and max 10 total assets per KCI rules.
```

---

## 8. Phase 6 — Manuscript draft (★ 6 DRAFTING + 1 INTEGRATION)

**[Claude Code Prompt]**
```text
Part 1: Invoke 6 parallel sub-agents (Agent tool) to draft sections in manuscript/sections/:
- Agent 1: 01_introduction_ko.md (3-4 pages). Context: research_plan.md and ../국방.md.
- Agent 2: 02_literature_ko.md (10-20 APA citations).
- Agent 3: 03_methods_ko.md (6-8 pages). Simulator, virtual corridor, DoE.
- Agent 4: 04_results_ko.md (6-8 pages). Reference Phase 5 outputs. *Disclose Origin D caveat in narrative and tables.*
- Agent 5: 05_conclusion_ko.md (2-3 pages). Include catchment hedge.
- Agent 6: 00_abstract_en.md (≤ 200 words) and references_apa.md.

Part 2: After all 6 finish, invoke 1 Integration Sub-agent to harmonize into manuscript/manuscript_ko.md. This agent MUST:
- Resolve citation number conflicts and renumber consistently.
- Align figure/table indices across sections.
- Enforce tonal/terminological consistency (Korean academic register).
- Do NOT simply 'cat' the files.
```

*Note on Formatting:* Do NOT use `clone_form.py` to auto-inject prose into `한국군사학논집_논문편집양식.hwpx`. The HWPX file is a STYLE GUIDE, not a placeholder form. The user will manually copy-paste the finalized `manuscript_ko.md` text into 한컴오피스 한글 using the required Pretendard 10pt format (Workflow A / Manual).

---

## 9. Phase 7 — Submission (User Manual Steps)
1. Receive KMA 보안성 검토 문서.
2. Manually format `manuscript_ko.md` into the official `.hwp` template per submission_format.md.
3. Strip author info from `.hwp` filename and body (blind review).
4. Sign 저작권 이양 동의서.
5. Check KCI similarity (<10%).
6. Upload to JAMS.

---

## 10. Roll-back and recovery notes
* **Phase 0 bootstrap incomplete:** If imports fail at step 11, the most common cause is a missing copy in steps 2/3/6/7. Re-run `python -c "from src.realworld import adapter"` with a verbose traceback to locate the missing module before proceeding.
* **CLI argument errors:** If Phase 2/3/4 reports `unrecognized arguments`, verify Phase 2 step 1 was completed for the script in question. Native flags (e.g., `--region-path`) remain valid as fallback.
* **Phase 4 overrun:** Drop streams in this order — first Stream 2 (Phase 2 paired-CRN), then reduce Morris `--trajectories` from 200 → 100, then drop Stream 4 (origin robustness B/C/D). Stream 1 (Phase 1 origin A) is non-negotiable.
* **Bash tool failures on Windows:** If `bash -c` fails to launch, fall back to multiple parallel Bash tool invocations in a single turn — each running one stream in foreground.

---

## 11. Quick-start summary (TL;DR)
1. **Now:** Request 보안성 검토 발급 at KMA.
2. **Phase 0 (~30m):** Bootstrap — copy src/ + scripts/ + scenarios/ + main.py, create runtime dirs, validate imports.
3. **Phase 1 (~1h):** OSM extraction & graph validation (use NATIVE accessibility-script flags).
4. **Phase 2 (~30m):** Patch argparse on main.py / run_pilot_smoke.py / run_sensitivity.py per matrix, write config.yaml, remap CSV.
5. **Phase 3 (~15m):** Parallel smoke runs A/B/C/D.
6. **Phase 4 (~3-6h):** Background launch of 4 bash streams (Morris MUST carry `--method morris --trajectories 200`). Go get coffee.
7. **Phase 5 (~30m):** 6 parallel Agent tool calls for figures/tables.
8. **Phase 6 (~2h):** 6 parallel Agent tool calls for sections → 1 Integration Agent for harmonization.
9. **Phase 7:** User pastes markdown into HWP and submits to JAMS.
