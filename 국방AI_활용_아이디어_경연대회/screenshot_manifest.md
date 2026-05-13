# 웹 데모 스크린샷 매니페스트

작성일: 2026-05-13

## 1. 캡처 기준

- 캡처 기준 URL: `https://webdemo-fawn.vercel.app`
- 배포 URL: `https://webdemo-fawn.vercel.app`
- Vercel deployment: `dpl_8tgWEnLGyNtaWzAvpZKCuTfy5rVe`
- Vercel inspect status: `Ready`
- Vercel inspect timestamp: `Wed May 13 2026 14:36:59 GMT+0900`
- 캡처 도구: `npx playwright screenshot`
- 검증 조건: 각 화면에서 핵심 텍스트 selector가 나타난 뒤 캡처
- 데모 성격: 공개자료 기반 비작전 의사결정지원 샘플

## 2. 캡처 파일

| 파일 | Viewport | URL/hash | 핵심 확인 텍스트 | 보고서 삽입 용도 |
|---|---:|---|---|---|
| `demo_screenshots/demo_desktop_map.png` | 1440x1000 | `/#map` | `Public-data, non-operational sample` | 대표 지도 화면 |
| `demo_screenshots/demo_mobile_map.png` | 390x844 | `/#map` | `Public-data, non-operational sample` | 모바일 반응형 확인 |
| `demo_screenshots/demo_data_review.png` | 1440x1000 | `/#data` | `AVG RAIL-BUS MAKESPAN` | KPI/샘플 데이터 화면 |
| `demo_screenshots/demo_evidence_review.png` | 1440x1000 | `/#review` | `Non-operational review context` | evidence boundary 화면 |

## 3. 캡처 명령

```powershell
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=Public-data, non-operational sample" --wait-for-timeout 1000 "https://webdemo-fawn.vercel.app/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_desktop_map.png"
npx playwright screenshot --browser chromium --viewport-size "390,844" --wait-for-selector "text=Public-data, non-operational sample" --wait-for-timeout 1000 "https://webdemo-fawn.vercel.app/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_mobile_map.png"
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=AVG RAIL-BUS MAKESPAN" --wait-for-timeout 1000 "https://webdemo-fawn.vercel.app/#data" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_data_review.png"
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=Non-operational review context" --wait-for-timeout 1000 "https://webdemo-fawn.vercel.app/#review" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_evidence_review.png"
```

## 4. 해석 경계

스크린샷은 실제 운용 화면, 작전 지시 화면, 최종 승인 결과 화면이 아니다. 보고서에는 "공개자료 기반 비작전 모의 예시"와 "대안별 위험 비교용 의사결정지원 화면"으로만 설명한다.
