# KCI Research Plan — Reserve-Force Mobilization Transport Resilience Study

**Workspace folder:** `./kci/`
**Target journal:** 한국군사학논집 (Journal of Korean Military Studies), KCI-listed
**Document role:** Research-level plan (WHY / WHAT). Implementation steps live in a separate `plan.md` to be authored after this plan and the companion `repo_assets_audit.md` are accepted.
**Status:** Draft v0.1 (2026-05-11). All claims here are scoped to the planned virtual-corridor study; no real-world calibration is asserted.

---

## 1. Working title

> **A Controlled-Experiment Industrial-Engineering Evaluation of Bus-Only versus Rail–Bus Multimodal Transport for Reserve-Force Mobilization on a Major-Arterial Virtual Corridor**

Korean working title (for the submission file):

> **예비군 동원 수송체계 회복력 평가: 송파구 주요 간선도로 가상 통로에서 단일수단(버스) 대비 복합수단(철도-버스)의 통제실험 기반 비교**

The English working title is for internal use; the manuscript itself will be submitted in Korean as the primary language, with an English abstract per the journal’s standing rules already filed under `kci/학회_관련_정보/`.

## 2. Target journal fit

`한국군사학논집` accepts (a) military strategy and policy work and (b) quantitative / operations-research studies with explicit military application. The proposed study sits in (b): an industrial-engineering simulation of a defense-relevant logistics problem (reserve-force mobilization) under disruption. The military framing carries the contribution; the IE methodology supplies the rigor.

The standing submission rules archived in `kci/학회_관련_정보/` (논문투고 규정, 논문접수 첨부서류 안내, 논문편집양식, 저작권 이양 동의서, 논문투고신청서, 수시 변경안내) are the binding format and process requirements. This plan does not duplicate them; the implementation plan must reconcile manuscript layout, length, abstract, keyword, and reference style against those documents at draft freeze.

## 3. Research question

> **Under disruption to a major-arterial road corridor between an urban assembly zone (Songpa-gu) and a reserve-force assembly area, how does the resilience of bus-only transport compare with rail–bus multimodal transport, when resilience is measured jointly by completion time, censoring (uncompleted personnel under a hard time horizon), and resource efficiency?**

Sub-questions:

- Q1. **Mode comparison.** Holding fleet, headway, and disruption realizations equal under a paired CRN design, which mode is faster on the median, and how does the gap depend on disruption intensity?
- Q2. **Censoring sensitivity.** Once miss-rate is admitted as a first-class outcome (rather than dropped from the makespan), does the comparative ranking of modes change?
- Q3. **Policy interaction.** Does a STRICT vs GRACE departure policy interact with mode under late-arrival distributions typical of reserve mobilization?
- Q4. **Where do the rankings flip?** Across the controlled disruption-intensity sweep, where (if anywhere) is the break-even line at which multimodal becomes preferred under a chosen resilience criterion (penalized makespan, miss-rate ceiling, or resource-time ratio)?

The output is a *map of conditions*, not a single recommendation.

## 4. Scope, in and out

### In scope

- A named real-world road corridor: **Songpa-gu (Seoul) → 72사단 부곡리 동원훈련장 (경기 양주 장흥 부곡리 산 6-17)**, ≈40–50 km north-northwest, extracted as a major-arterial subset (`motorway`, `motorway_link`, `trunk`, `trunk_link`, `primary`, `primary_link`, `secondary`) of OSM. Connecting expressways (올림픽대로 / 강변북로 / 서울외곽순환) are required.
- **Four origin scenarios** within Songpa-gu, supporting an origin-robustness analysis:
  - (A) 송파구청 일자리센터 앞 (37.5147, 127.1057) — primary, 송파구 조례 2023-09-14 + Hankyung 2024-02-29
  - (B) 삼전동 구민회관 앞 (37.5036, 127.0857) — Hankyung 2024-02-29
  - (C) 장지역 4번 출구 앞 (37.4784, 127.1262) — Hankyung 2024-02-29
  - (D) 잠실종합운동장 (37.5159, 127.0727) — secondary scenario, flagged "출처 미확인 가정 변형"
- The two transport comparators already implemented in the simulator: **bus-only** and **rail–bus multimodal** (the rail leg is treated as an abstract long-distance proxy for the songpa↔의정부/양주 direction, with documented headway / capacity / travel-time assumptions; rail-leg treatment is finalized in `plan.md`).
- A **two-phase paired CRN experimental design**: Phase 1 sweeps disruption intensity and corridor-redundancy variants; Phase 2 sweeps assembly-delay distribution and STRICT vs GRACE departure policy. The four origins (A/B/C/D) are exercised either as a fifth Phase 1 factor or as a focused robustness sweep — to be settled in `plan.md`.
- **Censoring-aware** outcome metrics: completion time, miss-rate (uncompleted personnel under a hard horizon — anchored to 병무청's 12:00 입영 + 1h 지연입소 허용 rule), penalized makespan, road vehicle-hours per person delivered, total mode vehicle-hours per person delivered.
- A **Morris elementary-effects** sensitivity analysis over the published parameter ranges.
- A **reproducibility appendix**: deterministic seeds, manifest, clean-checkout smoke evidence.

### Explicitly out of scope (deferred to follow-up paper)

- Real-world calibration of road capacity, free-flow speed, vehicle counts, headway, transfer time, and rail timetable. Numbers used for the corridor are documented planning assumptions, not source-backed evidence. The repo's 12 blocked formal-acceptance gates remain blocked and the KCI study makes no claim against them.
- Operational route guidance or any siting/routing recommendation for an actual reserve-force movement.
- Any claim about district-level 동원지정 자원 catchment. The 송파→72사단 routing is explicitly **illustrative**; per 병무청, 동원지정 assignments are notified by individual 병력동원소집통지서 and not published as a district map. This is stated in §10.
- External route-time validation against OSRM or KTDB/GTFS rail timetables. These belong to the deferred calibration track.
- Any operational details about 72사단 beyond what 병무청 itself publishes (parent command 육군동원전력사령부, 200/201/202보병연대 composition, 부곡리 동원훈련장 address, 동원훈련 2박3일 / 12:00 입영 / +1h 지연입소 rules). No internal site/gate layout, no end-strength estimates, no wartime-mission specifics.

## 5. Methodological framing

The contribution is positioned as **industrial-engineering / operations-research methodology applied to a defense logistics question**. Three pillars carry the methodological weight, all already implemented in the upstream simulator:

1. **Paired Common Random Numbers** — for each disruption realization, both modes are exercised on the same arrival times, road blockage draws, and BPR background-volume profiles. This isolates structural mode differences from sampling noise and is the foundation for paired CIs and break-even interpolation.
2. **Censoring-aware metric set** — completion time alone is misleading when some personnel fail to arrive within the time horizon. The miss-rate is reported alongside, and a penalized makespan combines them so that "fast but lossy" is not flattered by single-number scoring.
3. **Two-phase experimental design + Morris sensitivity** — Phase 1 isolates road-disruption effects; Phase 2 isolates assembly-delay × policy effects; Morris ranks parameters by effect magnitude and screens for non-linearity, justifying the focus of the manuscript narrative.

The military framing supplies the *significance*; these three pillars supply the *rigor*. The reviewer’s natural first question — "why is this not just civilian transport simulation?" — is answered by the reserve-mobilization scope, the wartime conceptual diagram already authored in the repo, and the resilience criterion (miss-rate under disruption) which is more relevant to a military-logistics evaluator than median completion time.

## 6. Network construction

Inputs:

- A **new** OSM extraction covering the Songpa-gu↔양주 부곡리 corridor. Provisional bbox: **lat 37.46–37.78, lon 126.85–127.20** (final bbox fixed in `plan.md` after a quick OSMnx sanity check). Saved as `data/cache/songpa_yangju_corridor.graphml` plus a JSON manifest. The existing `data/cache/pilot_region_road.graphml` (Songpa only, 4,608 nodes / 9,148 edges) is retained as REFERENCE-ONLY for the legacy abstract-network comparison.
- A new region YAML (`data/regions/songpa_yangju_corridor.yaml`) defining the corridor bbox, the four origin scenarios (A: 송파구청, B: 삼전동 구민회관, C: 장지역, D: 잠실종합운동장), the destination (72사단 부곡리 동원훈련장 at ≈37.74 N / 126.95 E), and abstract rail access/egress points (concrete points to be selected in `plan.md` based on the rail-leg treatment chosen).

Construction steps (specified here, implemented by `plan.md`):

1. Run a fresh OSMnx bbox extraction over the provisional bbox; save to `data/cache/songpa_yangju_corridor.graphml` with manifest.
2. Filter the extracted graph to the major-arterial highway classes listed in §4. Save the filtered cache.
3. Snap the four origins (A/B/C/D), the 부곡리 destination, and rail access/egress points to the nearest arterial node and add bidirectional connector edges, using the existing `realworld.zones` and `realworld.adapter` code paths.
4. Run graph-readiness checks (`realworld.validation.assert_graph_ready`) and an accessibility-loss diagnostic to characterize the corridor’s vulnerability to single-edge removal — particularly on the connecting expressways (올림픽대로 / 강변북로 / 외곽순환), which are likely single-points-of-failure.
5. Confirm that all four origins and the destination remain reachable from each other after the arterial filter; if any node is orphaned, add explicit access connectors.

The rail leg is an abstract long-distance service between an access point near the Songpa origins and an egress point near 부곡리. Headway, per-train capacity, and travel time are documented assumptions, not real timetable data — the closest-reality reference (1호선/7호선/의정부 환승, no direct high-frequency line) is acknowledged in §10. The final treatment (keep abstract, demote to alternative scenario, or drop entirely) is settled in `plan.md`.

## 7. Experimental design

### Phase 1 — disruption sweep

- Factors: disruption intensity (probability and capacity-reduction depth on selected arterials, with focused attention on the connecting expressways), corridor-redundancy variant (baseline vs redundancy-balanced), seed.
- Replications: paired CRN, with the per-cell replication count carried over from the upstream Phase 1 design unless review reveals a justified change.
- **Origin treatment:** the four origins (A: 송파구청, B: 삼전동, C: 장지역, D: 잠실) are exercised either as a fifth Phase 1 factor (full sweep, ~4× cell count) or as a focused robustness check at fewer seeds — settled in `plan.md` based on runtime budget. Either way, results are reported per-origin so that the manuscript can show that the bus-only vs rail–bus ranking is (or is not) robust to origin choice.
- Outcomes: completion time, miss-rate (anchored to 병무청's 12:00 입영 + 1h 지연입소 허용 hard horizon), penalized makespan, road vehicle-hours per person, total mode vehicle-hours per person.

### Phase 2 — policy sweep

- Factors: assembly-delay scale, departure policy (STRICT vs GRACE with two grace windows), seed.
- Replications: paired CRN.
- Outcomes: same metric set as Phase 1.

### Sensitivity — Morris

- Parameters: disruption probability, capacity-reduction depth, fleet size, dispatch headway, transfer delay, rail headway, assembly-delay scale.
- Output: Morris `mu_star` and `sigma` per parameter per outcome metric, with a screening interpretation for the manuscript discussion.

The actual cell counts and parameter ranges are carried forward from the existing simulator design and are documented in the implementation plan, not here. This plan only fixes the shape of the design.

## 8. Expected contributions

The manuscript will claim three contributions, in this order:

1. **A controlled-experiment IE framework** for evaluating personnel-transport resilience under disruption that combines paired CRN, censoring-aware metrics, and Morris sensitivity, applied to a defense-logistics question.
2. **A condition map for reserve-mobilization mode choice** on a major-arterial Songpa virtual corridor, identifying where bus-only and rail–bus rankings flip under joint completion-time / miss-rate criteria.
3. **A reproducible open scaffold** (deterministic seeds, manifest, clean-checkout smoke) for follow-up calibration and regional reuse.

Each contribution is bounded: (1) is methodological and does not claim novelty of any individual technique; (2) is conditional on the documented assumptions; (3) is an enabler, not a result.

## 9. Manuscript outline (target)

| § | Section (Korean / English working title) | Source assets (see `repo_assets_audit.md`) |
|---|---|---|
| 0 | 초록 / Abstract | Distilled from `report_draft.md` summary + this plan §3, §8 |
| 1 | 서론 — 연구 배경과 군사적 의의 | `국defense.md` (military significance), `report_draft.md` 연구 배경 |
| 2 | 선행연구 — 동원·재난 수송 OR 문헌 | `public_github_repo_research.md`, `disrupted_mobilization_resilience_repo_research.md` (extract citations only) |
| 3 | 연구 방법 — 모형, 가상 통로, 실험 설계 | `IMPLEMENTATION_PLAN.md`, `docs/analysis_corridor_method_note.md`, `docs/experiment_design_decision_packet.md`, `docs/sensitivity_diagnostics.md`, this plan §6–§7 |
| 4 | 결과 — Phase 1 / Phase 2 / Morris | `paper/paper_draft.md` results scaffold, `report_draft.md` 주요 결과 |
| 5 | 논의 — 군사적 함의와 의사결정 시사점 | Synthesized from `국방.md` framing |
| 6 | 한계 | This plan §10 |
| 7 | 향후 연구 — 실측 보정 로드맵 | This plan §4 (out-of-scope list reframed as roadmap) |
| 8 | 부록 — 재현성 패키지 | `docs/reproducibility_package.md`, `docs/reproducibility_smoke.md` (consolidated) |

**Figure 1 (concept)** is `전시_예비군_수송체계_시뮬레이션_개념도.png`. **Figures 2–4** are regenerated from the new arterial-corridor results.

## 10. Honest limitations

These limitations are stated up front so the manuscript can pre-empt the reviewer.

- **Major-arterial corridor abstraction.** The road network is a major-arterial subset of OSM extracted over the Songpa↔양주 bbox, not a calibrated traffic model. Road capacity, free-flow speed, and disruption probability are documented planning assumptions; the manuscript states this explicitly and does not dress them up as evidence.
- **Catchment is illustrative.** The Songpa→72사단 routing is chosen as a representative Seoul-southeast → Northern-Gyeonggi 동원훈련장 case. Per 병무청, district-level 동원지정 자원 catchment is conveyed via individual 병력동원소집통지서 and is **not** publicly mapped; the manuscript explicitly states *"실제 동원지정 자원의 행정구역별 배정은 병력동원소집통지서를 통해 개별 고지되며 공개 자료로 검증할 수 없음"* and frames the routing as illustrative.
- **Origin scenario D (잠실종합운동장) is unverified.** Three of the four origins (송파구청, 삼전동, 장지역) are publicly documented (Hankyung 2024-02-29 + 송파구 ordinance 2023-09-14) as 예비군 수송버스 집결지 — though for routine 예비군훈련 to 강동송파, not for 동원훈련 to 72사단. 잠실종합운동장 was included at user request but no public source confirms its use as a 병력동원 집결지; the manuscript flags this as 출처 미확인 가정 변형.
- **Single corridor, single destination.** The conclusions are conditional on this one Seoul→Yangju corridor, one parameterization of fleet / headway / rail service, and the 72사단 destination. Regional reuse is enabled by the framework but not demonstrated within this paper.
- **Abstract rail leg.** No real Korean rail timetable, GTFS, capacity, or disruption is modeled. The closest-reality reference for the songpa↔의정부/양주 direction is a multi-transfer route (1호선/7호선/의정부 환승) without a direct high-frequency line; the manuscript treats rail as an abstract scheduled proxy with documented assumptions.
- **No external validation.** OSRM and other external route-time benchmarks are not used. Calibration is the deferred follow-up paper’s job.
- **Methodological paper, not a planning artifact.** The output is a condition map, not operational guidance. The manuscript states that explicitly in §1, §6, §7. Neither operational details about 72사단 beyond what 병무청 publishes nor any inferences about specific reserve-force movements are claimed.

## 11. Acceptance risks and mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Reviewer rejects "virtual network" as unrealistic for a military journal | Medium | Frame as "arterial corridor abstraction consistent with wartime priority-routing assumptions" in §1; carry the wartime conceptual diagram as Figure 1; lean on §10 to scope claims |
| Reviewer asks "what is novel?" | Medium-High | Position as an IE *framework* contribution (paired CRN + censoring + Morris), not as a single technique; tie novelty to the defense-logistics context |
| Reviewer asks for empirical calibration | Medium | §10 acknowledges; §7 future-work names the exact deferred artifacts; the manuscript explicitly does not over-claim |
| Reviewer asks about Songpa specifically (sensitivity, identifiability) | Low-Medium | Use only public coordinates; reserve-assembly is a synthetic centroid; no real facility named |
| Reviewer questions Morris vs Sobol | Low | Cite the existing sensitivity-method decision packet (REFERENCE-ONLY in audit); justify Morris as screening; Sobol named in future work |
| Korean language and KCI format compliance | Low | Bind to `kci/학회_관련_정보/` rules at draft freeze |
| Length / abstract / reference style mismatch | Low | Same |

## 12. Open decisions (must close before `plan.md`)

Most of the open decisions identified in the v0.1 draft were resolved on 2026-05-11 (see `kci/agents.md` §7). The remaining items still open at the time of this revision:

1. **Final OSM bbox** for the songpa↔양주 corridor. Provisional (lat 37.46–37.78, lon 126.85–127.20) to be tightened in `plan.md` after a quick OSMnx extraction sanity check.
2. **Rail leg treatment.** Keep abstract long-distance rail with hedging, demote rail to alternative scenario, or drop rail entirely — settle in `plan.md` based on whether multimodal remains a meaningful comparator on the songpa↔의정부/양주 axis.
3. **Origin Phase 1 treatment.** Full 4-level factor (~4× cell count) vs focused robustness check at fewer seeds — settle in `plan.md` based on runtime budget.
4. **Authorship and affiliation.** Confirm before any draft circulates. Email on record is `ax_01@kma.ac.kr` (KMA); 국방.md template values are likely outdated.
5. **KCI manuscript template binding** (length, abstract length, keyword count, reference style). Bind at draft freeze using `kci/학회_관련_정보/`.

Resolved decisions (all 16 from the v0.1 audit) are recorded in `kci/agents.md` §7 and should be treated as inputs to `plan.md`.

## 13. Companion documents

- `kci/repo_assets_audit.md` — file-by-file decision (COPY / ADAPT / EXCLUDE / REFERENCE-ONLY) for every relevant path in the upstream repo, synthesized from three parallel audits.
- `kci/plan.md` (to be authored after this plan and the audit are accepted) — implementation steps, sequencing, file moves, code changes, run schedule, and figure/table assembly checklist.
- `kci/학회_관련_정보/` — binding KCI submission rules and templates from the 한국군사학회.
