# Phase 1 — Source data profile

> Analytical refinement (2026-09-16): the primary ED window is now 2025/26 → 2026/27. All 66 first-cycle ED candidates remain in history with explicit exclusions. The primary period has 130 matched cycles and 129 numeric change candidates, but zero verified comparable pairs under the stricter observation-window gates. See [reporting-period-review.md](reporting-period-review.md), [indicator-metadata.md](indicator-metadata.md), [taxonomy-review.md](taxonomy-review.md), and the updated [methodology](methodology.md). Earlier profiling observations below are retained as history, not current calculation authorization.

> Phase 2 follow-up (2026-09-16): the profiling findings below are preserved as the original inspection record. The implemented model, exclusions, calculation gates and updated cycle-level match rates are documented in [methodology.md](methodology.md). Accepted hospital–indicator cycle matches are 475/817 (58.14%) and 572/849 (67.37%); defined ED-subset matches are 5/66 (7.58%) and 130/206 (63.11%). Exact idea-row candidate coverage still reproduces the Phase 1 figures. `data/processed/data_quality_summary.csv` now contains Phase 2 diagnostics rather than the original profiling-only summary.

Profile date: 2026-09-16. Scope: all five CSVs directly under `data/`; the recursive CSV inventory found no additional source files. Read `PRD.md` and the existing instruction file, whose on-disk spelling is `AGENTS.MD`. This is a source inspection and schema proposal only. No frontend, transformation pipeline, classification system, or outcome dataset has been implemented. `data/processed/data_quality_summary.csv` is the profiling-only deliverable required by PRD §6.

## Decision summary

Both proposed Workplan → following-year Progress relationships are supported by matching source records and agreement of baseline/target values. They are **partial, not complete, joins**. Exact organization + indicator + change-idea keys give candidate matches for **1,049/1,688 (62.1%)** of 2024/25 workplan rows and **1,194/1,742 (68.5%)** of 2025/26 rows. Only **949** and **1,124** of those are unambiguous one-row-to-one-row matches before resolving duplicate/detail groups. All of these unambiguous pairs agree on baseline and target after numeric-format comparison.

The ED-specific coverage is much weaker than the overall figures suggest, especially in the first cycle. For eight precisely specified ED indicator strings below, only **9/118 (7.6%)** and **218/371 (58.8%)** workplan rows have exact-key progress candidates. This is a diagnostic subset, not a completed ED inclusion taxonomy. Absence from these exports does not establish that a hospital failed to implement or report an initiative.

The proposed intervention table must be split: one indicator can have many ideas, one idea can have multiple method/process details, and several ideas share a single performance observation. Some apparent duplicates carry different populations, performance values, or implementation flags. A flat join would multiply records and distort rates.

The source contains all four reported domains, missing hospital models, nonnumeric performance tokens, ambiguous units, and five explicitly labelled test-hospital rows in the 2026/27 progress export. Row-level indicator type, stable organization/indicator IDs, progress units, and structured outcome reporting dates are absent. Resolve scope and analytical grain before Phase 2.

## Inspection method and count definitions

- Read original bytes without modification; all files decode strictly as UTF-8 with BOM (`utf-8-sig`). Parse with Python standard-library `csv.reader`, `newline=''`, and `strict=True`; retain strings without automatic NA conversion.
- Row counts exclude the header and empty CSV records. Each file has one trailing empty record. Embedded quoted newlines are valid field content, not extra analytical rows. Examples below use **CSV record numbers, header = record 1**, not physical line numbers; source lineage should retain both record number and physical start/end lines.
- Organization/indicator counts use distinct, nonempty **actual row fields**, before normalization, scope exclusions, or test filtering. Organization counts are reporting entities, not necessarily physical hospitals/campuses. Cross-file union: 136 raw organization names (134 excluding the two explicitly named test organizations) and 1,242 raw indicator strings.
- Blank percentages mean empty or whitespace-only cells, not all analytically unavailable values. Performance-token frequencies and model `No type available` are reported separately. Do not convert missing values to zero.
- Exact duplicate excess = row count minus the number of distinct complete source rows, comparing every source column. Repeated idea keys use organization + indicator + idea within a file; these are **candidate groups**, not certified unique interventions.
- Match diagnostics are directional and use the stated fiscal-year file pairing. “Candidate coverage” counts every workplan row whose key exists in progress, including ambiguous groups. “One-to-one” requires the key to occur exactly once on each side. A match is not evidence of causality.
- The normalization sensitivity check applies Unicode NFKC, case folding, Unicode punctuation-to-space replacement, then whitespace collapse to each of the three key fields. It is a diagnostic, not an approved entity/indicator mapping: it can erase meaningful punctuation, including decimal points and hyphens. Exact-first matching is safer here.
- No external organization registry or indicator definition source was used. Meanings not directly supported by these exports are explicitly marked as provisional or requiring review.

## File inventory

| Alias | Source filename | Bytes | Data rows | Columns | Organizations | Indicators | Regions | Nonblank model labels | Exact duplicate excess |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W2024-25 | WorkplanIndicatorReport 2024-25.csv | 84,666,653 | 1688 | 25 | 131 | 466 | 6 | 8 | 9 |
| P2025-26 | ProgressReportIndicatorReport 2025-26.csv | 1,030,146 | 1102 | 20 | 111 | 461 | 6 | 8 | 5 |
| W2025-26 | WorkplanIndicatorReport 2025-26.csv | 83,116,352 | 1742 | 25 | 133 | 445 | 6 | 8 | 5 |
| P2026-27 | ProgressReportIndicatorReport 2026-27.csv | 1,260,499 | 1246 | 20 | 127 | 435 | 6 | 8 | 4 |
| W2026-27 | WorkplanIndicatorReport 2026-27.csv | 95,302,714 | 1804 | 25 | 132 | 462 | 6 | 8 | 18 |

Each file has eight nonblank model labels: seven named model categories plus `No type available`; blank is a ninth observed state. Every row has sector `Acute Care/Hospital`. Every file contains all six regions. All figures above include test rows.

### File-specific categorical values

#### W2024-25: `WorkplanIndicatorReport 2024-25.csv`

- Fiscal-year values: `Fiscal Year: 2024/25` only.
- Indicator-type values: `Indicator Type: ALL` only, in report-filter metadata. **Actual row-level indicator type is unavailable.**
- Domains (`objective_header_Text2`): Safety: 603; Access and Flow: 493; Equity: 255; Experience: 337.
- Quality aims (`aim_header_Text2`): Safe: 502; Efficient: 174; Equitable: 255; Patient-centred: 337; Timely: 319; Effective: 101.
- Regions: Central Region: 169; East Region: 418; North East Region: 245; North West Region: 135; Toronto Region: 297; West Region: 424.
- Hospital models: [blank]: 34; Chronic/Rehab Hospital: 129; Large Community Hospital: 682; No type available: 14; Other Hospital: 11; Small Hospital: 456; Specialty Children Hospital: 35; Specialty Mental Health Hospital: 78; Teaching Hospital: 249.
- Blank model: 34/1,688 (2.0%); `No type available`: 14/1,688 (0.8%); combined unavailable model: 48/1,688 (2.8%).
- CSV structure: 1 trailing blank record; 0 wrong-width records; 0 CSV parse errors; 0 duplicate headers; 0 U+FFFD replacement characters; 0 NUL characters.
- Test organizations in actual rows: none.

#### P2025-26: `ProgressReportIndicatorReport 2025-26.csv`

- Fiscal-year values: `Fiscal Year: 2025/26` only.
- Indicator-type values: `Indicator Type: ALL` only, in report-filter metadata. **Actual row-level indicator type is unavailable.**
- Domain and quality-aim columns are absent. `Domain: ALL` is a filter, not a row classification.
- Raw implementation flags (`methods`): Y: 966; N: 136. These are source-row frequencies, not deduplicated implementation rates.
- Regions: Central Region: 136; East Region: 242; North East Region: 110; North West Region: 103; Toronto Region: 241; West Region: 270.
- Hospital models: [blank]: 28; Chronic/Rehab Hospital: 106; Large Community Hospital: 401; No type available: 8; Other Hospital: 11; Small Hospital: 219; Specialty Children Hospital: 45; Specialty Mental Health Hospital: 73; Teaching Hospital: 211.
- Blank model: 28/1,102 (2.5%); `No type available`: 8/1,102 (0.7%); combined unavailable model: 36/1,102 (3.3%).
- CSV structure: 1 trailing blank record; 0 wrong-width records; 0 CSV parse errors; 0 duplicate headers; 0 U+FFFD replacement characters; 0 NUL characters.
- Test organizations in actual rows: none.

#### W2025-26: `WorkplanIndicatorReport 2025-26.csv`

- Fiscal-year values: `Fiscal Year: 2025/26` only.
- Indicator-type values: `Indicator Type: ALL` only, in report-filter metadata. **Actual row-level indicator type is unavailable.**
- Domains (`objective_header_Text2`): Safety: 566; Equity: 245; Access and Flow: 592; Experience: 339.
- Quality aims (`aim_header_Text2`): Safe: 501; Equitable: 245; Timely: 566; Patient-centred: 339; Effective: 65; Efficient: 26.
- Regions: Central Region: 176; East Region: 405; North East Region: 269; North West Region: 165; Toronto Region: 315; West Region: 412.
- Hospital models: [blank]: 40; Chronic/Rehab Hospital: 119; Large Community Hospital: 740; No type available: 19; Other Hospital: 11; Small Hospital: 466; Specialty Children Hospital: 33; Specialty Mental Health Hospital: 71; Teaching Hospital: 243.
- Blank model: 40/1,742 (2.3%); `No type available`: 19/1,742 (1.1%); combined unavailable model: 59/1,742 (3.4%).
- CSV structure: 1 trailing blank record; 0 wrong-width records; 0 CSV parse errors; 0 duplicate headers; 0 U+FFFD replacement characters; 0 NUL characters.
- Test organizations in actual rows: none.

#### P2026-27: `ProgressReportIndicatorReport 2026-27.csv`

- Fiscal-year values: `Fiscal Year: 2026/27` only.
- Indicator-type values: `Indicator Type: ALL` only, in report-filter metadata. **Actual row-level indicator type is unavailable.**
- Domain and quality-aim columns are absent. `Domain: ALL` is a filter, not a row classification.
- Raw implementation flags (`methods`): N: 349; Y: 897. These are source-row frequencies, not deduplicated implementation rates.
- Regions: Central Region: 145; East Region: 290; North East Region: 163; North West Region: 111; Toronto Region: 266; West Region: 271.
- Hospital models: [blank]: 36; Chronic/Rehab Hospital: 112; Large Community Hospital: 459; No type available: 14; Other Hospital: 11; Small Hospital: 283; Specialty Children Hospital: 38; Specialty Mental Health Hospital: 69; Teaching Hospital: 224.
- Blank model: 36/1,246 (2.9%); `No type available`: 14/1,246 (1.1%); combined unavailable model: 50/1,246 (4.0%).
- CSV structure: 1 trailing blank record; 0 wrong-width records; 0 CSV parse errors; 0 duplicate headers; 0 U+FFFD replacement characters; 0 NUL characters.
- Test organizations in actual rows: {'Hospital A (TEST) (TEST)': 3, 'Hospital xyz1 (TEST)': 2}.

#### W2026-27: `WorkplanIndicatorReport 2026-27.csv`

- Fiscal-year values: `Fiscal Year: 2026/27` only.
- Indicator-type values: `Indicator Type: ALL` only, in report-filter metadata. **Actual row-level indicator type is unavailable.**
- Domains (`objective_header_Text2`): Safety: 551; Experience: 316; Equity: 229; Access and Flow: 708.
- Quality aims (`aim_header_Text2`): Safe: 483; Patient-centred: 316; Equitable: 229; Timely: 693; Effective: 68; Efficient: 15.
- Regions: Central Region: 206; East Region: 421; North East Region: 302; North West Region: 139; Toronto Region: 296; West Region: 440.
- Hospital models: [blank]: 51; Chronic/Rehab Hospital: 119; Large Community Hospital: 731; No type available: 15; Other Hospital: 11; Small Hospital: 524; Specialty Children Hospital: 36; Specialty Mental Health Hospital: 52; Teaching Hospital: 265.
- Blank model: 51/1,804 (2.8%); `No type available`: 15/1,804 (0.8%); combined unavailable model: 66/1,804 (3.7%).
- CSV structure: 1 trailing blank record; 0 wrong-width records; 0 CSV parse errors; 0 duplicate headers; 0 U+FFFD replacement characters; 0 NUL characters.
- Test organizations in actual rows: none.

## Actual schemas, inferred types, and field mapping

All physical source values are strings. Types below describe the proposed semantic interpretation after validation. There are **no source IDs**. The first eight `Textbox*` fields in each schema are constant within their file and must be stored as export metadata, not repeated in every frontend record. In workplans these constants account for approximately 98% of field characters; the huge indicator selector text is not a row-level list of observed indicators. The source files are 83–95 MB despite containing fewer than 1,805 data rows each.

### Workplan schema: identical headers and order in all three files

| Actual column (source order) | Inferred type | Meaning / proposed mapping | W2024-25 blank | W2025-26 blank | W2026-27 blank |
| --- | --- | --- | --- | --- | --- |
| `Textbox168` | Export fiscal-year string | Report year; workplan plan cycle | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox150` | Constant filter string | Sector selection; use row sector below | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox132` | Constant filter string | `Model: ALL`; not hospital model | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox108` | Constant filter string | Selected region list; not row region | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox79` | Constant filter string | Organization selection; 2024/25 has a long list, later years `ALL` | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox57` | Constant filter string | `Domain: ALL`; use row objective below | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox39` | Constant filter string | `Indicator Type: ALL`; no actual type | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `Textbox21` | Constant filter string | Long selected-indicator list; not the row indicator | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `sector_name_Text2` | Categorical string | Reported sector | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `OrgCategory_Label_Text2` | Nullable category | Reported hospital model; blank and `No type available` remain unavailable | 34/1,688 (2.0%) | 40/1,742 (2.3%) | 51/1,804 (2.8%) |
| `LHIN_Label_Text2` | Categorical string | Ontario region labels as reported; do not reinterpret as historical LHIN IDs | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `org_name_Text2` | Entity-label string | Original organization name | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `aim_header_Text2` | Categorical string | Quality aim: Safe, Timely, etc. | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `objective_header_Text2` | Categorical string | Reported domain: Access and Flow, Safety, Experience, Equity | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `measure_header_Text2` | Free-text label | Original indicator wording; may include site, population or metric definition | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `unit_population_Text2` | Composite text | Raw unit / population; needs reviewed parsing | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `datasource_period_Text2` | Composite text | Raw data source / period; not a reliably structured date | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `current_value_text2` | Decimal or nonnumeric token | Workplan baseline/current-at-planning value | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `target_value_text2` | Decimal or nonnumeric token | Workplan performance target | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `target_justification2` | Narrative string | Target justification | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `planned3` | Narrative string | Change idea; may contain a bundle of actions | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `methods2` | Narrative string | Planned method/detail | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `process_measure3` | Narrative string | Planned process measure | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `goal2` | Narrative string | Planned process target; not the indicator numeric target | 0/1,688 (0.0%) | 0/1,742 (0.0%) | 0/1,804 (0.0%) |
| `comments2` | Nullable narrative | Workplan comments | 1,340/1,688 (79.4%) | 1,354/1,742 (77.7%) | 1,318/1,804 (73.1%) |

### Progress schema: identical headers and order in both files

| Actual column (source order) | Inferred type | Meaning / proposed mapping | P2025-26 blank | P2026-27 blank |
| --- | --- | --- | --- | --- |
| `Textbox382` | Export fiscal-year string | Progress report year; distinguish from the preceding plan cycle | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox333` | Constant filter string | Sector selection with `(AC)` suffix | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox429` | Constant filter string | `Model: ALL` | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox417` | Constant filter string | `Domain: ALL`; actual domain absent | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox405` | Constant filter string | `Indicator Type: ALL`; actual type absent | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox393` | Constant filter string | `Indicator: ALL` | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox369` | Constant filter string | Selected region list | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `Textbox345` | Constant filter string | `Organization: ALL` | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `sector_name_Text2` | Categorical string | Reported sector | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `OrgCategory_Label_Text2` | Nullable category | Reported hospital model | 28/1,102 (2.5%) | 36/1,246 (2.9%) |
| `LHIN_Label_Text2` | Categorical string | Reported region | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `org_name_Text2` | Entity-label string | Original organization name | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `measure_header_Text2` | Free-text label | Original indicator wording | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `formatted_current_value2` | Decimal or nonnumeric token | Prior/baseline performance, supported by paired workplan agreement | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `formatted_target_value2` | Decimal or nonnumeric token | Prior plan target, supported by paired workplan agreement | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `formatted_progress_value2` | Decimal or nonnumeric token | Reported subsequent performance | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `progress2` | Nullable narrative | Indicator-level progress commentary; not a numeric progress field | 558/1,102 (50.6%) | 468/1,246 (37.6%) |
| `planned_initiative` | Narrative string | Reported change idea | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `methods` | Y/N categorical flag | Inferred implemented flag from all observed values; NOT the planned method | 0/1,102 (0.0%) | 0/1,246 (0.0%) |
| `process_measure` | Nullable narrative | Implementation/progress notes, often lessons and challenges; NOT the original planned process measure | 0/1,102 (0.0%) | 1/1,246 (0.1%) |

The progress field interpretations follow the actual contents, not their misleading names: `methods` contains only `Y/N`; `process_measure` contains narratives such as “Transfers across UHT sites have improved d/t increased referral volumes; ALC corporate strategy committee developed in September 2024.” (P2025-26 record 2). There is no separate, authoritative `lessons_learned` column. Preserve neutral `implementation_notes_raw` rather than presenting extracted lessons as a source field. Confirm the precise meaning of `Y/N` with the report layout/data dictionary before releasing a KPI; mixed narrative completion does not justify overriding a source flag.

### Nonnumeric performance and zero baselines

| File | Performance column | Unavailable/nonnumeric tokens (count) | Nonnumeric share | Numeric zeros |
| --- | --- | --- | --- | --- |
| W2024-25 | `current_value_text2` | `CB`: 369, `X`: 31 | 400/1,688 (23.7%) | 75 |
| W2024-25 | `target_value_text2` | `CB`: 128 | 128/1,688 (7.6%) | 70 |
| P2025-26 | `formatted_current_value2` | `CB`: 267, `X`: 8 | 275/1,102 (25.0%) | 32 |
| P2025-26 | `formatted_target_value2` | `CB`: 106 | 106/1,102 (9.6%) | 36 |
| P2025-26 | `formatted_progress_value2` | `CB`: 38, `NA`: 20, `X`: 3 | 61/1,102 (5.5%) | 25 |
| W2025-26 | `current_value_text2` | `CB`: 281, `X`: 17 | 298/1,742 (17.1%) | 83 |
| W2025-26 | `target_value_text2` | `CB`: 163 | 163/1,742 (9.4%) | 82 |
| P2026-27 | `formatted_current_value2` | `CB`: 219, `X`: 3 | 222/1,246 (17.8%) | 44 |
| P2026-27 | `formatted_target_value2` | `CB`: 131 | 131/1,246 (10.5%) | 33 |
| P2026-27 | `formatted_progress_value2` | `NA`: 14, `CB`: 60, `X`: 9 | 83/1,246 (6.7%) | 17 |
| W2026-27 | `current_value_text2` | `CB`: 342, `X`: 16 | 358/1,804 (19.8%) | 93 |
| W2026-27 | `target_value_text2` | `CB`: 208 | 208/1,804 (11.5%) | 78 |

Every performance cell is nonblank, but many are not numeric. All remaining performance strings match a signed plain decimal/integer pattern; no percent-sign strings, comma-formatted numbers, inequalities, ranges, or other malformed numeric strings were observed in these performance columns. `N/A` does occur in narratives; the performance spelling in these files is `NA`. `CB`, `X`, and `NA` must remain distinct raw tokens with null numeric values. Some accompanying prose says “Collecting Baseline,” but the authoritative code dictionary is not supplied; do not invent a meaning for `X` or silently equate every token with the same reason.

Numeric `0.00` is a real reported zero and must remain numeric. Percentage change is undefined at zero baseline; absolute change and target comparison may still be available if direction and comparability are known. Never use an epsilon to manufacture a percent change.

Narrative missingness also exceeds blank counts: W2025-26 comments have 16 `N/A` cells; W2026-27 comments have 10. P2025-26 `progress2` has two `NA` cells beyond 558 blanks; P2026-27 has 48 `N/A`/`n/a` cells beyond 468 blanks. P2025-26 implementation notes have nine NA-like cells; P2026-27 has nine plus one blank. Workplan comments also contain explicit “no comment” variants. Preserve the original text and distinguish empty, NA-like, and substantive text; do not substitute invented lessons.

## Grain, multiplicity, and duplicates

| File | Org + indicator groups | Groups with >1 distinct idea | Maximum distinct ideas/group | Exact org + indicator + idea keys | Repeated idea-key groups | Excess rows over idea keys | Full-row duplicate excess |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W2024-25 | 817 | 425 | 9 | 1629 | 44 | 59 | 9 |
| P2025-26 | 480 | 294 | 9 | 1052 | 35 | 50 | 5 |
| W2025-26 | 849 | 445 | 9 | 1687 | 41 | 55 | 5 |
| P2026-27 | 578 | 331 | 9 | 1211 | 25 | 35 | 4 |
| W2026-27 | 866 | 451 | 21 | 1739 | 41 | 65 | 18 |

**One indicator has multiple change ideas in every file.** These counts are within organization and file, so they do not merely reflect the same indicator being used by different hospitals. For example, P2025-26 records 2–4 contain three distinct ideas for Unity Health Toronto’s St. Joseph’s mean ED length-of-stay indicator, each repeating baseline 20.50, target 18.50, and subsequent value 24.00. W2026-27 records 592–612 contain 21 distinct ideas for a Listowel Wingham financial-services indicator, illustrating that the files are broader than ED flow.

**Repeated change-idea text is not a sufficient reason to drop a row.** W2024-25 records 1586–1587, Trillium Health Partners, `Emergency Department wait time for inpatient bed (90th percentile)`, repeat the same idea but have different methods, process measures and goals. P2025-26 records 223–224 repeat that idea with different implementation notes. A direct join generates four pairs from two rows on each side; their order does not prove which methods correspond. The next cycle repeats this problem at W2025-26 records 1644–1645 and P2026-27 records 230–231.

Within a repeated exact idea key, `methods` flags disagree in **four groups in P2025-26** and **three in P2026-27**. For example, P2026-27 records 234–236 (Trillium, Hospital Total Margin) contain one `N` and two `Y` rows for the same idea. Preserve detail flags and expose mixed/conflicting status; `any(Y)` would invent an unqualified implemented initiative.

| File | Distinct idea texts reused across >1 organization/indicator group |
| --- | --- |
| W2024-25 | 87 |
| P2025-26 | 51 |
| W2025-26 | 97 |
| P2026-27 | 62 |
| W2026-27 | 97 |

Reused text across indicators is a separate association, not necessarily a duplicate project or an independently implemented intervention. Do not deduplicate globally by text, and do not split numbered action bundles into invented atomic initiatives. V1 should count documented **change-idea associations**, with this definition visible.

### Conflicting performance inside organization + indicator groups

| File | Groups with >1 raw performance tuple |
| --- | --- |
| W2024-25 | 3 |
| P2025-26 | 3 |
| W2025-26 | 1 |
| P2026-27 | 0 |
| W2026-27 | 0 |

W2024-25 and P2025-26 each contain three such groups for St. Joseph’s Care Group. W2024-25 records 362–363 have the same patient-information indicator wording but `% / Other` versus `% / Mental health patients`, and different baseline/target values. Records 364–367 similarly separate `% / Other` and `% / Rehab`. The progress export drops that population field. Do not assume organization + indicator + year uniquely identifies an observation.

W2025-26 records 1498 and 1500 (Erie Shores Healthcare, equity/anti-racism education indicator) report baselines 100.00 and 83.00 against the same 75.00 target. One idea has no progress candidate despite its organization/indicator being present. These are unresolved source distinctions/conflicts; do not average values, use the first row, or identify a measurement instance solely by its numeric value. Preserve separate source facts until population/site/series identity is reviewed.

## Historical matching feasibility

### Exact keys, before deduplication

| Diagnostic | W2024-25 → P2025-26 | W2025-26 → P2026-27 |
| --- | --- | --- |
| Workplan rows with an exact idea-key candidate | 1,049/1,688 (62.1%) | 1,194/1,742 (68.5%) |
| Progress rows with an exact idea-key candidate | 1,042/1,102 (94.6%) | 1,189/1,246 (95.4%) |
| Distinct shared idea keys | 992 | 1154 |
| Unique one-row-to-one-row matches | 949 | 1124 |
| Shared keys with ambiguity on either side | 43 | 30 |
| Naive exact join output rows (unsafe) | 1202 | 1288 |
| Workplan organization + indicator groups present in progress | 478/817 (58.5%) | 573/849 (67.5%) |
| Progress organization + indicator groups present in workplan | 478/480 (99.6%) | 573/578 (99.1%) |
| Workplan rows with no idea-key candidate | 639 | 548 |
| Progress rows with no idea-key candidate | 60 | 57 |

An organization/indicator-only join is useful for identifying a shared metric context but cannot establish initiative implementation. Exact one-to-one pairs have baseline **and** target agreement in 949/949 and 1,124/1,124 cases after decimal-value comparison (e.g. `3.1` equals `3.10`). In the second cycle only 1,055 of 1,124 pairs have byte-identical baseline strings and likewise 1,055 have byte-identical target strings; these are formatting differences, not conflicting numeric values. This supports `formatted_current_value2` as the preceding workplan baseline and `formatted_progress_value2` as its reported follow-up, rather than using the next workplan’s current value as a substitute outcome.

Among exact one-to-one pairs, 701/949 and 907/1,124 contain numeric progress baseline and follow-up. These are numeric-availability counts only: verified direction, unit, population, dates, scope, and duplicate handling are still required before classifying outcomes. Do not report these numbers as final usable clinical observations.

### Normalization sensitivity

| Diagnostic after NFKC/case/punctuation/whitespace normalization | First cycle | Second cycle |
| --- | --- | --- |
| Workplan rows with candidates | 1049 | 1194 |
| Progress rows with candidates | 1042 | 1189 |
| Distinct shared idea keys | 989 | 1153 |
| One-row-to-one-row keys | 945 | 1122 |
| Ambiguous shared keys | 44 | 31 |
| Naive join output rows | 1212 | 1290 |

Normalization adds **zero candidate-covered rows** in either historical pair and increases collisions. Preserve exact keys as the first pass. Use safe Unicode/whitespace aliases with collision checks only after that; do not automatically apply punctuation-stripping to indicator definitions. A normalized match is not intrinsically more trustworthy than an exact one.

Excluding the five test rows changes second-cycle progress-side candidate coverage from 1,189/1,246 (95.4%) to **1,189/1,241 (95.8%)**; workplan-side coverage is unchanged. Do not silently switch denominators.

### Unmatched records and change-idea wording

Most linked change ideas match verbatim; the remaining progress ideas are not repaired by basic text normalization. There are 60 and 57 progress rows without an exact idea-key candidate. Of those, 56 and 48 have an exact organization/indicator context in the corresponding workplan. These may be additional activities, rewrites, splits, or other reporting changes; the files cannot establish which explanation applies.

Examples of changed wording within the same organization/indicator:

- W2024-25 record 941, South Bruce Grey Health Centre, Patient falls/1,000 Patient Days, includes a sentence about involving patients/families followed by a sentence about monitoring falls data. P2025-26 record 513 contains only the latter sentence. A diagnostic `difflib.SequenceMatcher(autojunk=False)` ratio on raw text is 0.739.
- W2025-26 record 984, Bluewater Health, a mental-health ED revisit indicator, combines an access statement and engagement with school staff. P2026-27 record 494 retains the school-staff portion, with whitespace changes; raw diagnostic ratio 0.800.

These are **review candidates only**, not accepted fuzzy matches. No fuzzy links are counted in coverage. A high similarity can still conceal an altered target, population, or activity; use a documented algorithm/version, score, competing-candidate margin, and human review decision if fuzzy matching is added. Across each prescribed pair, no otherwise-unmatched progress row has an identical idea under the same organization but a different indicator string.

The first pair has two progress organization/indicator combinations absent from the workplan, covering four rows: Haliburton Highlands patient-information survey (P2025-26 record 565), and Atikokan sociodemographic collection (records 672–674). The second pair has five absent combinations covering nine rows: three test-hospital combinations/five rows, and two St. Joseph’s Health Care, London ambulatory medication-reconciliation variants/four rows (records 1233–1236). They remain unmatched until reviewed.

Only one workplan row in the second cycle lacks an idea match while its exact organization/indicator exists in progress: Erie Shores record 1498 described above. There are zero such workplan rows in the first cycle. Most unmatched workplan rows therefore lack that organization’s indicator in the progress export, rather than simply having altered idea wording.

### Organization coverage gaps in each historical pair

**W2024-25 → P2025-26:** organizations present only in the workplan (20): Blanche River Health; Campbellford Memorial Hospital; Deep River And District Hospital; Hawkesbury And District General Hospital; Hornepayne Community Hospital; Humber River Health; Huron Perth Healthcare Alliance; Niagara Health System; Nipigon District Memorial Hospital; North Bay Regional Health Centre; North of Superior Healthcare Group; Notre Dame Hospital (Hearst); Perth And Smiths Falls District Hospital; Queensway-Carleton Hospital; Services De Sante De Chapleau Health Services; Smooth Rock Falls Hospital; Stevenson Memorial Hospital Alliston; Timmins and District Hospital; Windsor Regional Hospital; Woodstock Hospital.

Organizations present only in progress: none.

**W2025-26 → P2026-27:** organizations present only in the workplan (8): Grand River Hospital Corporation; Guelph General Hospital; North of Superior Healthcare Group; Santé Manitouwadge Health; Smooth Rock Falls Hospital; Southlake Regional Health Centre; St. Mary's General Hospital; Weeneebayko Area Health Authority.

Organizations present only in progress: Hospital A (TEST) (TEST); Hospital xyz1 (TEST).

These are export-coverage gaps, not verified closures, renames, nonimplementation, or noncompliance. Both progress files say `Indicator: ALL`; nevertheless they lack many indicators present in the workplans. The CSVs alone do not explain the missing coverage. A more complete export or source-provider explanation would materially improve V1.

## ED scope and measurement comparability

### Eight observed indicator strings: source-row coverage

| Exact indicator string | W2024-25 | P2025-26 | W2025-26 | P2026-27 | W2026-27 |
| --- | --- | --- | --- | --- | --- |
| 90th percentile ambulance offload time | 26 | 0 | 70 | 76 | 60 |
| 90th percentile emergency department wait time to physician initial assessment | 0 | 0 | 109 | 105 | 120 |
| Daily average number of patients waiting in the emergency department for an inpatient bed at 8 a.m. | 0 | 0 | 44 | 47 | 45 |
| 90th percentile emergency department length of stay for nonadmitted patients with low acuity | 0 | 0 | 15 | 0 | 51 |
| 90th percentile emergency department length of stay for nonadmitted patients with high acuity | 0 | 0 | 23 | 0 | 63 |
| 90th percentile emergency department length of stay for admitted patients | 2 | 2 | 12 | 0 | 19 |
| 90th percentile emergency department wait time to inpatient bed | 57 | 6 | 61 | 0 | 53 |
| Percent of patients who visited the ED and left without being seen by a physician | 33 | 1 | 37 | 1 | 32 |

Counts use literal source strings. Similar local indicators and punctuation variants are not included in this diagnostic table. P2026-27 includes three test rows under ambulance offload and one under the 8 a.m. count, plus a fifth under `test test test`. This is why matching coverage must be measured by organization/idea as well as indicator label.

| Workplan cohort | First-cycle exact candidate coverage | First-cycle one-to-one rows | Second-cycle exact candidate coverage | Second-cycle one-to-one rows |
| --- | --- | --- | --- | --- |
| All source rows | 1,049/1,688 (62.1%) | 949 | 1,194/1,742 (68.5%) | 1124 |
| Reported Access and Flow domain | 236/493 (47.9%) | 221 | 439/592 (74.2%) | 414 |
| Eight exact ED strings above | 9/118 (7.6%) | 9 | 218/371 (58.8%) | 212 |

The eight-string workplan cohort contains 48 reporting organizations in 2024/25 and 87 in 2025/26. It is intentionally narrower than all candidate ED indicators. Its first-cycle matches cover only five organization/indicator combinations; the second covers 130. Do not use the 62.1%/68.5% overall coverage to promise two equally complete ED outcome cycles.

`Access and Flow` is not an adequate ED inclusion rule. The domain contains 493, 592, and 708 workplan rows (111, 114, and 124 distinct indicator strings), including Hospital Total Margin, carbon emissions, surgical activity, community services and other non-ED measures. Conversely, indicator definitions and context—not a guessed keyword alone—must determine inclusion. Retain every raw record, and mark `included`, `excluded`, or `needs_review` with a documented reason.

A notable historical label is `90th percentile ED length of stay`: 51 rows in W2024-25, only one in P2025-26, none in the later workplans. Fifty workplan rows say `Hours / ED patients`; one says `90th percentile / ED patients`. The label itself does not specify admitted/nonadmitted status or acuity. Do not map all 51 rows to a later, more specific metric without supporting definitions.

### Units, populations, sites, and periods

- Observed standard workplan units: ambulance offload → `Minutes / Patients`; physician initial assessment and most ED lengths/waits → `Hours / ED patients`; 8 a.m. waiting count → `Number / ED patients`; left-without-being-seen → `% / ED patients` (one 2024/25 row says `% / Other`). Lower-is-better is a reasonable proposed direction for these defined waiting/count/LWBS metrics, but the CSV contains no direction field. Approve definitions and record the basis in indicator metadata before calculation. Other Access and Flow indicators can have different directions.
- W2026-27 PIA records 1197–1198 (Haliburton Highlands) say `90th percentile / ED patients`, not a time unit. Five rows for the standard admitted-LOS string also say `90th percentile / ED patients`. `90th percentile` is a statistic, not a time unit. Do not silently infer hours from the numeric scale.
- W2026-27 records 931–932 (Centre for Addiction and Mental Health) use `Other / Other` for the standard 8 a.m. count and `CB` baseline/target. Two rows under standard time-to-inpatient-bed use `Hours / All inpatients`, unlike the usual ED population. These require review even though wording matches.
- Mean/average versus 90th percentile, admitted versus nonadmitted, high versus low acuity, CTAS-1 versus all ED patients, and 6 a.m./7 a.m./8 a.m./11 a.m./midnight counts are different measurement definitions. Text normalization must preserve these distinctions.
- Unity Health Toronto’s mean admitted-LOS labels explicitly distinguish St. Michael’s and St. Joseph’s sites. Other reports may combine sites under one organization. Keep nullable site/population context; do not equate reporting organizations with campuses.
- `datasource_period_Text2` combines data-source descriptions and variable periods such as `CIHI NACRS / Other`, `CIHI NACRS / Fiscal Year`, or `WTIS / Quarter`, as well as locally written dates. Parse only reviewed structures and preserve the composite raw string. The report fiscal year is not an observation date.
- Progress reports have **no unit/population or structured observation-period columns**. Prose sometimes specifies partial-year data: P2025-26 includes “Results as of FY24-25 Q3 YTD”; P2026-27 includes “Current performance based on Q3 FYTD.” Numeric before/after availability alone does not establish equal observation windows. Store unknown/partial-period flags; do not manufacture annual dates or line-chart timepoints.
- For matched progress records, workplan unit/population can supply inherited metadata only when the measurement instance is unambiguous; record its provenance. For unmatched progress records, retain unknown values until independently verified. Do not copy the next workplan’s units or baseline as if they were follow-up metadata.

## Organization and indicator naming across years

| Comparison | Exact shared organization names | Earlier-only organizations | Later-only organizations | Exact shared indicator strings | Earlier-only indicator strings | Later-only indicator strings | Normalized shared indicator strings |
| --- | --- | --- | --- | --- | --- | --- | --- |
| W2024-25 → W2025-26 | 131 | 0 | 2 | 57 | 409 | 388 | 77 |
| W2025-26 → W2026-27 | 131 | 2 | 1 | 74 | 371 | 388 | 95 |
| P2025-26 → P2026-27 | 105 | 6 | 22 | 45 | 416 | 390 | 64 |

Observed organization differences:

- All 131 W2024-25 organization labels also appear in W2025-26. The two additional names are Mississippi River Health Alliance and West Nipissing General Hospital.
- W2026-27 no longer contains Grand River Hospital Corporation or St. Mary’s General Hospital and adds Waterloo Regional Health Network. This is a **possible organizational succession/restructure**, not a confirmed alias or merger based on these CSVs. Keep distinct entity IDs pending a sourced, dated relationship; do not add predecessors’ performance together or backfill a successor’s history.
- `Brightshores Health System ` has a trailing space in all five files; a trimmed display/match alias is appropriate while raw text remains unchanged. `Hotel Dieu Hospital - Cornwall ` also has a trailing space.
- The W2024-25 organization selector contains names such as Atikokan Health and Community Services, Espanola Regional Hospital and Health Centre, and Stevenson Memorial Hospital. Actual row values are Atikokan General Hospital, Espanola General Hospital, and Stevenson Memorial Hospital Alliston. These row labels remain stable where present across files. Selector text must not be treated as evidence of a year-specific name change or as an organization dimension.
- No raw organization name changes its reported model or region across the five files. Missing models remain missing, including Unity Health Toronto and Listowel Wingham Hospitals Alliance; do not infer a hospital model from familiarity with an organization.

Indicator wording changes extensively, but set differences combine real additions/removals, wording edits and changed definitions. They are not counts of renamed indicators. Only 57 raw strings are shared by successive workplans in the first comparison and 74 in the second; even the aggressive diagnostic normalization raises these only to 77 and 95. Examples include a PIA target sentence in W2025-26 versus an abbreviated `90th Percentile PIA Time in the Emergency Department (ED).` in W2026-27; these require a reviewed alias decision with organizational context. The later workplans also contain `non-admitted`, `nonadmitted`, and the typo `noadmitted`, as well as site/time/acuity-specific variants. Review spelling candidates without erasing clinical distinctions.

### Encoding and content quality

No UTF-8 decode failures, malformed CSV rows, U+FFFD, NUL, suspicious C0 control characters (excluding normal tabs/newlines), or candidate mojibake strings `Ã`, `Â`, `â€` were observed. This is a targeted scan, not proof that every free-text character is correct. Nonbreaking spaces occur in nonmetadata fields in 9, 24, and 31 workplan rows, and 9 and 13 progress rows. Curly quotes, accents, embedded line breaks and apostrophes are valid source text. Keep them in raw fields; create separate normalization keys.

The 2026/27 progress rows for `Hospital A (TEST) (TEST)` (records 4–6) and `Hospital xyz1 (TEST)` (556–557) contain explicit test idea/notes text. Exclude these five from public analytics using an explicit, auditable organization exclusion rule, while retaining source records. Test names also appear in a workplan’s selector metadata despite having no actual workplan rows; never count selectors as data.

## Proposed final normalized schema

The final analytical grain is **a reporting organization’s defined measurement instance in a plan cycle**, linked to documented change-idea associations and their source details. A measurement instance distinguishes indicator definition, site/population, observation context, and any reviewed source-series distinction. Organization + indicator name + year is a candidate grouping, not a guaranteed primary key. Use deterministic surrogate IDs and explicit mappings; do not use row order or a performance value as clinical identity.

The tables below are a proposal for Phase 2, not files already created. All foreign keys must be validated. Nullable fields stay null when the source does not establish them. Raw source records and proposed aliases remain separate.

| Table | Grain / primary key | Required fields and relationships |
| --- | --- | --- |
| `source_files` | One immutable export; `source_file_id` derived from checksum | Filename, SHA-256, report type, report fiscal year, encoding, ordered headers, byte/row counts, constant filter fields with original strings, profile/build version. Store repeated selector metadata once. |
| `source_records` | One original nonempty CSV record; `source_record_id = file checksum + CSV record number` | `source_file_id`, record number, physical line start/end, lossless nonconstant raw fields, row hash, duplicate-group ID, exclusion/review flags. Constant raw values are recoverable through the file record. Original CSV bytes remain authoritative. |
| `organizations` | One reviewed reporting entity; `organization_id` | Preferred name, entity kind (`reporting_organization`), exclusion status/reason. Counts mean reporting organizations unless site coverage is explicitly known. No guessed model/region. |
| `organization_aliases` | A reviewed source-label mapping | Alias ID, raw name, normalized lookup key, `organization_id`, applicable report years/files, match rule, evidence/source record, review status. Trim-only aliases are distinct from organizational restructures. |
| `organization_attributes` | One entity’s reported attributes in a source/report period | Attribute ID, `organization_id`, report year/type, reported sector/model/region raw and normalized values, provenance. Conflicting claims stay separate. Blank and `No type available` normalize to unavailable with different raw reasons. |
| `organization_relationships` | Optional reviewed predecessor/successor or site relationship | Relationship ID, from/to entity IDs, relationship type, nullable effective dates, evidence, review status. Empty until supported; no automatic Grand River/St. Mary’s/Waterloo merge. |
| `indicator_definitions` | One comparable metric definition/version; `indicator_id` | Canonical name, metric family, statistic (mean/median/90th percentile/etc.), population/acuity/admission status, clock time if relevant, canonical unit, direction, scope status/reason, definition evidence, version. Unknown dimensions remain explicit. A display family is not a license to pool definitions. |
| `indicator_aliases` | One reviewed source wording/context → definition mapping | Alias ID, raw wording, safe normalized key, optional organization/site/year context, `indicator_id` nullable while unresolved, matching rule, review status/evidence. Preserve original domain/aim separately; no inferred row-level indicator type from `ALL`. |
| `measurement_instances` | One resolved organization/metric/site/population series; `measurement_instance_id` | `organization_id`, reviewed `indicator_id`, nullable site/local-series label, population detail, source-based resolution evidence, identity status. Ambiguous same-label groups remain unresolved instead of being collapsed or assigned fabricated sites. |
| `indicator_reports` | One measurement instance’s reporting context in one source/cycle; `indicator_report_id` | `measurement_instance_id` nullable if unresolved, `source_file_id`, `report_fiscal_year`, `plan_fiscal_year` nullable if unestablished, raw indicator label, reported aim/domain, raw unit/population, raw data source/period, parsed unit/population/date fields where justified, target justification, indicator-level comments, comparability/review status. Workplan and progress reports are separate rows. |
| `indicator_report_sources` | Report-context ↔ source-record bridge | `indicator_report_id`, `source_record_id`, role and resolution rule. Supports repeated numeric facts across multiple source idea/detail rows without losing provenance. Unresolved facts stay linked to their source rather than entering a trusted aggregate. |
| `performance_values` | One reported value role per indicator-report context | Value ID, `indicator_report_id`, role (`baseline`, `target`, `reported_followup`), raw string, nullable decimal, parse status/token, reported/inherited unit and provenance, nullable observation start/end, period text and status. Enforce unique report/role only for resolved contexts; conflicting raw claims remain in source records/review queue until resolved. Workplans have baseline and target only. |
| `plan_initiatives` | One documented change-idea association to a resolved workplan indicator report; `initiative_id` | Workplan `indicator_report_id`, plan year, change idea raw, normalized lookup key, identity/review status. Exact repeated ideas can form one parent with several detail records after conflict review. A bundled paragraph stays one documented idea; the same idea under another indicator is a different association. |
| `plan_details` | One distinct reported method/process-detail record under an initiative; `plan_detail_id` | `initiative_id`, planned method raw (`methods2`), process measure raw (`process_measure3`), process target raw (`goal2`), workplan comments raw, review status. Retain multiple details; exact duplicate source rows attach via lineage rather than inflate counts. |
| `progress_initiatives` | One reported change-idea association to a progress indicator report; `progress_initiative_id` | Progress `indicator_report_id`, idea raw/normalized, nullable matched plan initiative, derived status (`implemented`, `not_implemented`, `mixed`, `unknown`), status rule/version, review status. Keep progress-only associations so absence of a plan link does not erase reported activity. |
| `progress_details` | One distinct progress detail/flag record; `progress_detail_id` | `progress_initiative_id`, `implementation_flag_raw` (`methods`), nullable parsed flag, implementation notes raw (`process_measure`), review status. Do not create a false separate source `lessons_learned` field. |
| `record_lineage` | One normalized entity/detail ↔ source record association | Entity type/ID, `source_record_id`, source columns, derivation/mapping role. Every displayed plan, detail, measurement and aggregate drill-down must resolve to original records, including records collapsed as exact duplicates. |
| `longitudinal_matches` | One candidate or accepted cross-report link | Match ID, preceding workplan and following progress report IDs, nullable initiative/detail IDs, link level (`measurement`, `initiative`, `detail`), method/version, score nullable for nonfuzzy methods, review status, ambiguity reason, evidence, matched/unmatched reason, cardinality checks. An accepted measurement link does not automatically accept initiative or detail links. Never zip detail rows by order. |
| `initiative_classifications` | One versioned classification per plan/progress association | Association ID/type, primary category, 0–3 secondary tags, rule ID, method, confidence/review status, override reference, taxonomy version. Use reproducible rules and reviewed overrides; retain `Other` when unresolved. Do not classify during Phase 1. |
| `outcomes` | One derived comparison per resolved progress measurement report | Outcome ID, progress `indicator_report_id`, nullable preceding workplan report/link, baseline/target/follow-up value IDs, direction/unit/period-comparability status, signed absolute/relative change, direction-adjusted improvement percent, nullable `target_met`, outcome class/reason, algorithm/version. Several initiatives reference this same outcome through their report/match associations. |
| `data_quality_issues` | One source or mapping issue | Issue ID, affected entity/source IDs, issue code, severity, details, review status/resolution, build version. Examples: test entity, duplicate, conflicting baseline, missing model, unknown unit, unknown period, no follow-up, ambiguous match. The delivered quality CSV is an aggregate profile, not this future issue-level table. |

This logical separation can be implemented with Python and static CSV/JSON outputs; it does not require a database. Small UI-ready views may denormalize these tables after validation. `interventions.csv` would be a convenience view, with explicit measurement IDs and grain, rather than the authoritative store of repeated numeric outcomes. `current_workplans.csv` would be a view of W2026-27 plan initiatives/details with **no observed outcome or implementation result assigned to those plans**.

### Identity, matching, and aggregation rules

1. Preserve every raw source row, including exact duplicates, excluded tests and out-of-scope records. Create duplicate lineage groups. Only validated analytical views suppress redundant exact copies; retain distinct methods, notes, population contexts and conflicting facts.
2. Normalize organization labels through a reviewed mapping. Resolve indicators using metric definitions and contextual aliases, then establish measurement instances. Fail/queue unresolved identity and value conflicts rather than silently choosing the first row.
3. Match the prescribed cycles: plan 2024/25 → progress report 2025/26, and plan 2025/26 → progress report 2026/27. Validate the agreement of baseline/target and measurement context. Keep plan year, report year, and observation period as distinct concepts. Current 2026/27 plans do not have a subsequent progress report in this collection.
4. Prefer exact source matches with unambiguous cardinality, then reviewed safe aliases. Group-level matches can be valid where detail correspondence is unknown; store that distinction. Do not force a one-to-one detail match, numeric-value match, or fuzzy match merely to improve coverage.
5. Calculate indicator outcomes once per resolved measurement report. For the overall outcome distribution, count distinct eligible measurement outcomes. For category breakdowns, count distinct measurement outcomes associated with at least one relevant category association; the same measurement may legitimately appear in different categories, so category totals are not additive. If the UI instead shows an initiative-weighted measure, label it as such and show both initiative and distinct measurement counts.
6. Define `number_of_initiatives` as distinct included documented change-idea associations, not raw CSV rows, methods, repeated report appearances or inferred atomic projects. Count historical initiatives from the plan side and associate progress; distinguish progress-only ideas and current plans. Category distributions need a primary-category rule to remain additive at the initiative grain.
7. Proposed implementation rate: distinct resolved associations whose retained detail flags are all `Y`, divided by associations whose retained flags are all `Y` or all `N`. Mixed flags, missing progress and unresolved detail identity are separate disclosed exclusions. Show numerator, denominator, mixed count, unmatched count and coverage. `N` is reported nonimplementation at reporting time, not proof of permanent failure. This parent-level aggregation rule must be adopted explicitly before a KPI is released.
8. Target attainment denominator is the count of distinct resolved measurement outcomes with known direction and comparable numeric target/follow-up, **independent of baseline availability**. Improvement denominator requires comparable numeric baseline/follow-up and known direction, independently of whether target is numeric. Show insufficient-data counts; no null-to-zero conversion. For outcome-after-implementation statements, explicitly select measurement outcomes linked to the relevant implemented associations and expose the shared-outcome limitation.
9. No pooled means across hours, minutes, counts, ratios and percentages. Even relative percentages should only be summarized within compatible metric definitions/populations and observation windows, with n and weighting stated. Use medians/distributions where suitable; sample-size denominators for rates are recorded observations/associations, not unreported patient volumes.
10. Repeated-activity and persistent-issue metrics need reviewed identity across cycles. Do not infer a persistent problem from reused prose or a missing target. Leave `persistent_issue`, arbitrary scores/rankings, predictions and causal interpretations out of V1 until a defensible definition and evidence exist.

### Explicit calculation conventions to adopt before implementation

For an eligible comparison with baseline `b` and follow-up `c`:

- `performance_change = c - b` in the indicator’s own unit.
- `performance_change_pct = 100 * (c - b) / abs(b)` only if `b != 0`; this is a signed relative change, not inherently improvement.
- `improvement_pct = 100 * (b - c) / abs(b)` for lower-is-better; reverse the numerator for higher-is-better. Preserve both semantics with unambiguous labels, or expose only the direction-adjusted one consistently.
- `target_met = c <= target` for lower-is-better and `c >= target` for higher-is-better, only with comparable target/follow-up and verified direction. Keep nullable; it is independent of improvement.
- For percentage-valued indicators, `c - b` is a **percentage-point** difference; the relative change formula remains a percentage. Do not confuse the two.
- The sources do not establish a threshold for “No material change.” Proposed V1 default: exact numeric equality is `Unchanged`; any directional numeric difference is `Improved` or `Worsened`, subject to eligibility. If “No material change” is retained, add a justified, indicator-specific tolerance and document its units before using it. Never invent a universal clinical threshold.
- No outcome classification for unknown direction, unresolved conflicting facts, or incompatible measurement definitions/units. Store a specific insufficient-data/review reason. Unknown or partial reporting periods must remain visible; require a documented comparability policy before presenting cross-hospital comparisons as equivalent.
- Current 2026/27 plan outcomes should be **not applicable/not yet available**, distinct from historical `Insufficient data`; do not mix current plans into historical outcome distributions.

## PRD changes needed before implementation

These are proposed amendments; `PRD.md` has not been rewritten in Phase 1.

| PRD sections | Required change | Source evidence / implementation consequence |
| --- | --- | --- |
| §4, §6, §18 and definition of done | Replace implicit full ED coverage with a reviewed indicator-scope registry and coverage matrix by plan cycle/indicator. Permit partial historical analysis with explicit gaps. Seek a fuller progress export or explanation if complete coverage is required. | Workplans include all domains; several standard ED metrics are absent from progress. First-cycle eight-string ED match coverage is 7.6%, not the 62.1% all-data rate. |
| §5, §12, §20, §22, §33 | Replace ambiguous `fiscal_year` with `plan_fiscal_year`, `report_fiscal_year`, and nullable observation-period fields. Specify filter behavior for each view. | P2026-27 describes 2025/26 plans; W2026-27 is current planning. Progress notes include partial-year performance. |
| §6, §10, §18, §21 | Count reporting organizations, disclose unknown model, and exclude explicit test entities through an audited rule. Do not promise matched-model comparison for unknown models. | Five test rows; blank/`No type available` models; hospital networks and site-specific indicators coexist. |
| §10, §31 | Add source-label alias maps, dated organizational relationships, file checksums and record-level lineage. | Stable raw names can differ from selector names; Waterloo appears after two names disappear. The files do not prove the organizational relationship. Source filename alone cannot identify a record. |
| §11, §15, §16 | Extend indicator metadata with statistic, unit, population, acuity, site/clock context, comparability and definition version. Add an explicit missing/unknown row-level indicator type. | No direction/type column; mean versus percentile and multiple clock times; progress unit/population omitted; some workplan units are invalid or underspecified. |
| §12 and §9 output structure | Replace the flat intervention/outcome store with the normalized grain above; retain child method/process details and shared measurement outcomes. | Hundreds of organization/indicator groups have multiple ideas; repeated idea rows contain real detail differences; some same-label groups have distinct populations or conflicting baselines. |
| §12, §19 | Correct actual source mappings: progress `methods` is a Y/N flag, `process_measure` is implementation narrative, and `progress2` is commentary. Treat lessons as narrative content, not a fabricated source column. | Direct inspection of both progress files. Workplan `methods2`, `process_measure3`, `goal2` are separate planned-detail fields. |
| §14 | Classify at documented association grain; preserve bundles, review conflicts, and version rules/overrides. Do not derive initiative counts from text snippets. | A paragraph can contain several numbered actions; an idea can appear under several indicators and process details. |
| §16, §18, analytics rules | Specify rates, distinct-count grains, denominators, missing/mixed status, percent versus percentage points, and equality/tolerance policy. | Repeated/shared outcomes and conflicting Y/N groups; “No material change” has no defined threshold. Numeric baseline missingness must not disable otherwise valid target attainment. |
| §18, §21, statistical restraint | Only compare compatible measurement definitions/populations/windows. Remove any implied comparable annual series where dates are unknown; no “best hospital” or arbitrary ranking. | Progress reporting periods are unstructured or absent and performance can use local/site-specific definitions. |
| §32, §33 | Report exact candidate coverage, unambiguous linkage, review-resolved linkage, scope-specific coverage and progress-only records separately. Add cardinality/collision checks. Do not accept a join on organization/indicator alone as an initiative match. | Exact joins can produce 1,202/1,288 rows through duplication; broad normalization adds no covered rows and increases ambiguity. |
| §39 and methodology page | Document export-selection limits, incomplete follow-up, source-token meanings/unknowns, group-level outcomes shared by ideas, test exclusions, model gaps, and unknown periods. | These limitations affect what the proposed dashboard can honestly answer. No export retrieval timestamp or authoritative code dictionary is supplied. |

The proposed analytical views remain feasible in stages, but hospital-model comparisons, pooled trend displays and outcome callouts must be conditional on eligible data. “Which initiatives were implemented?” can use preserved reported flags and an explicit aggregation rule. “What happened afterward?” can use eligible progress measurements with linkage/coverage information. Neither question can be answered for an absent follow-up record by assuming an outcome.

## Phase 2 acceptance checks

Before producing the first normalized dataset:

- Reconcile every input source record to retained, duplicate-linked, excluded, or review-pending status; none disappear silently. Verify file checksums and exact schema headers; stop or reprofile on unexpected schema changes.
- Ensure all raw numeric strings remain recoverable, nonnumeric tokens parse to null with their own flags, and actual zeros remain zero. Review the listed population/unit/value conflicts.
- Validate foreign keys and explicit uniqueness constraints at resolved grains. Check that shared observation IDs survive joins and that adding method details cannot change an outcome denominator.
- Produce a match audit for both prescribed cycles, with raw/candidate/accepted/ambiguous/unmatched counts from both sides, including ED-scope counts and all exclusions. Regression-check the Phase 1 figures before any reviewed reconciliation changes them.
- Keep current workplan rows separate from observed outcomes. Preserve mixed implementation status; ensure unavailable baseline and target are evaluated independently.
- Version and document organization/indicator aliases, scope decisions, classification rules, exclusions, calculation definitions and any source-enrichment evidence.

## Validation performed and remaining limits

Profiling used Python's standard library against all source rows, not a preview or pandas' default missing-value conversion. A second read using `csv.DictReader` independently checked inventory counts, source-column counts, exact duplicates, numeric token counts, per-column blank counts, and exact join cardinalities. Generated report tables and the quality CSV were checked against the source-derived totals. Source SHA-256 hashes were rechecked after writing the documentation.

No frontend/package manifest, lint/typecheck configuration, application tests, or build exists in this repository. Application lint, typecheck, tests, build and browser QA are therefore **not runnable/applicable to this documentation-only phase**; they are not reported as passing. Executed validation consists of source parsing and profiling assertions. UI/browser checks remain for the later phases specified in `AGENTS.MD`.

Unresolved before publishable analytics: authoritative implementation/code meanings, complete progress-export coverage, reviewed ED scope/indicator aliases and units, ambiguous detail/measurement linkage, institutional succession evidence, and the period-comparability policy. These limits do not prevent Phase 2 from preserving and validating data; they prevent treating unresolved records as established analytical facts.

### Source fingerprints

SHA-256 values identify the exact bytes profiled (including BOM). No input file was rewritten.

| Source file | SHA-256 |
| --- | --- |
| `WorkplanIndicatorReport 2024-25.csv` | `9772e4124db9000923df7ee0723b6c5954285930dee8a3dad72efbcf089e68be` |
| `ProgressReportIndicatorReport 2025-26.csv` | `2d5012536ed5ac5f9e0e255fec2131c2e0ce54d8782e454c2c26de9965c72b73` |
| `WorkplanIndicatorReport 2025-26.csv` | `161ce5fbf507dd667d6dc24dad51011bd988de49fcb53fc2805a29335914ff7f` |
| `ProgressReportIndicatorReport 2026-27.csv` | `6e6459eb666246e5c840b4d605cf5548dd9d9493406d8ba5673cd77e4809033c` |
| `WorkplanIndicatorReport 2026-27.csv` | `fd960952b94a17c6133039e5515cdb29b133b2905b36909786e69941eb196f09` |

### Reproducing the core Phase 1 checks

The profiling analysis did not install dependencies or add a Phase 2 build script. The following read-only command, run from the repository root, reproduces source row/header counts, full-row duplicate excess, and the two exact match audits using only Python. The detailed definitions above specify how to extend these checks in `scripts/profile_data.py` during Phase 2. The source fingerprints identify the snapshot; the delivered quality CSV exposes 362 aggregate checks with their denominators and token spellings.

```sh
python3 - <<'PY'
import csv
from collections import Counter
from pathlib import Path

sources = {}
for path in sorted(Path('data').glob('*.csv')):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        rows = list(reader)
        headers = reader.fieldnames
    assert all(None not in row and None not in row.values() for row in rows)
    duplicates = len(rows) - len({tuple(row[h] for h in headers) for row in rows})
    sources[path.name] = rows
    print(path.name, 'rows', len(rows), 'columns', len(headers),
          'duplicate excess', duplicates)

for plan_year, report_year in [('2024-25', '2025-26'), ('2025-26', '2026-27')]:
    workplan = sources[f'WorkplanIndicatorReport {plan_year}.csv']
    progress = sources[f'ProgressReportIndicatorReport {report_year}.csv']
    def keys(rows, idea_column):
        return Counter((r['org_name_Text2'], r['measure_header_Text2'],
                        r[idea_column]) for r in rows)
    w = keys(workplan, 'planned3')
    p = keys(progress, 'planned_initiative')
    common = w.keys() & p.keys()
    print(plan_year, '->', report_year,
          'workplan candidate rows', sum(w[k] for k in common), '/', len(workplan),
          'progress candidate rows', sum(p[k] for k in common), '/', len(progress),
          'unique one-to-one', sum(w[k] == p[k] == 1 for k in common),
          'unsafe join rows', sum(w[k] * p[k] for k in common))
PY
```
