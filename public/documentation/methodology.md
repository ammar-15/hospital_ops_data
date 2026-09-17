# Phase 2 methodology

This is a descriptive, reproducible pipeline for Ontario hospital Quality Improvement Plan (QIP) exports. It organizes reported plans, implementation flags and subsequent measurements. It does not estimate intervention effects, rank hospitals, predict performance or recommend treatments. Phase 2 contains no frontend.

## Sources and cycle relationships

The immutable inputs are the five CSV files directly under `data/`. `config/sources.json` records their exact ordered schemas, SHA-256 hashes, report types, report years and expected row counts. The detailed schema inventory and original matching diagnostics remain in [data-profile.md](data-profile.md).

| Workplan | Following progress report | Workplan rows | Progress rows, before exclusions |
| --- | --- | ---: | ---: |
| WorkplanIndicatorReport 2024-25.csv | ProgressReportIndicatorReport 2025-26.csv | 1,688 | 1,102 |
| WorkplanIndicatorReport 2025-26.csv | ProgressReportIndicatorReport 2026-27.csv | 1,742 | 1,246 |
| WorkplanIndicatorReport 2026-27.csv | Not available | 1,804 | Not applicable |

`plan_fiscal_year` identifies the planned activity; `progress_report_fiscal_year` identifies its subsequent report. Neither field supplies an observation date. No next-workplan baseline is substituted for a progress result. Current 2026/27 plans have no outcome or implementation-result columns and never enter `performance_cycles.csv`.

The build fails on changed source bytes, schemas, counts, unused exclusions, unmapped labels or unresolved mapping entries. To adopt new source exports, profile them first and explicitly revise the source manifest and relevant mappings. The build does not regenerate or guess mapping decisions.

## Revised grain and output contracts

The user's Phase 2 model supersedes the PRD's proposed flat intervention/outcome table. An outcome belongs to **one organization + normalized indicator identity + QIP workplan/progress cycle**. Different ideas in that cycle reference the same outcome.

| File under `data/processed/` | Grain and purpose |
| --- | --- |
| `performance_cycles.csv` | One historical organization–indicator–cycle candidate; deterministic `cycle_id`. Includes unmatched candidates and flagged unresolved groups, so missing follow-up remains visible. |
| `cycle_categories.csv` | One unique cycle + primary category, with count of linked ideas, shared cycle outcome, eligibility and category-count flags. |
| `dashboard_summary.json` | Vetted primary ED counts and outcome summaries with numerators, denominators, sample sizes and drill-down cycle IDs; current ED plans separate. |
| `interventions.csv` | One distinct verbatim change-idea association within a historical cycle; `intervention_id`, foreign key `cycle_id`. No independently assigned numeric outcome or outcome class. |
| `organizations.csv` | One included reporting organization; original labels, normalized display name, reported region/model and lineage. |
| `indicators.csv` | One source-exact indicator definition identity; normalized display name, direction, allowed units/populations, ED scope, original reported domains and lineage. |
| `current_workplans.csv` | One 2026/27 change-idea association, classified using the same taxonomy. References `current_plan_group_id`, not a historical cycle. |
| `current_plan_groups.csv` | One current organization–indicator group, with source links and idea count; no observed outcomes. |
| `source_files.csv` | One immutable export: checksum, filename, encoding, report year, ordered headers and constant export fields. |
| `source_records.csv` | Every original nonempty CSV record, including duplicates and excluded tests; raw variable fields, file ID, record number, physical line span, row hash and duplicate/exclusion flags. |
| `source_observations.csv` | Every original performance field: source record/column, raw value, parsed decimal string or empty value, and explicit source status. Includes excluded records for audit only. |
| `source_measurement_contexts.csv` | Every included workplan source record's raw and normalized unit/population, dimensional compatibility and original source/period text; covers historical and current plans. |
| `record_lineage.csv` | Every included source record → idea → historical cycle or current group. Multiple detail rows and exact duplicates remain individually recoverable. |
| `data_quality_issues.csv` | Cycle or source-context issues with reasons and source references. Multiple issues may describe the same entity. |
| `data_quality_summary.csv` | Counts, coverage and explicit rate numerators/denominators, separately for all hospitals and the ED registry, both historical pairs and their union. |
| `build_manifest.json` | Pipeline version, configuration/code hashes and output table row counts. No clock-dependent fields. |

Lists and sets inside CSV cells are JSON, including source references and retained narrative variants. Parse them as JSON, not comma-separated strings. Nullable scalar numeric fields are empty strings in CSV, never zero. Read with `dtype=str, keep_default_na=False, na_filter=False` in pandas. Boolean scalars use `true`/`false`; empty `target_met` means not calculable.

`cycle_valid=true` means the candidate has no conflicting source measurement facts/context. It does **not** imply follow-up is present or an outcome can be calculated. `match_status`, `comparable`, direction and numeric statuses are separate gates. Four ambiguous groups retain a single cycle placeholder with `cycle_valid=false`; the pipeline does not invent population/site identities to split them or average their values.

An idea means a documented text association, not a verified atomic project. Multiple numbered actions inside a paragraph remain one idea. Identical idea text at another hospital, under another indicator or in another cycle is a separate association. Repeated exact idea text within a cycle consolidates detail rows, retaining all source references, methods, process measures, targets, notes and flags. A changed idea remains distinct. Ambiguous cycle associations carry `association_review=needs_review`.

## Normalization and explicit mappings

- `config/organization_mappings.csv`: one exact raw label per mapping. Trim display whitespace, including Brightshores and Hotel Dieu Cornwall. Preserve all raw text. Grand River, St. Mary's and Waterloo remain separate identities; no institutional succession is inferred.
- `config/indicator_mappings.csv`: one exact source definition per identity. Collapse whitespace for display only. Preserve punctuation, clock times, statistic, site, admission status and acuity distinctions in identity. No cross-label clinical equivalence is asserted. Similar display names can remain separate IDs.
- `config/unit_mappings.csv`: explicit unit aliases; `Number` and `Count` map to `count`. Hours and minutes remain different with no automatic conversion. `90th percentile` is a statistic, not a time unit; it maps to unknown. Bare `Rate` has no denominator and remains unknown. Explicit denominators retain distinct units.
- `config/population_mappings.csv`: trim and case-normalize explicit labels, retaining distinctions such as patients/all patients, staff/worker, and ED/all inpatients. `Other` and `N/a` are unknown. No guessed population is introduced.
- `config/indicator_metadata.json`: versioned, source-exact direction, expected units/populations, ED scope and rationale. The eight V1 ED definitions now have official direction/unit/population evidence and published period metadata; see [indicator-metadata.md](indicator-metadata.md). Legacy nonspecific ED LOS is now unknown. Non-ED wording interpretations do not establish verified definitions or grant calculations. Direction is never inferred from numeric values.

Duplicate mapping keys, multiple raw labels assigned to the same identity, and nonaccepted mapping entries stop the build. Adding reviewed clinical aliases later requires extending the explicit contextual mapping policy and tests; punctuation removal or fuzzy matching cannot silently merge them now. This intentionally conservative registry limits cross-year series and full-hospital outcome coverage.

Missing hospital model values remain empty, with their original blank versus `No type available` values retained. Organizations are reporting entities and may cover multiple campuses. No model or campus count is inferred from external familiarity.

## ED Access & Flow subset

The initial included registry is exactly the eight standard indicator strings in the Phase 1 ED table: ambulance offload, physician initial assessment, the 8 a.m. inpatient-bed backlog, nonadmitted low- and high-acuity length of stay, admitted length of stay, time to inpatient bed, and left without being seen. Their direction is `lower_is_better`.

All eight retain separate identities and unit/population requirements. The legacy nonspecific `90th percentile ED length of stay` has a separate identity and unknown direction and remains outside the included ED registry pending scope review. Other local variants default to `needs_review`. Thus ED diagnostics describe this **defined subset**, not every possible ED measure. The full hospital dataset retains all non-test records, including safety, equity and experience initiatives. Access and Flow domain alone is not an ED filter.

## Exclusions and traceability

`config/exclusions.csv` contains five exact file/record/organization exclusions: progress 2026/27 records 4–6 (`Hospital A (TEST) (TEST)`) and 556–557 (`Hospital xyz1 (TEST)`). Their organization names are verified against the specified source records at build time. No test-name filter is hardcoded in transformation logic.

These rows are absent from analytical cycles, ideas, current plans and dimensions. They remain explicitly marked in source audit tables. Their presence there is preservation, not inclusion in a denominator. There are 7,582 original records and 7,577 included lineage records.

Original CSV bytes are never rewritten. The eight constant export/selector columns are stored once per source file; the remaining original fields are stored losslessly in `raw_fields_json`. Together they reconstruct every original field. Record numbers count CSV records with header = 1; physical line spans also account for quoted multiline text. Original filenames, organization/indicator labels, ideas and every numeric token are recoverable.

Full-row duplicates get `duplicate_of` references. They do not create extra cycle or idea counts, while distinct methods and notes remain source detail records. No workplan detail is paired with a progress detail by row order. A drill-down follows cycle → idea → source record → raw fields and file metadata.

## Matching and ambiguity

1. Group included records by explicit organization ID, indicator ID and the prescribed cycle. Take the union of both sides, retaining workplan-only and progress-only groups.
2. Consolidate repeated numeric formats using Decimal equivalence (`3.1` equals `3.10`). Distinct source statuses remain distinct. Do not resolve disagreement by majority, first row or averaging.
3. Require a single workplan measurement context: compatible unit/population identities and one baseline source/period string. Multiple previous, target or subsequent facts, or conflicting context, flag the group as ambiguous. Three first-cycle groups and one second-cycle group need review.
4. Accept a cycle link when both sides exist and the group is unambiguous. Unknown direction or unit can prevent calculation without negating its identity match. `match_method=exact` records raw organization/indicator equality. No fuzzy or cross-label normalized links are accepted in this snapshot.
5. Within each cycle, associate identical verbatim idea text only. Changed/unmatched progress ideas are retained as `progress_only`; a cycle match alone does not establish implementation of a different planned idea. Exact idea candidate coverage can include ambiguous cycles and is reported separately from accepted cycle matches.

`workplan_cycle_match_rate_pct = accepted matched cycles / all workplan cycle candidates × 100`. The denominator includes ambiguous workplan candidates. Progress-side coverage uses progress cycle candidates. Row-weighted cycle coverage and exact-idea candidate row coverage are additional, explicitly named diagnostics; they must not replace cycle rates without relabeling.

## Numeric statuses and calculations

Only plain signed decimal strings are numeric. Preserve `CB`, `X`, `NA`, `N/A`, blanks and unrecognized text as explicit statuses, with their exact raw source values available. Their authoritative meanings are not supplied by these files; do not silently expand CB or treat X as a numeric suppression bound. Malformed numbers, percent-decorated strings, infinity and NaN are not silently repaired. Real zero remains zero.

For an accepted historical cycle, a progress measurement inherits unit/population metadata **only from its unambiguous preceding workplan**. Progress-only groups cannot inherit metadata from other years. Whitelists prevent a time indicator from accepting a count or an incompatible population. No unit conversion or scale inference occurs.

Comparability policy: `comparison_eligible` requires a verified indicator definition, known direction, compatible documented units/population, an accepted historical match and verified comparable observation windows. `comparable` is an alias. Both improvement and target calculations require this gate. Only `analysis_eligible=true` comparisons in the 2025/26 → 2026/27 defined ED cohort enter aggregates. First-cycle ED records remain in all audit/detail datasets, carrying `analysis_eligible=false` and the exact reason `insufficient first-cycle ED longitudinal coverage`.

The earlier inherited-context assumption is retired. Full flag definitions, published periods and source exceptions are in [reporting-period-review.md](reporting-period-review.md). Date evidence is versioned in `config/comparison_reviews.csv`; one entry verifies incompatible overlapping windows, and there are no approved comparable pairs. Unverified windows remain empty rather than fabricated dates. `numeric_change_candidate` reports numeric availability under the former context gate without assigning an outcome.

For previous value `b` and current value `c`:

- `performance_change = c - b` in the source unit.
- `performance_change_pct = 100 × (c - b) / abs(b)`, only for nonzero `b`.
- `improvement_pct` reverses that sign for lower-is-better indicators and retains it for higher-is-better indicators. Positive means improvement. It is empty for zero baseline, even though absolute change and outcome can still be calculated.
- `Improved` and `Worsened` follow indicator direction.
- `No material change` means **exact Decimal numeric equality only**. Threshold = 0 in the indicator's unit. No source-supported material or clinical tolerance exists. This label does not assert statistical or clinical equivalence; display “exactly unchanged” as clarification.
- `Insufficient data` covers missing follow-up, nonnumeric values, unknown direction, incompatible/unknown context or ambiguity. Reasons remain machine-readable.

Target attainment is separate: `c <= target` for lower-is-better and `c >= target` for higher-is-better. It requires numeric target/current and the same identity/context/direction gates, but no numeric baseline. A missing target does not disable an otherwise eligible improvement calculation. Conflicting baseline/target facts can indicate unresolved measurement identity and conservatively block both; merely nonnumeric baseline does not.

For percentage-valued measures, absolute change is in percentage points; relative change is a percentage. Never average hours, minutes, counts and percentages together. Even relative changes should only be summarized within compatible definitions/populations/windows, with denominators and weighting specified.

## Implementation status

Progress `methods` is the reported Y/N flag. `process_measure` is implementation narrative; `progress2` is commentary. Workplan `methods2`, `process_measure3` and `goal2` are planned detail fields. There is no invented source `lessons_learned` column.

For an exact idea association, all retained flags Y → `Implemented`; all N → `Not implemented`; both Y and N → `Partial/conflicting`; no flags or unresolved/unknown flag values → `Unknown`. Narratives do not override flags. These statuses reflect the source report, not independently verified completion.

At cycle level the same aggregation summarizes all reported flags. A cycle with some implemented and some unimplemented **different** ideas is partial, but not necessarily contradictory. `implementation_conflict_count` counts ideas with their own conflicting Y/N details. The snapshot has seven conflicting ideas across six cycles. Cycle-level mixed status has a separately named diagnostic.

If showing an implementation rate later, use exact idea associations classified Implemented divided by those classified Implemented or Not implemented. Disclose excluded Partial/conflicting, Unknown and needs-review associations, and explicitly select whether progress-only ideas are included. Do not count raw detail rows as independent implementations.

## Intervention classification

Version 1.1 of `config/intervention_taxonomy.json` uses transparent regex rules on the **change idea only**. Original rules retain their assignments; when none match, specific refinement rules run. Highest matched-rule count wins, and taxonomy order breaks ties. Up to three other matching categories become secondary tags. No match produces Other. The added Safety & Risk Prevention category brings the taxonomy to 15 categories including Other.

Historical Other falls from 1,635/3,428 (47.70%) to 1,171/3,428 (34.16%). The reproducible [taxonomy review](taxonomy-review.md) lists recurring phrases, every rule's affected counts, additive reassignment counts and deferred concepts. Raw text, matched patterns/rule IDs, version, qualitative confidence and reasons remain in each idea record. These are rule assignments, not probabilities or human-certified labels; vague ideas remain Other.

`config/classification_overrides.csv` initially contains headers only. To review an assignment, add its stable intervention ID, one taxonomy category, JSON secondary tags and a nonempty reason. Overrides are validated, recorded as such, and take precedence. An unknown/unused override ID stops the build. Current ideas use the same rules and can also receive explicit overrides. No LLM/API is used.

## Aggregation rules for the later dashboard

The primary ED outcome window is **2025/26 Workplan → 2026/27 Progress Report**. `analysis_eligible` includes scope, period and comparability gates; it does not require a numeric baseline. Improvement and target attainment each have separate calculable denominators. Count distinct cycles, not ideas or raw detail rows. Current 2026/27 ideas never receive historical outcomes.

`dashboard_summary.json` contains the vetted overall and category/model/region/indicator summaries. Each metric object retains `numerator`, `denominator`, `sample_size` (equal to the denominator), `percentage` and `grain`. An empty denominator produces JSON `null`, not 0%. Outcome rates use calculable eligible cycles; target rates use eligible cycles with numeric target/current, independently of baseline. Coverage metrics use explicitly broader candidate denominators. Cycle IDs support drill-down; current-plan and implementation/category counts are labeled idea-grain and are not restricted by outcome availability. The ED implementation summary includes progress-only associations and excludes unknown/partial statuses from its rate, while retaining all statuses in counts.

`cycle_categories.csv` contains exactly one row per cycle and distinct **primary** category. Multiple ideas in a category increase `interventions_in_category`, never the outcome denominator. A cycle can appear in several categories, so category outcome denominators are not additive. The bridge covers all retained history; summary charts filter to primary ED and verified comparisons. Region/model use cycle source attributes, preserving absent/conflicting values as explicit Unknown/Conflicting groups instead of dropping them or borrowing future attributes.

`category_count_per_cycle` counts distinct primary labels **including Other**. `single_category_cycle` means exactly one label; `multi_category_cycle` means more than one. `classified_category_count_per_cycle` excludes Other. For the optional only-classified-category comparison, use `single_classified_category_cycle=true`: exactly one category and no Other ideas. This avoids presenting an incompletely classified bundle as isolated. Secondary tags are not extra bridge categories. Neither subset establishes causal isolation.

Required category language: **“cycles containing this intervention category.”** If outcomes become available, a valid statement is “63% improved (17 of 27 analyzable cycles containing this intervention category).” It must name the cohort and calculable denominator. Do not attribute the shared outcome to an individual idea, sum category outcomes into a total, or generate causal explanations. Outcome-after-implementation filtering must select relevant implemented idea associations and then deduplicate cycles.

No mixed-unit or cross-definition percentage-change averages, persistent-issue classifications, arbitrary scores, rankings, predictions or recommendations are produced.

## Refined snapshot results

| Measure | All retained historical records | Primary-period ED cohort |
| --- | ---: | ---: |
| Cycle candidates | 1,669 | 206 |
| Accepted matched cycles | 1,047 | 130 |
| Numeric ED change candidates before period verification | — | 129 |
| Analysis-eligible cycles | 0 | 0 |
| Calculable headline outcomes / targets | 0 / 0 | 0 / 0 |
| Historical idea associations | 3,428 | 370 |
| Ideas classified Other | 1,171 (34.16%) | 111 (30.00%) |
| Single-category / multi-category cycles | 980 / 689 | 130 / 76 |

The full history contains 272 ED cycles, including 66 first-cycle candidates retained only for history. The old four first-cycle and 129 primary-cycle ED outcomes were calculated under the superseded inherited-context assumption; their source values remain, but they are no longer approved calculated outcomes. One primary cycle has verified incompatible dates; 205 lack verified pairs. Eight ED **definitions** are fully verified; no hospital comparison currently has all required evidence.

There are 2,644 unique cycle/category pairs. Fifteen primary labels are observed (14 substantive categories plus Other). Current 2026/27 plans remain separate: 1,739 ideas in 866 groups across all indicators, with 627 Other (36.06%). The current ED subset and its category counts are separately identified in the dashboard JSON. All 134 included organizations are reporting entities, not a census of physical hospital sites. Four ambiguous historical groups and seven conflicting implementation ideas remain flagged.

Accepted cycle match coverage is unchanged: all-hospital 475/817 and 572/849; ED 5/66 and 130/206. Match coverage is not comparison eligibility.

## Limitations that affect dashboard design

Headline outcome charts need an explicit unavailable state, not zero-percent bars. Show candidates, matched cycles, numeric candidates, verified comparisons and reasons separately. Retain raw measurements/notes for audit without plotting them as comparable annual outcomes. Additional period/ERNI/site evidence is required before presenting valid before/after or hospital comparison rates. Definition metadata alone cannot fill that gap.

Keep first-cycle ED history outside headline totals; do not imply a representative two-year trend. Keep current plans visibly separate. Display sample sizes, overlapping-category notes, Other coverage and the only-classified-category filter. Rule labels remain reviewable, local indicator variants remain separate, and missing models must remain visible. Hospital networks may cover different sites.

Patient volume, acuity, staffing, capacity, seasonality and concurrent activities can affect reported performance. Observations cannot establish that an intervention caused a change. Source audit tables/narratives should be loaded on demand in later UI work. No frontend has been built in this refinement pass.

## Validation and reproduction

Run the commands in [README.md](../README.md). The build validates before writing processed tables. The standalone validator reloads CSVs with lossless pandas settings and checks IDs, foreign keys, source coverage, numeric statuses, conflict preservation, unit/population gates, calculations, current-plan separation and exclusions. Tests also reconstruct every original source field and physical line span, test rejected corruptions, independently exercise formulas and verify byte-identical full rebuilds.

The source inventory is pinned deliberately. After changing rules or mappings, rebuild, run all checks, inspect diagnostics and update this snapshot section. Outputs and configuration are analytical artifacts; neither compilation nor a successful CSV write alone constitutes validation.
