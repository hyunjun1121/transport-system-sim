# ScholarOne Submission Metadata — IEEE Access

**Verify every field against the manuscript before submitting. Author action items are marked [AUTHOR].**

## Title
Resource Frames, Graph Scope, and Rail States: Conditional Decision Boundaries for Reserve-Force Bus versus Rail–Bus Multimodal Transport

## Article type
Full-length original research article

## Authors (order as in manuscript)
1. **Hyunjun Kim** — Korea Military Academy, Seoul 01805, Republic of Korea; Korea Advanced Institute of Science and Technology (KAIST), Daejeon, Republic of Korea — hyunjun1121@kaist.ac.kr — ORCID 0009-0009-5791-9468
2. **Jae Woo Lee** — Korea Military Academy, Seoul 01805, Republic of Korea; CHA University, Seongnam, Republic of Korea — simonlee98@chauniv.ac.kr — ORCID 0009-0009-8988-1513
3. **Hyunho Kim** — Korea Military Academy, Seoul 01805, Republic of Korea — **corresponding author** — kimhyuh@kma.ac.kr — ORCID 0009-0007-6847-6696

## Keywords
Break-even analysis; common random numbers; discrete-event simulation; multimodal transport; network reduction; reserve-force transport

## Abstract (verbatim from manuscript, 1:1)
Wartime reserve-force transport planning often compares bus-only road movement with rail–bus multimodal movement under disrupted links, yet a modal ranking is uninterpretable unless the resource frame, reduced-graph scope, rail availability state, fleet allocation, and response rule are stated explicitly. This article reports a public-data-based conditional scenario simulation on a Songpa–Goseong case corridor using the Korean Standard Node-Link road network. Top-10 corridor graphs (9,089 nodes; 18,602 edges) are audited against a full reference graph (360,556 nodes; 971,680 edges); road vehicles complete passenger travel, traverse the reverse road network empty, and incur turnaround before reuse; rail is represented by available, degraded, and unavailable service states. Sixteen campaign sets produced 32,790 runs under common-random-number seed blocks with paired t intervals, 10,000-replicate percentile bootstrap intervals, a joint-seed break-even bootstrap with reported valid-replicate counts, a crossed two-way random-threat bootstrap, and Morris elementary-effect screening on completion rate. Under configured resource bundles (23 direct road vehicles versus 46 road vehicles plus rail), mean completion times are 374.1 and 363.8 min and the paired difference includes zero. Under an equal total road fleet of 23 vehicles, the comparison is allocation-conditional: sweeping all 22 feasible feeder/last-mile splits shows a U-shaped surface whose best split (6 feeder + 17 last-mile, 394.6 min) is re-selected on an independent holdout seed block and in every nested-bootstrap resample, and leaves bus-only faster or statistically tied (−20.5 min unresolved on the selection block; −40.7 min [−69.0, −12.4] on the holdout block), while the arbitrary fixed 12/11 split (475.8 min) inflates the bus advantage to −101.7 min. The long-haul road-damage break-even is therefore a band, not a point: splits within 5% of the best mean (a formally defined band, 5–10 feeder vehicles) cross near 1.150–1.277, the fixed 12/11 split at 1.742 (joint-seed interval 1.550–2.003), and a 16-combination joint factorial over rail runtime, headway, transfer delay, and turnaround keeps the best-split crossing inside 1.017–1.451. Full-graph validation reproduces the band endpoints and the fixed-split crossing with overlapping intervals (1.201, 1.280, and 1.761), and a second corridor case (Songpa–Yangyang) replicates the protocol diagnostics with different numbers (audit pattern identical, crossing 1.278 at its own best split). Top-5 and top-10 graphs match full-scope connectivity and policy ranking in the tested conditions, whereas top-3 does not. When rail is unavailable, static multimodal transport does not complete at any tested allocation, while a precheck switching policy recovers bus-level completion at every tested allocation. The contribution is a conditional decision boundary and a reporting protocol for resource frames and graph scope, not a general claim that either mode is superior.

## Data / code availability
- Code + data archive: Zenodo DOI **10.5281/zenodo.23187709**, version `paper-revision-top10-v7-20261006-datacode` (MIT License; 213 files; includes README "Manuscript table to analysis-CSV map").
- Repository: https://github.com/hyunjun1121/transport-system-sim (branch `wartime-bpr-targeting-fix`, tag `ieee-access-submit-v2`, commit `6a7680c3`).

## Funding
[AUTHOR ACTION] No funding statement appears in the manuscript. Confirm in ScholarOne whether to state "This research received no specific grant..." or add a grant number.

## Conflict of interest
[AUTHOR ACTION] No COI statement appears in the manuscript. Confirm "The authors declare no conflict of interest" in ScholarOne.

## Suggested classification / topics
[AUTHOR ACTION] Suggested: Transportation systems; discrete-event simulation; network resilience/reliability; public-sector and military logistics OR (transportation) optimization/simulation. Pick from the IEEE Access subject-area list at submission.

## Cover letter
See `cover_letter.md` (draft for author review; do not submit unedited).
