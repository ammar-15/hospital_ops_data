# Deterministic taxonomy review

Review date: 2026-09-16. Run `python scripts/review_taxonomy.py` after rebuilding to regenerate this document.

Original historical Other: **1,635 of 3,428 (47.70%)**. Final historical Other: **1,171 of 3,428 (34.16%)**. 464 previously unclassified associations now have explicit rule support.

The denominator is distinct historical change-idea associations across all hospital indicators and both retained cycles. It is not raw CSV rows or the primary ED outcome cohort. No outcome values, external LLM or API inform classification.

## Recurring phrases in the original Other cohort

Counts are associations containing a phrase, at most once per association. Lowercase alphabetic bigrams/trigrams exclude the stop words recorded in the script. Phrases overlap and are descriptive clues, not automatic categories.

| Phrase | Associations |
| --- | ---: |
| patient experience | 72 |
| workplace violence | 71 |
| emergency department | 49 |
| experience survey | 24 |
| patient safety | 22 |
| patient flow | 21 |
| wait times | 21 |
| patient experience survey | 20 |
| risk assessment | 20 |
| patients who | 19 |
| violence incidents | 19 |
| working group | 19 |
| follow up | 18 |
| improve patient | 18 |
| workplace violence incidents | 18 |
| medication reconciliation | 17 |
| mental health | 16 |
| quality improvement | 16 |
| inpatient units | 15 |
| high risk | 14 |
| hand hygiene | 13 |
| lost time | 13 |
| pressure injury | 13 |
| best practices | 12 |
| p r | 12 |
| experience surveys | 11 |
| inpatient bed | 11 |
| action plans | 10 |
| acute care | 10 |
| change ideas | 10 |

## Applied rule refinements

Version 1.1 preserves all existing version 1 assignments. Refinement rules run only when no original pattern matches. The largest number of matching rules wins; taxonomy order breaks ties. This limits reclassification of previously covered ideas. Manual overrides remain first priority.

One category is added: **Safety & Risk Prevention**, for explicit preventive mechanisms such as risk assessment, hand hygiene and medication reconciliation. There are 15 primary categories including Other (14 substantive categories). Generic references to workplace violence or patient safety alone do not trigger this category.

`Hits` counts original Other associations matching a proposed regex; `winning category` counts matching associations whose final primary category is that rule's category. Both columns can overlap across rules and must not be added. Zero-hit rules are retained only as narrow vocabulary coverage. The next table gives additive reassignment totals.

| Rule ID | Category | Evidence required | Hits | Winning category |
| --- | --- | --- | ---: | ---: |
| staff_shifts | Staffing & Scheduling | Explicit staffing resources or shift coverage | 3 | 3 |
| bed_turnover | Bed & Capacity Management | Explicit allocation or turnover of beds | 7 | 7 |
| ed_process | Emergency Department Workflow | Explicit ED process or diagnostic flow action | 2 | 2 |
| referral_pathway | Admission & Transfer Process | Named referral, intake or consult process | 9 | 9 |
| survey | Data, Measurement & Dashboards | Survey or structured feedback collection; not patient experience alone | 132 | 132 |
| measurement_verbs | Data, Measurement & Dashboards | Measurement action paired with an object | 38 | 38 |
| data_quality | Data, Measurement & Dashboards | Explicit data capture or quality improvement | 10 | 10 |
| analysis_variants | Data, Measurement & Dashboards | Analysis spelling variants and explicit report review | 20 | 20 |
| incident_reporting | Data, Measurement & Dashboards | Recording/reporting incidents; not violence prevention generally | 8 | 8 |
| digital_systems | Technology & Digital Tools | Named digital system or explicit digital service | 55 | 41 |
| teaching_formats | Training & Education | Explicit teaching format or course completion | 23 | 22 |
| collaboration | Care Coordination & Communication | Explicit collaboration or navigation action | 52 | 44 |
| communication_modes | Care Coordination & Communication | Named communication or language support mechanism | 15 | 15 |
| offload_variants | Ambulance / EMS Flow | Offload spelling variants and specific EMS terms | 10 | 10 |
| streaming_variants | Patient Streaming / Triage | Named streaming approach | 4 | 4 |
| standard_work | Policy / Standardization | Explicit standard work, pathway or bundle; not generic improvement | 23 | 22 |
| risk_assessment | Safety & Risk Prevention | Explicit risk assessment or risk identification | 31 | 29 |
| safety_mechanisms | Safety & Risk Prevention | Named prevention or medication safety process | 40 | 36 |
| safety_response | Safety & Risk Prevention | Explicit prevention, response or postincident support | 21 | 20 |

| Final category among original Other | Associations |
| --- | ---: |
| Admission & Transfer Process | 9 |
| Ambulance / EMS Flow | 10 |
| Bed & Capacity Management | 7 |
| Care Coordination & Communication | 59 |
| Data, Measurement & Dashboards | 201 |
| Emergency Department Workflow | 2 |
| Other | 1171 |
| Patient Streaming / Triage | 4 |
| Policy / Standardization | 22 |
| Safety & Risk Prevention | 84 |
| Staffing & Scheduling | 3 |
| Technology & Digital Tools | 41 |
| Training & Education | 22 |

## Remaining unclassified concepts and deferred proposals

The export includes clinical care, safety, equity and patient experience beyond ED operations. Topic mentions are not an operational mechanism. The following candidate concepts are counted in the remaining Other cohort but do not trigger new categories:

| Concept / deferred category | Matching remaining Other | Decision |
| --- | ---: | --- |
| Patient experience / engagement | 35 | Consider a co-design category only after concrete actions are reviewed; experience alone is an objective. |
| Workplace violence / safety | 35 | Retain generic strategies in Other; classify only explicit mechanisms. |
| Clinical prevention / care | 81 | Do not create a catch-all clinical category from an outcome topic. |
| Equity / accessibility | 39 | A goal is insufficient to distinguish education, access redesign or policy. |
| Generic flow improvements | 36 | Do not infer bed, triage or staffing mechanisms from an aim. |

Examples deliberately left unclassified include ‘Flow Optimization’, ‘Engage key stakeholders’, and ‘Same change ideas and methods as Surgical Volumes’. Bare PODS remains ambiguous without expanded discharge wording. Bundles containing several actions remain one source idea.

## Review and traceability

`change_idea_raw` is unchanged. Each assignment retains `classification_rule_used`, full regex evidence, `taxonomy_version`, `classification_confidence`, `classification_reason`, and source-record IDs. `rule_supported` is a qualitative evidence label, not a probability or independent human validation. Mixed concepts can still be misclassified; up to three alternative matching categories remain secondary tags. The category bridge uses primary categories only.

`config/classification_overrides.csv` supports stable intervention ID, category, secondary tags and a mandatory reason. Invalid or unused overrides fail the build. Regex definitions live in `config/intervention_taxonomy.json`. Unchanged v1 rules retain their known keyword/tie-breaking limitations; the pass does not claim a fully adjudicated taxonomy.

## Cohort-specific Other shares

| Cohort | Other | Total | Other % |
| --- | ---: | ---: | ---: |
| All historical | 1171 | 3428 | 34.16% |
| Historical defined ED | 147 | 488 | 30.12% |
| Primary-period ED | 111 | 370 | 30.00% |
| Current 2026/27, all indicators | 627 | 1739 | 36.06% |
| All historical + current | 1798 | 5167 | 34.80% |
