# Frontend QA — 2026-09-17

The production static export was tested in Chromium using Playwright.

## Completed checks

- ESLint: passes, no warnings.
- TypeScript: passes.
- Vitest: 13 tests pass, including real exported data contracts, cohort separation, cycle deduplication, unavailable denominators, implementation conflicts and CSV formula protection.
- Existing Python pipeline suite: 28 tests pass, including source reconstruction and reproducible builds.
- Production build: passes; all six requested routes are statically generated.
- Playwright: five smoke tests cover all six pages at 1440px, 1024px and 390px, plus detailed interaction and failure/retry scenarios.
- Axe WCAG 2 A/AA automated checks: no violations across the six pages at each tested viewport.
- Browser console: no errors or warnings in the normal page tests. Deliberately injected HTTP 503 responses are tested separately.

## Browser coverage

Navigation and active-page state; persistent fiscal-year/region filters; historical-cohort chart drill-down; current-plan empty selections; unavailable coverage when no historical denominator exists; chart and KPI tooltips; exact-count tables; horizontal table scrolling; search; sorting; column visibility; pagination controls; CSV download; source Sheet loading, raw fields and comparability notice; initial-data and source-detail error/retry states.

Page overflow was checked at each viewport. Scrollable audit and documentation tables were made keyboard-focusable. Chart labels were reviewed in screenshots and changed from truncated strings to wrapped labels; tooltips and exact-count tables retain the complete names. Source detail tables show original reported values without calculated differences.

## Analytical contract

The presentation export contains 917 ED idea associations: 488 historical and 429 current. It contains 272 retained historical cycles, with 206 candidates, 130 matches and 129 numeric pairs in the primary 2025/26 → 2026/27 window. Those are data-presence diagnostics. The UI calculates no outcome/effectiveness/target-attainment aggregates. Source-wide audit counts and filtered ED metrics have separate, explicit denominators.

Screenshots: [1440px](screenshots/desktop.png), [1024px](screenshots/tablet.png), [390px](screenshots/mobile.png). The full test definition is `tests/e2e/explorer.spec.ts`.

Optional Python Ruff/Mypy checks could not run because those tools are not installed in the active Python environment. Frontend lint/typecheck and the existing Python test suite passed.
