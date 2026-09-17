# Ontario Hospital Quality Improvement Explorer

Explore how Ontario hospitals approach emergency department access and patient flow: planned initiatives, reported implementation, intervention categories, hospital differences and reporting quality. The Next.js frontend uses real processed data and preserves original source records.

**No outcome, effectiveness, improvement or target-attainment metrics are calculated or displayed.** Numeric values exist for 129 of 130 matched primary ED cycles, but reporting windows have not been verified as directly comparable. Analyzable outcome rate is **Unavailable**, not 0%.

## Run locally

Node.js 20.9+ and Python 3.12+:

```sh
npm ci
npm run dev
```

Open http://127.0.0.1:3000. The development command exports the processed data automatically. The six routes are Overview, Intervention Explorer, Hospital Explorer, Current Plans, Reporting & Data Quality, and Methodology.

```sh
npm run lint
npm run typecheck
npm test
npm run build
npx playwright install chromium
npm run test:e2e
npm run start
```

`build` creates a static site in `out/`; `start` serves that directory locally. Deploy `out/` to a static host; no database, API key or runtime backend is required. Browser tests use the production build and automatically start a local server if needed.

## Data and architecture

Five Ontario Health QIP CSV exports contain 2024/25, 2025/26 and 2026/27 workplans and 2025/26 and 2026/27 progress reports. Source CSV → reproducible Python pipeline → `data/processed/` → presentation exporter → static JSON and Next.js.

The explorer includes eight reviewed ED indicator definitions: **488 historical idea associations**, **429 current 2026/27 ideas**, and **272 historical hospital–indicator cycles**. It retains both historical pairings but does not interpret their counts as a comparable time trend. The primary 2025/26 → 2026/27 pair contains 206 cycle candidates and 130 accepted matches. Source-wide audits also cover indicators outside this ED subset.

`npm run data:export` reads processed CSVs only, publishes `public/data/explorer.json`, and writes source detail JSON per intervention for loading on demand. The browser payload excludes calculated outcome fields. Zod validates loaded data; pure TypeScript helpers perform filtered counts outside React components. UI uses Tailwind, shadcn-style Radix components, TanStack Table, Recharts and Lucide.

To rebuild the original pipeline:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/build_dataset.py
python scripts/validate_data.py
python scripts/review_taxonomy.py
python -m unittest discover -s tests -v
npm run data:export
```

The source manifest pins schemas, hashes and counts. New source exports require profiling and explicit mapping review. Original CSV bytes remain unchanged.

## Methodology and limitations

- An initiative is one distinct verbatim change-idea association within a hospital–indicator cycle, not necessarily an atomic project. Duplicate detail rows do not increase initiative counts.
- Hospital and indicator normalization uses explicit mappings; ambiguous links remain flagged. Reporting organizations can span multiple sites.
- Deterministic taxonomy rules assign one primary category; Other and source classification evidence remain visible.
- Implementation-status coverage counts Implemented, Not implemented and Conflicting ideas over all selected historical ideas. It measures reporting coverage, not completion. Current plans are separate.
- Fixed source audit counts and filtered ED metrics have separate labels and denominators. Missing values are Unavailable; conflicting implementation is Conflicting. Values are never converted from N/A to zero.
- Submitted performance values are shown only in record details with the comparability notice. No causal claims, effectiveness rankings, predictions or mixed-unit averages are produced.
- CSV exports include stable record/cycle/organization/indicator identifiers and quote formula-like text for spreadsheet safety. Original text remains unchanged in detail JSON.

Read [frontend definitions](docs/frontend-methodology.md), [pipeline methodology](docs/methodology.md), [source profile](docs/data-profile.md), [taxonomy review](docs/taxonomy-review.md), and [reporting-period review](docs/reporting-period-review.md). Earlier outcome-oriented specifications are retained as historical documentation and superseded by the current policy.

## Browser QA and screenshots

Playwright covers all six pages at 1440px, 1024px and 390px, filter persistence, empty states, table sorting/visibility/CSV export, source details, error retry, tooltips, page overflow, console errors and automated accessibility checks. See [QA report](docs/frontend-qa.md).

[Desktop screenshot](docs/screenshots/desktop.png) · [1024px screenshot](docs/screenshots/tablet.png) · [Mobile screenshot](docs/screenshots/mobile.png)
