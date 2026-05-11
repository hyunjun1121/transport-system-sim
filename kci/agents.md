# `kci/` Agent Working Context

**Folder role:** Self-contained workspace for preparing a KCI submission to 한국군사학논집 (Journal of Korean Military Studies). Code, data, manuscript, and supporting documents for this submission live under `./kci/`. The upstream repo (`../`) is the source of the simulator and is referenced, not modified, from this workspace.

**Last updated:** 2026-05-11
**Author email on record:** `ax_01@kma.ac.kr` (Korea Military Academy — pending confirmation, see §7)

---

## 1. One-line mission

Industrial-engineering controlled-experiment evaluation of bus-only versus rail–bus multimodal transport for emergency reserve-force mobilization, on a virtual major-arterial road corridor extracted from Songpa-gu (Seoul) cached OSM data, targeted for submission to KCI-listed 한국군사학논집.

## 2. Binding constraints

- **Target journal:** 한국군사학논집 (한국군사학회). The standing submission rules, manuscript template, copyright transfer form, and submission application are archived in `kci/학회_관련_정보/`. These are binding format and process requirements; reconcile against them at draft freeze.
- **Submission language:** Korean primary, English abstract only. No English supplementary manuscript for this submission.
- **Real-world calibration is deferred.** The upstream repo carries 12 blocked formal-acceptance gates and a real-world calibration scaffold; the KCI study explicitly does not pursue them. The contribution is positioned as IE methodology applied to a virtual corridor, not as a calibrated empirical study.
- **Destination is the publicly documented 72사단 부곡리 동원훈련장** (경기 양주 장흥 부곡리 산 6-17), published by 병무청 on its 「찾아가는길」 page. The manuscript may name the unit, its parent 육군동원전력사령부, the 200/201/202보병연대 composition, the 부곡리 동원훈련장 address, and the published 동원훈련 (2박3일) rules (12:00 입영, +1h 지연입소 허용). **Do not add anything beyond publicly published facts:** no internal site layout, no end-strength estimates, no wartime mission specifics, no district-level 동원지정 catchment claims. The Songpa→72사단 catchment is *not* publicly documented; the manuscript frames the routing as illustrative, not as an assertion of operational assignment. (This supersedes the earlier 2026-05-11 "no real military unit named" rule.)
- **Coordinates policy:** only public or publicly documented coordinates. The OSM extraction now spans Songpa-gu origins through to 양주 장흥 부곡리 (expanded bbox — see §7 #3). Any new coordinate added to `kci/` must be documented as `coordinate_class: public` or `coordinate_class: synthetic` in the region YAML.

## 3. Companion documents (read these first)

| Document | Role |
|---|---|
| `kci/research_plan.md` | WHY / WHAT. Working title, target journal fit, research question (Q1–Q4), in/out scope, methodology pillars (paired CRN, censoring-aware metrics, Morris), expected contributions, manuscript outline, honest limitations, acceptance risks and mitigations. |
| `kci/repo_assets_audit.md` | WHICH FILES. File-by-file COPY / ADAPT / EXCLUDE / REFERENCE-ONLY decisions for every relevant path in the upstream repo, synthesized from three parallel sub-agent audits on 2026-05-11. Includes the suggested `kci/` directory layout and manuscript-asset → KCI section mapping. |
| `kci/plan.md` | HOW. Implementation plan — file moves, code changes, run schedule, figure/table assembly checklist. **Not yet authored.** Should be authored after the open decisions in §7 are closed. |
| `kci/학회_관련_정보/` | Binding submission rules and templates from 한국군사학회. Includes 논문투고 규정, 논문접수 첨부서류 안내, 논문편집양식, 저작권 이양 동의서, 논문투고신청서, 수시 변경안내. |

## 4. Workspace conventions

- **Platform:** Windows 11. Default shell is PowerShell. Bash is available via the Bash tool for POSIX scripts.
- **Path style:** absolute paths in tool calls. Project root from inside `kci/` is `C:\Users\User\Downloads\transport-system-sim\kci`.
- **Encoding:** UTF-8 for all source files. Korean filenames in `학회_관련_정보/` and image files at the upstream root must be quoted properly. When invoking Python that prints Korean to stdout, set `sys.stdout.reconfigure(encoding='utf-8')`.
- **Git:** the repo is a single git repo at `C:\Users\User\Downloads\transport-system-sim`. The `kci/` folder is a normal subdirectory tracked by the same git history. Branch is `main`. Do not commit unless explicitly asked.
- **Language of artifacts in `kci/`:** all planning, audit, and `agents.md`-style documents are in **English** by user instruction. The Korean manuscript and figures are the only Korean artifacts.

## 5. Upstream repo relationship

The upstream repo at `..` (one level above `kci/`) carries:

- The simulator (`src/`, `main.py`, `config.yaml`, `requirements.txt`).
- A large real-world calibration / formal-acceptance scaffold (most of `src/realworld/*.py` beyond the OSM extraction surface, most of `data/parameters/`, most of `data/manifests/`, most of `data/validation/`, most of `tests/test_realworld_*_acceptance*.py` and `*_packet*.py`, most of `scripts/write_*_packet.py`, most of `docs/`).
- The Korean narrative report (`report_draft.md`, `report.docx`) and English paper draft (`paper/paper_draft.md`).
- Two military-themed assets used as KCI source material: `국방.md` (defense AI competition proposal) and `전시_예비군_수송체계_시뮬레이션_개념도.png` (wartime reserve-force transport conceptual diagram — slated for **Figure 1**).

**Rule for agents working in `kci/`:** consult `kci/repo_assets_audit.md` before touching any upstream file. The audit specifies which files COPY, ADAPT, EXCLUDE, or REFERENCE-ONLY. Do not import the entire `src/realworld/` package as-is — the current `__init__.py` eagerly re-exports ~100 modules that include the deferred acceptance machinery and would force every excluded module to load. A slim init is required (audit §1, "Real-world adapter subset").

## 6. Important framing rules

These are decisions that have been made deliberately and should not be re-litigated by future agents without explicit user direction.

1. **Use only publicly published facts about 72사단 부곡리 동원훈련장.** Web research on 2026-05-11 (three parallel sub-agents) confirmed: (a) 72사단 is a publicly documented 동원사단 under 육군동원전력사령부; (b) the 부곡리 동원훈련장 address (경기 양주 장흥 부곡리 산 6-17) is published by 병무청 itself; (c) the 동원훈련 schedule (2박3일, 12:00 입영, +1h 지연입소 허용) is published in 병무청 FAQ. Naming these facts in a KCI manuscript is consistent with what 병무청 publishes. **What is *not* publicly documented and must not be claimed:** district-level 동원지정 자원 catchment tables, internal site/gate layout, wartime mission, end-strength. The 송파→72사단 routing is explicitly framed as **illustrative**, with the catchment caveat in the Limitations section. This rule supersedes the earlier 2026-05-11 "no real military unit named" decision; the change is justified because 72사단 is a publicly documented 동원사단 (not an active combat unit) and the address is published by the government itself.
2. **Virtual corridor, not calibrated traffic model.** Road capacity, free-flow speed, vehicle counts, headway, transfer time, and rail timetable are documented planning assumptions, not source-backed evidence. The manuscript states this explicitly. The 12 blocked formal-acceptance gates in the upstream repo remain blocked and the KCI study makes no claim against them.
3. **Methodological paper, not a planning artifact.** The output is a *condition map* showing where bus-only versus rail–bus rankings flip under joint completion-time / miss-rate criteria — not operational guidance. The manuscript states this in §1, §6 (Limitations), §7 (Future work).
4. **Censoring-aware reporting.** Single-number completion time is misleading when some personnel fail to arrive within the time horizon. Always report miss-rate alongside, and use penalized makespan for any single-number summary. This is one of the three methodological pillars; do not weaken it.
5. **Paired CRN.** For each disruption realization, both modes are exercised on the same arrival times, road blockage draws, and BPR background-volume profiles. Do not break this pairing in any new experiment code.

## 7. Resolved decisions (closed 2026-05-11)

The 16 open decisions identified in `repo_assets_audit.md` §6 are resolved as follows. The implementation plan (`kci/plan.md`) should treat these as inputs.

| # | Item | Decision |
|---|---|---|
| 1 | Arterial filter scope | Include `secondary` in addition to `motorway / motorway_link / trunk / trunk_link / primary / primary_link`. The Songpa↔양주 corridor depends on `motorway` (올림픽대로, 강변북로, 외곽순환), so all three classes are required. |
| 2a | Origin (송파구) — primary scenarios | **Three publicly documented Songpa-gu mass-transport assembly sites** (Hankyung 2024-02-29, 송파구 조례 2023-09-14): (A) **송파구청 일자리센터 앞** (37.5147, 127.1057), (B) **삼전동 구민회관 앞** (37.5036, 127.0857), (C) **장지역 4번 출구 앞** (37.4784, 127.1262). All three are existing 예비군 수송버스 boarding sites under Songpa-gu ordinance. Caveat: the original program services routine 예비군훈련 to 강동송파, not 동원훈련 to 72사단; the manuscript treats these as documented mass-transport assembly sites used analogously for the 72사단 mobilization scenario. |
| 2b | Origin — additional scenario | **(D) 잠실종합운동장** (37.5159, 127.0727) as a secondary scenario, flagged in the manuscript as "출처 미확인 가정 변형" because no public source confirms 잠실 as a 병력동원 집결지. Included to show robustness across origin choices and to honor the user's prior working hypothesis. |
| 2c | Origin — Phase 1 treatment | Use origin as a 4-level factor (A/B/C/D) in a robustness sweep. Whether to fold this into the main Phase 1 grid (4× cell count) or run as a focused robustness check at fewer seeds is a `plan.md` design choice. |
| 3a | Destination | **72사단 부곡리 동원훈련장** (경기 양주 장흥 부곡리 산 6-17, ≈37.74 N / 126.95 E). Address publicly published by 병무청. Manuscript names the unit, parent 육군동원전력사령부, 200/201/202보병연대 composition, 동원훈련 2박3일 schedule, 12:00 입영 / +1h 지연입소 rules — all 병무청-published facts. |
| 3b | Catchment treatment | Songpa→72사단 동원지정 catchment is **not** publicly documented. Manuscript frames the routing as illustrative and includes an explicit Limitations footnote: *"실제 동원지정 자원의 행정구역별 배정은 병력동원소집통지서를 통해 개별 고지되며 공개 자료로 검증할 수 없음."* |
| 3c | OSM bbox | **Expanded from the Songpa-only pilot bbox** (~37.50–37.53 N, 127.09–127.14 E) to a corridor that contains all four origins, the 부곡리 destination, and the connecting expressway / arterial network. Provisional bbox: **lat 37.46–37.78, lon 126.85–127.20**. Final bbox to be fixed in `plan.md` after a quick OSMnx extraction sanity check. New cache file path: `data/cache/songpa_yangju_corridor.graphml` (provisional). |
| 4 | Network construction path | Build dynamically each run from the corridor region YAML + new GraphML cache via `realworld.adapter`. Cache is frozen; build is reproducible. |
| 5 | Rail leg under expanded corridor | Re-evaluate. The original 잠실↔잠실 abstract rail link is no longer applicable; the 송파↔양주 corridor has no high-frequency rail. Options: (i) keep an abstract long-distance rail leg with documented headway / capacity assumptions (closest reality: 1호선 + 7호선 + 의정부 환승), (ii) make rail an alternative scenario rather than the primary multimodal default, (iii) drop rail and reframe as bus-only resilience study. **Decision deferred to `plan.md`** but currently leaning toward (i) with strong "abstract rail leg" hedging. |
| 6 | Scenario remap | Remap all `D` references in `data/scenarios/disruption_scenarios.csv` to the 72사단 destination ID. Add new scenario rows for arterial blockages on the connecting expressways (올림픽대로, 강변북로, 외곽순환). |
| 7 | Fleet sizing | Keep current values (`bus.fleet_size = 23`, `multimodal.shuttle_fleet_size = 23`, `lastmile_fleet_size = 23`, `lastmile_vehicle_capacity = 45`) for the baseline; add fleet size as a Phase 1 sensitivity factor. Verify the baseline can plausibly move 1,000 personnel ≈40 km within a hard horizon. |
| 8 | Result reuse | **Re-run** Phase 1 and Phase 2 fresh on the new corridor. (User decision.) Do not mix legacy abstract-network results into the manuscript. |
| 9 | accessibility.py promotion | Include as a first-class KCI diagnostic. Drop `plausibility.py` (tied to deferred validation). |
| 10 | Single-mode fallback | Keep both modes. The bus-only vs rail–bus comparison is the contribution; do not collapse to single-mode. |
| 11 | Language | Korean primary, English abstract only. No English supplementary manuscript for this submission. |
| 12 | Authorship and affiliation | **PENDING USER CONFIRMATION.** Author email on record is `ax_01@kma.ac.kr` (KMA). The `국방.md` template lists 김현준 / 군사과학기술연구대 / kaist.ac.kr — almost certainly outdated. Do not insert author or affiliation into any draft until the user confirms. |
| 13 | Image strategy | `전시_예비군_수송체계_시뮬레이션_개념도.png` becomes **Figure 1**. Regenerate a new corridor-map figure as **Figure 2**. |
| 14 | `schemas/` directory | Omit from `kci/`. The simulator core uses Python-side validation. |
| 15 | `PROJECT_ROOT` | Adjust `main.py` path resolution so `kci/` works as a self-contained root. |
| 16 | `학회_관련_정보/` | Already in place. Sits alongside `kci/src/`, `kci/data/`, etc. Do not overwrite. |

## 8. Pending items (must close before submission)

- **Authorship and affiliation** (decision #12 above). Required before any draft circulates.
- **KCI manuscript template binding** (length, abstract length, keyword count, reference style). Read from `kci/학회_관련_정보/논문투고 규정.txt` and `한국군사학논집 논문편집양식.hwp` at draft freeze.
- **Final OSM bbox for the songpa↔양주 corridor** (provisional in §7 #3c). Do a quick OSMnx extraction sanity check at the start of `plan.md` execution; tighten the bbox if the network is too large to run in budget.
- **Rail leg treatment** (§7 #5). Resolve in `plan.md`: keep abstract long-distance rail with hedging, demote rail to alternative scenario, or drop rail entirely.
- **Origin Phase 1 treatment** (§7 #2c). Resolve in `plan.md`: full 4-level factor (4× cell count) vs focused robustness check at fewer seeds.
- **Phase 1 / Phase 2 / Morris run schedule and runtime budget** for the new corridor — likely larger than the upstream Songpa-only baseline.

## 9. Setup and run conventions (planned)

The implementation plan will define exact commands. Provisional shape:

- **Python environment:** Python 3.11+, `venv` at repo root or `kci/.venv`. Install from `kci/requirements.txt` (the ADAPTed version, with `osmnx` added and `python-docx` removed).
- **Working directory:** all commands assumed to run from `C:\Users\User\Downloads\transport-system-sim\kci`.
- **Cache build:** `python scripts/build_arterial_cache.py --filter major_arterials_secondary` produces `data/cache/arterial_corridor.graphml` and its manifest from the upstream OSM cache.
- **Smoke:** `python scripts/run_pilot_smoke.py` for fast offline check.
- **Phase 1:** `python main.py --phase 1 --config config.yaml`.
- **Phase 2:** `python main.py --phase 2 --config config.yaml`.
- **Sensitivity:** `python scripts/run_sensitivity.py --config config.yaml`.
- **Figures:** `python scripts/make_pilot_figures.py --results results/`.
- **Statistics tables:** `python scripts/make_pilot_statistics.py --results results/`.
- **Reproducibility smoke:** `python scripts/run_reproducibility_smoke.py` and `python scripts/run_clean_checkout_smoke.py`.

## 10. Document hierarchy and write conventions

When writing or editing under `kci/`:

- All planning, audit, and meta documents (this file, `research_plan.md`, `repo_assets_audit.md`, `plan.md`, `README.md`, `agents.md`) are **English only**.
- The Korean manuscript (`manuscript/manuscript_ko.md`), figure captions, and abstract translations are **Korean** (with the abstract also having an English version per KCI standard).
- Do not write the manuscript yet — it is downstream of `plan.md`.
- Do not duplicate upstream `docs/` content into `kci/docs/` verbatim. Each `kci/docs/*.md` should be a concise restatement with the deferred-track hedges removed and the IE/military framing applied (per `repo_assets_audit.md` §3).
- When adding a new file under `kci/`, also note its purpose in `kci/research_plan.md` §13 (companion documents) so the next agent can find it.

## 11. Conversation context summary (2026-05-11)

This file was created at the user's request after the following decisions and exchanges:

1. The user asked whether the current `report.docx` (virtual abstract-network results) could be accepted at a KCI journal. The honest answer was: not as-is for an accredited KCI journal; reframing as an IE methodology paper for a niche-fit journal is the practical path.
2. The user committed to the IE / virtual-corridor framing and selected 한국군사학논집 as the target journal, with the contribution positioned around reserve-force mobilization on a major-arterial Songpa corridor.
3. The user asked for `./kci/` to be created with (a) a detailed research plan and (b) a synthesized repo-asset audit produced by parallel Opus sub-agents. Both were authored: `research_plan.md` and `repo_assets_audit.md`.
4. The user committed to **re-running** experiments fresh on the new arterial corridor (decision #8 above), and asked whether the docx files specified a real military-unit destination. Both docx files were inspected; neither named a military facility — `D` was deliberately abstract `전방 지역`. The recommendation was therefore to use a synthetic centroid (decision #2 above), and the full set of 16 open decisions was closed in §7.
5. The user requested this `agents.md` to record the full context so future agents (or future sessions) can pick up without losing any of the framing or decisions.
6. **Destination and origin firmed up (2026-05-11, second update):** the user committed to **72사단 부곡리 동원훈련장** as the destination (replacing the earlier "synthetic centroid" decision) and asked for web-search verification of Songpa-gu mass-transport assembly sites. Three parallel Opus sub-agents executed the research and reported: (i) 72사단 / 부곡리 동원훈련장 is publicly documented by 병무청 itself, so naming it in a KCI paper is acceptable provided the manuscript adds no operational details beyond what 병무청 publishes; (ii) the 송파→72사단 동원지정 catchment is *not* publicly documented and must be hedged in Limitations; (iii) the user's working hypothesis 잠실종합운동장 has **no** public source confirming use as a 「병력동원훈련 집단수송 집결지」, but three OTHER Songpa-gu sites (송파구청 일자리센터, 삼전동 구민회관, 장지역 4번 출구) are documented by Hankyung 2024-02-29 and a 송파구 ordinance 2023-09-14 as 예비군 수송버스 집결지. The user then accepted both recommendations: (Q1) use the 3 documented sites as primary scenarios A/B/C plus 잠실 as scenario D (origin robustness sweep); (Q2) keep 72사단 부곡리 as the sole destination with catchment hedge. §2, §6 #1, §7, §8, and this §11 were updated to reflect the new framing.

The next step (per the agreed sequence) is to author `kci/plan.md` — the implementation plan that consumes `research_plan.md` (WHY / WHAT) and `repo_assets_audit.md` (WHICH FILES) plus the resolved decisions in this file (§7) to produce concrete file moves, code changes, run commands, and a figure/table assembly checklist.
