# Policy Feasibility and Fairness Table

Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance.

## Verdict

- Publication ready: `false`
- Can mark complete: `false`
- Rows: 8
- Status counts: `{'blocked_current_policy_no_effect': 1, 'blocked_excluded_until_documented_corridor': 1, 'deterministic_dispatch_variant_not_adaptive_routing': 1, 'proxy_comparator_ready_for_engineering_compact_only': 2, 'resource_sensitivity_ready_for_engineering_compact_only': 2, 'stress_sensitivity_only': 1}`

## Rows

| Row | Key Status | Claim Boundary |
| --- | --- | --- |
| bus_only | proxy_comparator_ready_for_engineering_compact_only | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| baseline_multimodal | proxy_comparator_ready_for_engineering_compact_only | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| multimodal_lastmile_redundancy | resource_sensitivity_ready_for_engineering_compact_only | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| staggered_or_adaptive_dispatch | deterministic_dispatch_variant_not_adaptive_routing | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| multimodal_increased_feeder_capacity | resource_sensitivity_ready_for_engineering_compact_only | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| bus_corridor_redundancy | blocked_excluded_until_documented_corridor | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| rail_delay_or_partial_unavailability | stress_sensitivity_only | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |
| fleet_shortage_stress | blocked_current_policy_no_effect | Phase 8 pre-compact review table only; not policy acceptance, not validation acceptance, not calibrated real-world evidence, not final-study approval, and not operational routing or dispatch guidance. |

## Boundary

- This table is a Phase 8 pre-compact guardrail.
- It cannot close validation, policy, publication, final-study, or formal acceptance gates.
- Any compact result that violates these rows remains exploratory unless rerun after review.
