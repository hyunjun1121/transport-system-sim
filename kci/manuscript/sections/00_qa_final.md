# T5.2 Final QA — manuscript_ko.md (v0.7)

Source: `manuscript/manuscript_ko.md` (96,811 B, 633 L). QA: 2026-05-13.

## G4/G5 Status

| # | Criterion | Status |
|---|---|---|
| 1 | KOR body ≥ 6,000 chars (G5) | PASS (16,391) |
| 2 | ≤ 10 main assets (G4) | PASS (5 fig + 5 tbl) |
| 3 | Origin D caveat (first mention + caption + footnote) | PASS (§1.1 L21, §3.2 L202/204, §3.9 L326, §4.2 box L379, Tbl4 D† L402, §5.3 L545, Fig2 L176) |
| 4 | No orphan citations | PASS (refs 1-25 all cited; all cites defined) |
| 5 | Sign Δ = bus_only − multimodal | PASS (§3 L133/L295, §4 L336, §5 L511) |
| 6 | Morris top-3 (44.5/27.4/20.8) | PASS (abstract L3, §4.5 L472-486, §5.1 L522 = canonical) |
| 7 | Headline numbers identical | PASS (see ledger) |
| 8 | No TODO/FIXME/placeholder | PASS |
| 9 | §4/§5 match Tables 2-6 | PASS (see ledger) |
| 10 | Title matches v0.7 | PASS (L1) |

## Spot-Check Ledger

| # | Claim | Body | Table | Canonical | OK |
|---|---|---|---|---|---|
| 1 | Phase 1a Δ pen_mks @ p=0.0 = −58.5 | L342, L519 | Tbl2 L360 | phase1a_origin_A.csv (−58.51) | Y |
| 2 | Phase 1a Δ P(완료) @ p=2.0 = +0.433 | L344, L519 | Tbl2 L367 | phase1a_origin_A.csv (0.4333) | Y |
| 3 | Phase 2 best-tune Δ @ p=2.0 = −576,348 | L408, L520, L555 | Tbl3 L427-428 | phase2_singlemode.csv (−576347.76) | Y |
| 4 | Phase 3 cells: 0/54/27 | L436, L521 | Tbl6 L452 | table6_lever_conditions_summary.json | Y |
| 5 | Morris top-3 μ* | L472-474, L522 | Tbl5 L484-486 | canonical_morris_top3.md | Y |

## Open Issues

No must-fix items.

Minor (non-blocking): Fig 3 caption cites Δ=−624,352 @ p=2.0 (matches Tbl2 L367). Figure numbering skips 5 by design (1,2,3,4,6 = 5 figs); satisfies G4 ≤ 10-asset rule.

## Verdict

**GO** for KCI submission.
