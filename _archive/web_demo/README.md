# Transport System Simulation Web Demo

React, TypeScript, Vite, BlueprintJS, TailwindCSS, Leaflet, Papa Parse, and
react-i18next demo for the disrupted regional transport simulation project.

This is a visual decision-support demo for the single Seoul/Suseo to
Pyeongtaek-Jije/Pyeongtaek support-zone sample scenario. It is not an
operational route plan, real-world forecast, automated command system, or final
acceptance record.

Production URL:

```text
https://defense-ai-mobility-demo.vercel.app
```

The default language is Korean. The top bar includes a Korean/English toggle for
reviewers who want to inspect the same non-operational demo boundary in English.

## Run Locally

```powershell
npm ci
npm run dev
```

## Validate

```powershell
npm run lint
npm run build
```

## Data Inputs

- `public/data/config.yaml`: copied scenario configuration used by the map view.
- `public/data/phase1_results.csv`: sample phase 1 output used by the data view.
- `src/i18n/resources.ts`: Korean and English UI copy.

## Scope Notes

- Claims in the UI must stay within research-prototype and scaffold evidence
  boundaries.
- The project status remains `final_study_ready=false` until formal acceptance
  gates are closed by source-backed human review.
- The web app should present bus-only and rail-bus outputs as comparative
  simulation samples, not accepted operational recommendations.
- Map markers are generalized area-level labels for report screenshots; they
  must not be treated as actual pickup, dispatch, or facility locations.
