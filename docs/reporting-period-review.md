# Reporting-period and comparison review

Reviewed 2026-09-16, before frontend development. The source inspection in `data-profile.md` remains the original profiling record; this review supersedes the earlier assumption that a progress row alone establishes a comparable before/after pair.

## Reference evidence

No official definition documents were present in the repository. The review therefore used Ontario Health's published [2025/26 indicator specifications, pp. 7–16](https://www.hqontario.ca/Portals/0/documents/qi/qip/2025-26-QIP-technical-specifications-en.pdf), [2026/27 specifications, pp. 9–16](https://qipnavigator.hqontario.ca/portals/0/documents/qi/qip/2025/Technical%20Specifications%20EN.pdf), and [2026/27 guidance, pp. 9–10](https://qipnavigator.hqontario.ca/portals/0/documents/qi/qip/2025/Guidance%20Document%20EN.pdf). Reviewed facts, source URLs and page references are pinned in `config/indicator_metadata.json`; normal builds do not access the network.

The guidance explains that progress reports carry prior workplan values and targets forward and populate current values for centrally available indicators. This supports the report linkage. It does not establish equal observation windows for every exported hospital record.

The 2025/26 specifications distinguish ERNI and non-ERNI windows for six ED time measures. The 8 a.m. backlog and LWBS definitions use a six-month baseline. The 2026/27 specifications give a December–November window for time measures and the preceding full fiscal year for backlog/LWBS. Full dates are recorded in the indicator registry. These defaults cannot resolve missing hospital participation information or override conflicting hospital notes.

## Actual export findings

The primary ED cohort contains 206 organization–indicator cycles, 130 matched pairs, 76 workplan-only cycles and 129 numeric change candidates before period verification. Workplan source/period strings, counted once per cycle:

| Source/period string | Cycles |
| --- | ---: |
| `CIHI NACRS / Other` | 158 |
| `CIHI NACRS / Fiscal Year` | 46 |
| `CIHI NACRS / April 1, 2024-Novemeber 30, 2024` | 1 |
| `Other / April 1, 2024- December 2024 Q1- Q3` | 1 |

`Fiscal Year` gives no year endpoints. `Other` supplies no dates. The two explicit local windows differ from the default windows. None of these strings independently identifies the follow-up window. Progress exports have no structured unit, population or observation-window columns. ERNI participation and site coverage are absent. A hospital's size or inclusion in an export does not establish its ERNI status.

Review included all matched ED progress commentary with date, quarter, YTD, period, month or annual references. Most dated prose describes activity rather than measurement windows. Notable source evidence is retained through these cycle IDs and their progress-source links:

| Cycle | Evidence in original progress commentary | Decision |
| --- | --- | --- |
| `cycle_9c5a3f964824b764c8ef` | Baseline Q1/Q2 2024 versus current full FY2024/25; note disputes relevance to the 2025/26 workplan | Dates verified in `comparison_reviews.csv`, but overlapping and unequal windows; comparison excluded |
| `cycle_26e977802dc16717fbc6` | Exported offload figure uses the P4R year ending November 2025, while the hospital evaluates an April 2025–February 2026 window | Baseline window unresolved; do not replace the exported figure with a narrative number |
| `cycle_ac12907f4eec0fa0b11a` | HIS extraction problem; roughly two months of reliable offload data | No verified comparable pair |
| `cycle_b5bf3a792b3a8470565c` | Distinguishes the auto-populated value from more recent quarterly values | Do not substitute quarterly narrative values |

## Implemented verification contract

- `unit_verified`: a matched, unambiguous cycle uses a verified official indicator and the preceding workplan explicitly supplies an allowed unit. The exact progress indicator identifies the same standard definition. This is verification of the documented definition/context, not an independent audit of patient records.
- `population_verified`: the same conditions hold for the allowed workplan population label and the indicator's specific admission/acuity definition. Broad `ED patients` alone cannot merge different indicators. Unknown, conflicting or incompatible contexts fail.
- `reporting_period_verified`: a reviewed cycle entry supplies actual baseline and follow-up endpoints with source IDs and an evidence note. Verified dates can still be incomparable.
- `comparison_eligible`: accepted historical match, verified definition and direction, verified unit/population, verified windows and an affirmative comparability review. Approved windows must be nonoverlapping and comparable in duration (one day tolerance for leap years); a reviewer must also establish matching seasonal/reporting bases and population/site definitions. Similar durations alone are insufficient.
- `analysis_eligible`: comparison eligible **and** in the eight-indicator ED registry **and** the 2025/26 → 2026/27 primary period. All first-cycle ED records carry `analysis_eligible=false` and the exact exclusion reason `insufficient first-cycle ED longitudinal coverage`, regardless of other gates.

`comparable` is retained as an alias of `comparison_eligible`. `numeric_change_candidate` is a coverage diagnostic only: matched legacy context plus known direction and numeric baseline/current. It does not grant an outcome or target calculation. Numeric values and every raw source record remain available even when calculations are withheld.

One primary ED cycle has verified but incompatible dates; 205 have unverified pairs. Unit/population checks pass for the 130 accepted matches. **Zero cycles currently pass all comparison gates, so zero outcomes and targets are eligible for headline calculation.** This is missing comparable evidence, not a measured zero improvement rate. The previous pipeline's four first-cycle and 129 primary-cycle ED calculations relied on an assumption this pass removes.

## Frontend consequences

Use a coverage-first presentation: 206 candidates → 130 matches → 129 numeric candidates → 0 verified comparisons. Show outcome percentages as unavailable (`null`), with numerator/denominator and exclusion explanations; never render 0/0 as 0%. Do not draw annual trend lines or label these exported values as post-implementation annual results. Implementation reporting, intervention categories, current plans and source drill-down remain usable. A later evidence review can enable outcomes through `comparison_reviews.csv`, without weakening the gates or rewriting raw values.
