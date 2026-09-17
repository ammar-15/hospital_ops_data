// Keep this concise mirror in sync with assistant/project-context.md. It is bundled
// server-side so every request is grounded without runtime filesystem access.
export const PROJECT_CONTEXT = `
Project: Ontario Hospital Quality Improvement Explorer. A public descriptive explorer of Ontario Health QIP reporting about ED access and patient flow. It is not live operational data or a hospital-choice tool.

Sources and years: processed Workplan Indicator Reports for 2024/25, 2025/26, 2026/27, and Progress Report Indicator Reports for 2025/26, 2026/27. Workplans describe planned change ideas, baseline/target context and methods. Progress Reports contain later implementation reporting, comments and submitted values. Historical activity is 2024/25 and 2025/26 workplan cycles; 2026/27 is current plans only, with no following Progress Report.

Pages: Overview; Intervention Explorer; Hospital Explorer; Current Plans; Reporting & Data Quality; Methodology. Filters: workplan fiscal year, region, hospital model, reporting organization, indicator, intervention category, implementation status, report cohort. KPI cards describe selected activity and coverage, not scores/rankings. Implementation-status coverage means historical ideas with Implemented, Not implemented, or Conflicting status divided by selected historical ideas; it is not implementation success.

15 categories: Admission & Transfer Process; Ambulance / EMS Flow; Bed & Capacity Management; Care Coordination & Communication; Data, Measurement & Dashboards; Discharge & Transition Planning; Emergency Department Workflow; Other; Patient Streaming / Triage; Policy / Standardization; Safety & Risk Prevention; Staffing & Scheduling; Surge Management; Technology & Digital Tools; Training & Education. These are deterministic project classifications, not official Ontario Health categories.

Eight reviewed ED indicators: ambulance offload time; time to physician initial assessment; patients waiting for an inpatient bed at 8 a.m.; ED length of stay for nonadmitted low-acuity patients; ED length of stay for nonadmitted high-acuity patients; ED length of stay for admitted patients; time to an inpatient bed; patients leaving without being seen. Ambulance offload time is the time from ambulance arrival to transfer of care, shown as a 90th-percentile measure.

Cleaning/matching: processed data preserve original text/numeric tokens and source IDs, normalize mapped names, classify ideas with versioned deterministic rules, and retain source drill-down. Historical matching begins with exact organization, indicator and change-idea keys. Unmatched/ambiguous records remain visible. Statuses are Implemented, Not implemented, Unknown, or Partial/conflicting; conflicts stay visible.

Limit: reporting windows, population/unit context, participation and site coverage are not consistently verified. No cycle passes all comparison gates. Outcomes, target attainment and intervention effectiveness are Unavailable, not zero. Do not rank hospitals, claim causality, call an intervention best, or interpret submitted values as comparable outcomes. When unsupported, say so.
`;
