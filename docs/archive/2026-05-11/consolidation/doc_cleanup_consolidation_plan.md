# `docs` 정리 실행 계획 (2026-05-11)

## 1단계: 확정 적용 (완료)
- 불필요한 consultation 요청/응답/검토 파일 삭제: `docs/expert_consultation_request.md`,
  `docs/expert_consultation_request_reply.md`, `docs/expert_consultation_followup_plan.md`,
  `docs/expert_verification_request.md`.
- `docs/draft_acceptance/final_study_audit.placeholder.md` 삭제(외부 참조 0개).
- 리뷰 아카이브 이동: `docs/expert_review_cycle_archive_20260511.md` ->
  `docs/archive/2026-05-11/expert_review_cycle_archive_20260511.md`.
- 스키마 문서 묶음 이동: 14개 `*_schema.md`를 `docs/schemas/`로 통합.
  - 대상: `experiment/ final_audit/ graph_scale/ manuscript/ parameter/ pilot/
    provenance/ rail_*_cache/ reproducibility/ road_class_override/
    sensitivity/ validation` 스키마 군.
- 경로 레퍼런스 전체 갱신: 코드/테스트/매니페스트/실행계획 문서에서
  `docs/<schema>.md` → `docs/schemas/<schema>.md`로 변경.
- 새 가이드 문서 추가: `docs/schemas/README.md`.

## 2단계: 정리 잔여 항목 (진행)
- `docs/review_packets/*` 패킷 문서 집약 전략:
  - `docs/review_packets/`는 유지하되, 1개 인덱스 허브(`docs/review_packets/README.md`)를
    신설하고, 패킷별 상태를 패킷 헤더에 통일.
- `docs` 루트의 단독 패킷/검토 메모 성격 문서(`region_reuse_checklist.md`,
  `publication_readiness_audit.md`, `accessibility_loss_analysis.md`,
  `route_road_evidence_exposure.md`, `formal_target_placeholder_relocation.md`,
  `osm_graph_snapshot_review_packet.md`, `formal_target...` 등) 우선순위 기반으로
  "deprecated index" 반영.
- 스키마 이동이 아닌 진짜 폐기 후보(필드 증거 기준: 더 이상 참조·출력·검증 경로 미사용)가
  확인되면 삭제 또는 `docs/archive/<date>/`로 이관.
- Expert review handoff 생성 로직에서 비활성화된 consultation 문서를 사이드카 필수 항목에서
  분리하고, 존재하지 않을 경우 생략되도록 조정 완료.

## 3단계: 품질 게이트
- 변경된 경로에 대한 스모크 확인:
  - `rg -n "docs/schemas/*.md"` 및 `rg -n "docs/<이동전 경로>"`로 잔류 여부 점검.
  - 핵심 스크립트/테스트  (`test_realworld_parameter_acceptance.py`,
    `test_realworld_source_context_cache_decision_packet.py`) 실행 후 통과 확인.

## 4단계: 릴리즈 준비 체크
- `docs/schemas/README.md`와 `docs/tracked_artifact_audit.md`에 아카이브/통합 현황을
  반영.
- 최종적으로 사용자 요청 범위(`docs`만 정리) 바깥 경로(임시 산출물)은 필요 시
  별도 정리 브랜치에서 처리.
