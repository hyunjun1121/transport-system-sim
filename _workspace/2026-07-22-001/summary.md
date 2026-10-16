# Humanize Korean strict review

- Run: 2026-07-22-001
- Mode: strict follow-up
- Source: `01_input_v2.txt`
- Final: `final.md` (strict round 2)
- Quality: A (`accept_with_note`)
- Findings: S1 0, S2 3 -> S1 0, S2 1
- Weighted score: 12.0 -> 1.0
- Metrics risk: low (score 2) -> low (score 0)
- Round-1 Levenshtein change rate: 10.05%
- Round-2 Levenshtein change rate: 16.36%
- Fidelity audit: full pass in both rounds

주요 변경:

1. 내부 수치와 연구자용 표현을 덜어내고 제3자가 읽을 수 있는 연구 설명으로 바꿨다.
2. 열차 편수, 좌석 공동이용, 버스·운전자 확보 문제를 일상어로 정리했다.
3. 실제 작전계획이나 특정 이동경로를 제시하는 연구가 아니라는 범위를 분명히 했다.
4. 표의 세부 내용은 변수명이 아니라 자문자가 정해야 할 판단으로 표현했다.
5. DOCX 첫 렌더에서 6번 항목만 둘째 페이지로 넘어가 문장을 더 짧게 다듬었다.

잔존 패턴:

- 세부 항목의 `정한다` 반복은 의도적으로 유지했다. 결정사항을 찾는 문서 기능에 필요하며 문장 길이와 내부 구조는 달리했다.

도구 참고:

- 설치본에 `prepare_monolith_input.py`가 없어 `metrics_v2.py`를 직접 실행했다.
- `report` 기준선이 없어 지표 계산은 `essay` 기준선으로 대체됐다.
