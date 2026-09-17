# Verified ED indicator metadata

Reviewed 2026-09-16. All eight exact V1 ED identities have an officially verified direction, unit, population definition and published reporting-period information. They are definition-eligible for outcomes, conditional on cycle-level verification. No cycle is eligible merely because its indicator is verified.

| Display name | Direction | Unit | Comparable population (abridged) | 2025/26 page | 2026/27 page |
| --- | --- | --- | --- | ---: | ---: |
| Ambulance offload (90th percentile) | lower_is_better | minutes | Unscheduled ambulance arrivals; valid arrival/transfer timestamps | 7 | 9 |
| Time to physician assessment (90th percentile) | lower_is_better | hours | Unscheduled ED visits assessed by a physician | 8 | 10 |
| Patients awaiting a bed at 8 a.m. (daily average) | lower_is_better | patients_per_day | Unscheduled admitted ED patients still waiting at 8 a.m.; disposition wait exceeds two hours | 9 | 11 |
| Nonadmitted ED stay, CTAS 4–5 (90th percentile) | lower_is_better | hours | Unscheduled nonadmitted ED visits, CTAS 4–5; excludes LWBS | 11 | 12 |
| Nonadmitted ED stay, CTAS 1–3 (90th percentile) | lower_is_better | hours | Unscheduled nonadmitted ED visits, CTAS 1–3; excludes LWBS | 13 | 13 |
| Admitted ED stay (90th percentile) | lower_is_better | hours | Unscheduled ED visits resulting in admission; excludes LWBS | 10 | 14 |
| Disposition to inpatient bed (90th percentile) | lower_is_better | hours | Unscheduled ED visits resulting in admission | 15 | 15 |
| ED visits leaving without physician assessment | lower_is_better | percent | Unscheduled ED visits; numerator dispositions 61/63, excludes 62/64 | 16 | 16 |

Sources: [Ontario Health 2025/26 specifications](https://www.hqontario.ca/Portals/0/documents/qi/qip/2025-26-QIP-technical-specifications-en.pdf) and [2026/27 specifications](https://qipnavigator.hqontario.ca/portals/0/documents/qi/qip/2025/Technical%20Specifications%20EN.pdf). Consult the linked pages for full inclusion/exclusion criteria. Machine-readable source-exact mappings, display labels and metadata live in `config/indicator_metadata.json` and are exported in `indicators.csv`.

## Published windows

| Definition group | 2025/26 workplan current-performance window | 2026/27 published current-performance window |
| --- | --- | --- |
| Six ED time measures | ERNI: 2023-12-01–2024-11-30; non-ERNI: 2024-04-01–2024-09-30 | 2024-12-01–2025-11-30 |
| 8 a.m. backlog and LWBS | 2024-04-01–2024-09-30 | 2024-04-01–2025-03-31 |

These are documented defaults, not automatically assigned observation dates. The backlog unit is a daily average patient count (`patients_per_day`); raw `Number` remains normalized as `count` without rescaling. PIA, LOS and inpatient-bed waiting measure different intervals. CTAS groups remain distinct. LWBS display wording is mapped explicitly to its existing source-exact Percent label; no additional local variants are merged.

The legacy nonspecific `90th percentile ED length of stay` remains outside V1 with direction `unknown`, definition unverified and indicator outcome eligibility false. Other unreviewed local indicators retain unknown verification fields. Existing non-ED wording interpretations are documented separately and do not grant calculation eligibility.

See [reporting-period-review.md](reporting-period-review.md) for record-level flags, exceptions and the reason no current comparison passes every gate. Eight verified definitions does not mean eight indicators with verified hospital observation windows.
