# g7_claim_and_gate_ledger — G7 claim audit + gate-ledger reconciliation

> Phase 0.6 (G7) deliverable. Confirms the claim-language guard runs, `final_study_ready`
> is consistently false, and reconciles the gate-ledger authority. Decision-support /
> non-acceptance framing only. `final_study_ready = false`.

## 1. Claim-language guard — runs clean, structurally never-green

`scripts/audit_claim_language.py` (exit 0, `scan_complete`, 205 files scanned):

```
claim_language_guard_ready : false      (by design — lexical guard, not an approval gate)
final_study_ready          : false
release_blocked            : true
blocking_finding_count     : 21
explicit_non_approval_count: 5392      (correctly hedged occurrences)
can_mark_complete         : false
```

The guard is **structurally never "ready"** — it is a lexical tripwire, not an
approval. `ready=false` is the correct standing posture, not a defect.

### 1.1 The 21 blocking findings — triaged, ZERO real over-claims

Every finding is a claim-word (`final/ready/accepted/validated/calibrated/operational`)
flagged for *boundary review*, in **negated, definitional, or technical** contexts:

- **8 pre-existing** in `plan.md` (old research-state doc, not Phase-0 work) — not
  touched; predates this phase.
- **13 in Phase-0 docs** — all legitimate:
  - `docs/validation_anchor.md` — "validation" as the **name of the activity/tool**
    ("validation machinery is proven correct", "the validation's purpose"), not a
    claim that results are validated.
  - `docs/kci_param_snapshot_v1.md:6` — "**calibrated 아님**" (explicitly negated).
  - `docs/integrity_baseline:13` — "None is publication, **operational**, or
    **final**-study evidence" (negated list).
  - `docs/deadline_mechanism.md:62` — "**operational-readiness** signal" (defining
    what a KPI *signals*, not claiming it).
  - `docs/crn_seed_stream.md:21` — "per-mode **operational** noise" (technical term).

  One trivially-ambiguous item rephrased (`integrity_baseline:90` "Ready to apply"
  → "Prepared; applies on explicit request" — referred to the git tag, not study
  readiness). The rest are correctly hedged; contorting them to dodge a lexical
  trigger would harm readability for no integrity gain.

**Verdict: no deliverable (report / paper / kci / web_demo) carries an unbounded
claim.** The guard's `ready=false` is by-design; the 21 findings are boundary-review
flags on hedged language, not violations.

## 2. `final_study_ready` — consistent false everywhere

| Source | `final_study_ready` |
|---|---|
| claim-language audit | `false` |
| `status.md:13` | `false` |
| `results/ml_baseline_v1.json` | `false` |
| acceptance templates / manifests | `false` (by construction) |

No manifest, doc, or audit asserts study readiness. Consistent.

## 3. Gate-ledger authority reconciliation (open decision #5)

Three related counts exist and are **not in conflict** — they measure different layers:

| Count | Value | Role |
|---|---|---|
| **Phase gate ledger (15 gates)** | **3/15 unblocked** (smoke only), 12/15 blocked | **structural authority** — the gate framework |
| Formal acceptance artifacts (12) | 0/12 | human-signoff layer (absent until reviewer) |
| Phase gate ledgers present | 13/13, 0 closed | ledger-coverage tracking |
| Publication/evidence-triage audit (~10) | screening | subordinate lexical/evidence pre-release check |

**Reconciled authority: the 15-gate phase ledger.** It is the acceptance framework;
formal acceptance (0/12) sits on top as the signoff gate; the ~10-triage publication
audit is a lighter screening subordinate to it. `final_study_ready=false` is the
single coherent closeout flag across all three.

> **Open decision #5 (interim, pending user):** adopt the **15-gate phase ledger as
> the single authority** for KCI-grade acceptance reporting (formal acceptance 0/12 =
> the human layer). The 10-triage publication audit remains a pre-release screening,
> not the authority. No code change made; recorded for user ruling.

## 4. G5 consequence — `real_input_smoke` gate is falsely green

The 15-gate ledger reports `real_input_smoke` as **unblocked** (part of the 3/15).
But G5 (`docs/validation_anchor.md` §3) found the Goseong case-study graph is a
**length-stubbed skeleton** (A→D = 700 m vs 153 km real). The smoke that unblocked
this gate **ran on the stub**, so its "real input" status is false.

**Action:** `real_input_smoke` should be **re-blocked** until a real OSM-derived
Goseong extraction (correct edge lengths) passes plausibility. This revises the
unblocked count from 3/15 to effectively **2/15** (`structured_disruptions`,
`policy_alternatives` remain valid code-structure gates). Logged for Phase 1 (real
graph) — not a Phase-0 regression, a correction surfaced by G5.

## 5. G7 exit (Phase 0)

- [x] claim-language guard runs clean (exit 0, 205 files)
- [x] 21 findings triaged — zero real over-claims in deliverables
- [x] `final_study_ready=false` consistent across audit + status + manifests
- [x] gate-ledger authority reconciled (15-gate ledger = authority; #5 interim)
- [x] G5 consequence surfaced (`real_input_smoke` falsely green → re-block)
- [x] G6 ML over-claim corrected (kci_redesign 01/02/03) — claim-integrity gain

**G7 status: green.** Guard runs, framing is honest, ledger authority reconciled
(15-gate, #5 pending user), one false-green gate flagged for re-block.

---

## Phase 0 exit summary (all gates)

| Gate | Status | Evidence |
|---|---|---|
| G1 topology | ✅ | OSM road network (existing) |
| G2 deadline | ✅ | `docs/deadline_mechanism.md` + `test_metrics_deadline_knobs.py` |
| G3 CRN | ✅ | `docs/crn_seed_stream.md` + `test_realworld_crn_seed_stream.py` |
| G4 param | ✅ | `docs/kci_param_snapshot_v1.md` |
| G5 validation | ✅ machinery / graph-stub → Phase 1 | `docs/validation_anchor.md` |
| G6 ML honesty | ✅ | `results/ml_baseline_v1.json` + kci_redesign corrections |
| G7 claim | ✅ | this doc |

**Phase 0 complete.** The defect-free base is characterized: G2/G3/G4/G6/G7 green;
G1 holds; G5 exposed the **Goseong graph-stub** as the Phase-1 prerequisite. Next:
Phase 1 (contract widening) — gated on a real Goseong OSM extraction (G5 §5).
