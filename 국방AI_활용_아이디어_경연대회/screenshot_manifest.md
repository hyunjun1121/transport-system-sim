# 웹 데모 스크린샷 매니페스트

작성일: 2026-05-13

## 1. 캡처 기준

- 캡처 기준 URL: `https://defense-ai-mobility-demo.vercel.app`
- 배포 URL: `https://defense-ai-mobility-demo.vercel.app`
- Vercel deployment: `dpl_EWrut7cVuZJApjZwWEhoY2AJ1Jz5`
- Vercel inspect status: `Ready`
- Vercel inspect timestamp: `Wed May 13 2026 16:38:41 GMT+0900`
- 캡처 도구: `npx playwright screenshot`
- 검증 조건: 각 화면에서 핵심 텍스트 selector가 나타난 뒤 캡처
- 데모 성격: 한국어 기본 공개자료 기반 비작전 의사결정지원 샘플

## 2. 캡처 파일

| 파일 | Viewport | URL/hash | 핵심 확인 텍스트 | 보고서 삽입 용도 |
|---|---:|---|---|---|
| `demo_screenshots/demo_desktop_map_ko.png` | 1440x1000 | `/#map` | `공개자료 기반 비작전 샘플` | 한국어 기본 대표 지도 화면 |
| `demo_screenshots/demo_mobile_map_ko.png` | 390x844 | `/#map` | `공개자료 기반 비작전 샘플` | 한국어 모바일 반응형 확인 |
| `demo_screenshots/demo_data_review_ko.png` | 1440x1000 | `/#data` | `평균 철도-버스 완료시간` | 한국어 KPI/샘플 데이터 화면 |
| `demo_screenshots/demo_evidence_review_ko.png` | 1440x1000 | `/#review` | `근거 검토 작업공간` | 한국어 evidence boundary 화면 |

## 3. 캡처 명령

```powershell
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=공개자료 기반 비작전 샘플" --wait-for-timeout 1000 "https://defense-ai-mobility-demo.vercel.app/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_desktop_map_ko.png"
npx playwright screenshot --browser chromium --viewport-size "390,844" --wait-for-selector "text=공개자료 기반 비작전 샘플" --wait-for-timeout 1000 "https://defense-ai-mobility-demo.vercel.app/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_mobile_map_ko.png"
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=평균 철도-버스 완료시간" --wait-for-timeout 1000 "https://defense-ai-mobility-demo.vercel.app/#data" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_data_review_ko.png"
npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=근거 검토 작업공간" --wait-for-timeout 1000 "https://defense-ai-mobility-demo.vercel.app/#review" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_evidence_review_ko.png"
```

## 4. 해석 경계

스크린샷은 실제 운용 화면, 작전 지시 화면, 최종 승인 결과 화면이 아니다. 보고서에는 "공개자료 기반 비작전 모의 예시"와 "대안별 위험 비교용 의사결정지원 화면"으로만 설명한다.
