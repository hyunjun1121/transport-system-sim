# URL Rename and Korean/English Toggle Plan

Date: 2026-05-13

## 1. Goal

Update the deployed web demo so that both the public URL and the in-app language
experience fit the defense AI competition context.

Required outcomes:

- Replace the previous generic production alias with a
  competition-appropriate URL.
- Add a Korean/English language toggle to `web_demo`.
- Make Korean the default language.
- Preserve the current non-operational, public-data, sample/scaffold boundary in
  both Korean and English.
- Update report-side references after the URL changes.
- Re-capture screenshots after language and URL changes.

## 2. Source Research Summary

Vercel domain behavior:

- Vercel automatically assigns deployments a `.vercel.app` domain based on the
  project name, and these deployment URLs are first-come, first-served.
- Vercel project names must be lowercase and can include letters, digits, `.`,
  `_`, and `-`, but cannot contain `---`.
- A project name can be changed in the Vercel dashboard under project settings
  > General.
- A custom domain or subdomain can be assigned under project Settings > Domains.
  Subdomains are configured with CNAME records; apex domains use A records.
- The Vercel CLI supports `vercel domains add [domain] [project]` for adding a
  domain to a Vercel project.

React/i18n behavior:

- `react-i18next` binds i18next to React through `initReactI18next`.
- i18next supports language switching through `i18next.changeLanguage(lng)`.
- For this app, browser language detection should not decide the initial
  language, because the product requirement is "default Korean". Persisted user
  choice may override Korean after the first manual toggle.

Primary references:

- Vercel working with domains:
  `https://vercel.com/docs/domains/working-with-domains`
- Vercel project rename guidance:
  `https://vercel.com/kb/guide/how-do-i-change-the-name-of-my-vercel-project`
- Vercel general settings:
  `https://vercel.com/docs/project-configuration/general-settings`
- Vercel domains CLI:
  `https://vercel.com/docs/cli/domains`
- react-i18next instance:
  `https://react.i18next.com/latest/i18next-instance`
- i18next API:
  `https://www.i18next.com/overview/api`

## 3. URL Naming Decision

### 3.1 Preferred URL

Use a short ASCII URL that explains the competition context without implying
operational deployment:

```text
https://defense-ai-mobility-demo.vercel.app
```

Rationale:

- `defense-ai` directly matches the competition context.
- `mobility` is broader and safer than "operation", "dispatch", or "command".
- `demo` clearly marks it as a demonstration, not a production system.
- It remains readable in a report and screenshot caption.

### 3.2 Fallback URL Candidates

If the preferred `.vercel.app` name is unavailable, use the first available
fallback:

1. `https://defense-ai-transport-demo.vercel.app`
2. `https://ai-move-defense-demo.vercel.app`
3. `https://defense-ai-decision-demo.vercel.app`
4. `https://suseo-pyeongtaek-ai-demo.vercel.app`

Avoid:

- Names with `ops`, `command`, `dispatch`, `battle`, `mission`, or `route-plan`.
- Names that imply final approval or live operation.
- Korean characters in the URL slug.

### 3.3 URL Change Procedure

Use one of the two tracks below.

Track A: `.vercel.app` project/domain rename

1. Check the current Vercel project with:

   ```powershell
   npx vercel inspect <previous-production-url>
   ```

2. In Vercel dashboard, rename the project from `web_demo` to
   `defense-ai-mobility-demo` if available.
3. Add or confirm the production domain:

   ```powershell
   npx vercel domains add defense-ai-mobility-demo.vercel.app defense-ai-mobility-demo
   ```

4. Redeploy from `web_demo/`:

   ```powershell
   npm run lint
   npm run build
   npx vercel deploy --prod --yes
   npx vercel inspect https://defense-ai-mobility-demo.vercel.app
   ```

5. Verify HTTP 200:

   ```powershell
   (Invoke-WebRequest -Uri "https://defense-ai-mobility-demo.vercel.app/#map" -UseBasicParsing).StatusCode
   ```

Track B: owned custom subdomain

If a domain is already owned, prefer a report-grade subdomain such as:

```text
https://mobility-demo.<owned-domain>
https://defense-ai-demo.<owned-domain>
```

Then add it in Vercel project Settings > Domains and configure DNS:

- Subdomain: CNAME to the Vercel-provided target.
- Apex domain: A record as shown by Vercel.

Track B is cleaner for a formal submission, but Track A is sufficient if the
goal is a quickly shareable Vercel demo URL.

## 4. Korean/English Toggle Design

### 4.1 Implementation Approach

Use `i18next` + `react-i18next` rather than ad hoc conditional strings.

Install:

```powershell
cd web_demo
npm install i18next react-i18next
```

Do not add browser-language detection initially. The default must be Korean, so
the app should use:

```ts
lng: savedLanguage ?? 'ko'
fallbackLng: 'ko'
supportedLngs: ['ko', 'en']
```

Persist manual changes in `localStorage`, for example:

```text
web_demo_language=ko
web_demo_language=en
```

### 4.2 File Structure

Add:

```text
web_demo/src/i18n/index.ts
web_demo/src/i18n/resources.ts
web_demo/src/i18n/types.ts
web_demo/src/components/language/LanguageToggle.tsx
```

Update:

```text
web_demo/src/main.tsx
web_demo/src/App.tsx
web_demo/src/components/layout/TopBar.tsx
web_demo/src/components/layout/Sidebar.tsx
web_demo/src/components/map/OperationalMap.tsx
web_demo/src/components/panels/CommandDashboard.tsx
web_demo/src/components/panels/DataWorkspace.tsx
web_demo/src/components/review/EvidenceReviewWorkspace.tsx
web_demo/README.md
web_demo/demo_map_spec.md
국방AI_활용_아이디어_경연대회/*.md
국방AI_활용_아이디어_경연대회/지원서식_국방AI_활용_아이디어_경연대회.txt
```

### 4.3 Translation Namespace Plan

Use one namespace at first, split only if the file becomes too large.

Suggested key groups:

```text
app.*
nav.*
topbar.*
map.*
dashboard.*
data.*
review.*
common.*
boundary.*
```

Examples:

```ts
topbar.title.ko = "국방 AI 비상 수송 의사결정 데모"
topbar.title.en = "Defense AI Mobility Decision Demo"

map.notice.ko = "공개자료 기반 비작전 샘플입니다. 표식은 권역 라벨이며 실제 집결·배차·승인 증거가 아닙니다."
map.notice.en = "Public-data, non-operational sample. Markers are generalized area labels, not pickup orders, dispatch guidance, or accepted field evidence."
```

### 4.4 Language Toggle UX

Place a compact segmented toggle in `TopBar` near the right side:

```text
[한국어] [English]
```

Behavior:

- Default: Korean.
- On click: call `i18n.changeLanguage('ko' | 'en')`.
- Persist selected language in `localStorage`.
- Keep `#map`, `#data`, `#review` routing unchanged.
- Do not reload the page.
- On mobile, show a compact `KO / EN` toggle and hide nonessential status
  badges first.

### 4.5 Text Migration Order

Migrate UI text in this order to reduce broken screens:

1. TopBar and Sidebar labels.
2. Map title, legend, notices, marker labels, KPI footer.
3. Dashboard cards, scenario copy, action labels.
4. Data workspace headings, metric labels, table aliases.
5. Evidence review queue, audit notes, package context.
6. README/demo spec/report screenshots references.

Do not translate raw CSV field names unless they are presented as user-facing
column labels. Keep data keys stable.

## 5. Korean Default Copy Direction

Default Korean screen should read as a polished competition demo, not a direct
machine translation.

Preferred Korean labels:

- App title: `국방 AI 비상 수송 의사결정 데모`
- Short mobile title: `국방AI 수송 데모`
- Sidebar:
  - `의사결정 센터`
  - `시나리오 지도`
  - `시뮬레이션 데이터`
  - `근거 검토`
- Map scenario: `서울/수서-평택지제 지원 수송 시나리오`
- Safety note:
  `공개자료 기반 비작전 샘플입니다. 표식은 권역 라벨이며 실제 집결·배차·승인 증거가 아닙니다.`
- KPI boundary: `비작전 검토용 샘플`

English mode should preserve the current wording, with minor cleanup only.

## 6. Report and Screenshot Dependencies

URL rename and i18n affect report-side assets. After implementation:

1. Redeploy the web demo.
2. Update all report URLs from the previous generic URL to the new URL.
3. Capture screenshots in Korean default mode:

   ```powershell
   npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=공개자료 기반 비작전 샘플" --wait-for-timeout 1000 "<new-url>/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_desktop_map_ko.png"
   npx playwright screenshot --browser chromium --viewport-size "390,844" --wait-for-selector "text=공개자료 기반 비작전 샘플" --wait-for-timeout 1000 "<new-url>/#map" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_mobile_map_ko.png"
   npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=시뮬레이션 데이터" --wait-for-timeout 1000 "<new-url>/#data" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_data_review_ko.png"
   npx playwright screenshot --browser chromium --viewport-size "1440,1000" --wait-for-selector "text=비작전 검토" --wait-for-timeout 1000 "<new-url>/#review" "국방AI_활용_아이디어_경연대회\demo_screenshots\demo_evidence_review_ko.png"
   ```

4. Optional: capture English mode screenshots only if the final report wants to
   show bilingual support.
5. Update:

   ```text
   국방AI_활용_아이디어_경연대회/screenshot_manifest.md
   국방AI_활용_아이디어_경연대회/demo_reference_paragraphs.md
   국방AI_활용_아이디어_경연대회/final_report_draft.md
   국방AI_활용_아이디어_경연대회/지원서식_국방AI_활용_아이디어_경연대회.txt
   ```

## 7. Sub-Agent Dependency Plan

This work should be split by ownership, but the outputs are not independent.
The dependency order below is the controlling plan.

### 7.1 Sub-Agent Roles

| Sub-agent | Ownership | Inputs | Outputs | Can run in parallel? |
|---|---|---|---|---|
| Domain Agent | Vercel project name, `.vercel.app` alias, optional custom domain | Current Vercel project, URL candidate list | Confirmed new public URL or fallback decision | Yes, after URL naming decision |
| I18n Core Agent | `package.json`, `src/i18n/*`, `src/main.tsx` | Current React/Vite app, Korean default requirement | i18next setup, Korean default, persisted manual toggle state | Yes, after language architecture decision |
| Copy/Translation Agent | Korean and English translation resources | Current UI text, non-operational wording rules | `ko`/`en` translation keys for all visible UI copy | Yes, after i18n key schema is fixed |
| UI Integration Agent | TopBar, Sidebar, Map, Dashboard, Data, Review components | I18n Core output, translation resources | Components using translation keys and language toggle | No; depends on I18n Core and Copy/Translation |
| Layout QA Agent | Desktop/mobile layout behavior | UI Integration output | Overflow fixes, 390px mobile-safe toggle and labels | No; depends on UI Integration |
| Deployment Agent | Production deployment and Vercel inspect | Passing lint/build, Domain Agent output | Ready production URL and HTTP 200 check | No; depends on UI Integration and Layout QA |
| Screenshot Agent | Korean default screenshots and optional English screenshots | Ready production URL | Updated screenshot files and manifest commands | No; depends on Deployment |
| Report Update Agent | Competition report docs and submission TXT | Ready URL, screenshot files, manifest | Updated URL, screenshot references, bilingual demo wording | No; depends on Screenshot |
| Final QA Agent | End-to-end verification and git state | All prior outputs | Final checklist, stale URL/text search, clean commit/push readiness | No; runs last |

### 7.2 Dependency DAG

```text
URL Naming Decision
  -> Domain Agent
  -> Deployment Agent
  -> Screenshot Agent
  -> Report Update Agent
  -> Final QA Agent

Language Architecture Decision
  -> I18n Core Agent
  -> UI Integration Agent
  -> Layout QA Agent
  -> Deployment Agent

Language Architecture Decision
  -> Copy/Translation Agent
  -> UI Integration Agent

Non-Operational Claim Boundary
  -> Copy/Translation Agent
  -> UI Integration Agent
  -> Report Update Agent
  -> Final QA Agent
```

### 7.3 Critical Path

The critical path is:

```text
Language Architecture Decision
-> I18n Core Agent
-> Copy/Translation Agent
-> UI Integration Agent
-> Layout QA Agent
-> Deployment Agent
-> Screenshot Agent
-> Report Update Agent
-> Final QA Agent
```

The Domain Agent can run early, but it does not unblock UI work unless the URL
choice affects report copy. The actual report URL cannot be finalized until
Deployment Agent confirms the production alias is ready.

### 7.4 Parallel Work Windows

Allowed parallelism:

1. After the URL naming decision, Domain Agent can check or configure the
   preferred Vercel URL while I18n Core Agent prepares localization plumbing.
2. After the translation key schema is fixed, Copy/Translation Agent can write
   Korean/English resources while I18n Core Agent finishes integration setup.
3. After UI Integration starts, Layout QA Agent may review likely overflow risks
   from diffs, but it cannot mark layout safe until a browser screenshot exists.

Blocked work:

- Screenshot Agent must wait for Deployment Agent.
- Report Update Agent must wait for Screenshot Agent and the final public URL.
- Final QA Agent must wait for report updates, screenshots, lint/build, Vercel
  inspect, stale URL search, and language-toggle browser checks.

### 7.5 Handoff Gates

Gate 1: URL Gate

- Preferred or fallback URL selected.
- Vercel project/domain operation has a concrete result.
- Old generic URL remains only until the replacement is verified.

Gate 2: I18n Schema Gate

- Translation key groups are fixed.
- Korean default policy is implemented without browser detection.
- `localStorage` key behavior is documented.

Gate 3: UI Integration Gate

- Every visible component uses translation keys for user-facing text.
- Raw data keys remain stable.
- Korean and English both preserve the non-operational boundary.

Gate 4: Layout Gate

- Desktop screenshot shows no clipped language toggle.
- 390px mobile screenshot shows no title, toggle, or status overlap.
- Map legend, KPI footer, and evidence notes remain readable in Korean.

Gate 5: Deployment Gate

- `npm run lint` passes.
- `npm run build` passes.
- Vercel production deployment is `Ready`.
- New URL returns HTTP 200.

Gate 6: Evidence Gate

- Korean default screenshots exist and are captured from the new URL.
- Screenshot manifest records selectors, viewport sizes, and URL.
- Report docs and submission TXT reference the new URL and screenshot names.

Gate 7: Final Gate

- Search checks find no stale old generic URL, placeholder URL, local dev URL,
  or deprecated AI-branding text in final-facing files.
- Git working tree is clean after commit and push.

## 8. Verification Checklist

Run these before committing:

```powershell
cd web_demo
npm run lint
npm run build
npx vercel deploy --prod --yes
npx vercel inspect <new-url>
```

Browser checks:

- Default load at `<new-url>/#map` is Korean.
- Toggle to English changes visible text without losing route/hash state.
- Toggle back to Korean restores Korean text.
- Refresh after selecting English preserves English only if user manually chose
  English.
- Fresh localStorage or incognito defaults to Korean.
- Desktop and mobile top bars do not clip the language toggle.
- Map labels and safety notices remain non-operational in both languages.
- Data table renders after language switch.
- Evidence review screen still states that formal acceptance is not complete.

Search checks:

```powershell
rg -n "<old-url-slug>|<placeholder-url>|<local-dev-url>" web_demo "국방AI_활용_아이디어_경연대회"
rg -n -i "<deprecated-ai-branding>" web_demo "국방AI_활용_아이디어_경연대회"
```

Expected:

- No stale old generic URL remains after the new URL is confirmed.
- No placeholder, local dev URL, or deprecated AI-branding text appears in final-facing files.

## 9. Commit Plan

Use two commits if the URL/domain operation and i18n implementation are
separated:

1. `feat: add korean english demo localization`
2. `chore: update competition demo url`

If implemented in one pass:

```powershell
git add .
git commit -m "feat: localize competition demo"
git push origin main
```

## 10. Risks and Controls

| Risk | Control |
|---|---|
| Preferred `.vercel.app` URL unavailable | Try fallback list in order and record the final selected URL. |
| Vercel preview domain requires auth | Use the public production alias only in reports and screenshots. |
| Browser language detection overrides Korean | Do not use language detector in v1; default to Korean unless saved user preference exists. |
| Some UI text remains hard-coded English | Run `rg` for old English phrases and inspect every component. |
| Korean text overflows mobile top bar | Keep short mobile labels and verify 390px screenshot. |
| Report references stale URL or old English screenshots | Update report docs only after deployment and recapture screenshots. |

## 11. Acceptance Criteria

The work is complete only when all criteria pass:

- New public URL is competition-appropriate and accessible with HTTP 200.
- All report files reference the new URL.
- Default page load is Korean.
- Language toggle switches between Korean and English without reload.
- Korean and English screens both preserve the non-operational/scaffold boundary.
- `npm run lint` passes.
- `npm run build` passes.
- Vercel deployment is `Ready`.
- Korean desktop/mobile screenshots exist and match the new URL.
- Git working tree is clean after commit and push.
