# Ontario Hospital Quality Improvement Explorer: assistant context

This public, descriptive explorer organizes Ontario Health Quality Improvement Plan (QIP) reporting about emergency-department (ED) access and patient flow. It is not live operational data or a hospital-choice tool.

## Data and reporting

The processed source exports are Workplan Indicator Reports for 2024/25, 2025/26 and 2026/27, and Progress Report Indicator Reports for 2025/26 and 2026/27. A Workplan records a planned change idea, baseline/target context and methods. A Progress Report records later implementation reporting, comments and submitted values. Historical activity is the 2024/25 and 2025/26 workplan cycles; 2026/27 is a separate current-plan cohort with no subsequent Progress Report in this project.

Dashboard pages are Overview, Intervention Explorer, Hospital Explorer, Current Plans, Reporting & Data Quality, and Methodology. Filters narrow records by workplan fiscal year, region, hospital model, reporting organization, indicator, intervention category, implementation status, and report cohort. KPI cards describe selected activity and coverage; implementation-status coverage is historical ideas with Implemented, Not implemented, or Conflicting status divided by selected historical ideas. It is not implementation success.

## Definitions

The taxonomy has 15 primary categories: Admission & Transfer Process; Ambulance / EMS Flow; Bed & Capacity Management; Care Coordination & Communication; Data, Measurement & Dashboards; Discharge & Transition Planning; Emergency Department Workflow; Other; Patient Streaming / Triage; Policy / Standardization; Safety & Risk Prevention; Staffing & Scheduling; Surge Management; Technology & Digital Tools; Training & Education. They are deterministic project classifications of source change ideas, not official Ontario Health categories.

The reviewed ED indicators are ambulance offload time; time to physician initial assessment; patients waiting for an inpatient bed at 8 a.m.; ED length of stay for nonadmitted low-acuity patients; ED length of stay for nonadmitted high-acuity patients; ED length of stay for admitted patients; time to an inpatient bed; and patients leaving without being seen. Ambulance offload time is the time from an ambulance patient’s arrival to transfer of care, reported here as a 90th-percentile measure.

## Methods and limits

The pipeline uses processed datasets only, preserves original text and numeric tokens, normalizes names with mapped aliases, classifies ideas using versioned deterministic rules, and retains source IDs and original records for drill-down. Historical Workplan-to-Progress matching starts with exact organization, indicator and change-idea keys; ambiguous and unmatched records remain visible. Implementation flags can be Implemented, Not implemented, Unknown, or Partial/conflicting; conflicts are retained rather than resolved.

Reported historical values cannot be treated as comparable outcomes. Exports lack sufficient consistent observation-window, population, unit, participation and site-coverage evidence. No reviewed cycle currently passes all comparison gates, so outcome, target-attainment and intervention-effectiveness metrics are unavailable, not zero. The dashboard does not rank hospitals, claim causality, or identify a best intervention. Submitted source values remain traceable but require the reporting-period limitation when discussed.
