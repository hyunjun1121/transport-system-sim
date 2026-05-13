# Figure 5 — Origin robustness (Δ penalized_makespan)

**제목.** Origin robustness — Δ penalized_makespan by origin candidate.

**해석.** 본 그림은 출발지 후보 4종(A: 잠실역 — 본문 기준, R=10; B: 한강 르네상스/코엑스, R=5; C: 잠실대교 남단, R=5; D: 잠실종합운동장, R=5)에 대해 공통 그리드 셀(s∈{1.0, 1.5} × p∈{0.0, 1.0, 2.0})에서의 Δ penalized_makespan 평균과 95% 신뢰구간(정규 근사)을 비교한다. 동일 셀에서 네 후보가 거의 같은 부호와 크기를 보이면, 본문 결과가 출발지 선택에 강건함을 시사한다.

**Origin D 주의(중요).** Origin D(잠실종합운동장)는 공개 자료에서 사용자가 요청한 출처(연구계획 부속자료)가 확인되지 않은 가정치이며, 본문 분석에는 사용하지 않았다. 그림에서는 빨간 테두리·해치(///)·연한 채움 색으로 시각적으로 분리해 표시했으며, 범례 또한 "D — 출처 미확인 가정"으로 표기한다. 본 그림에서의 포함은 오직 **민감도/강건성 점검(robustness variant)** 목적이며, 본문 수치·결론은 A(잠실역)에 한정된다.

**기타 주.** Δ = (bus-only) − (multi-modal). 음(−)의 값은 multi-modal 대안이 더 큰 penalized_makespan을 보임을 뜻한다. p=1.0 이상에서 발생하는 완전 실패(failure) 케이스는 penalized_makespan 페널티(=1,441,440 분)로 들어가며, 본 집계에서 비유한값(±inf)은 사전 제거 후 평균·CI를 계산했다.
