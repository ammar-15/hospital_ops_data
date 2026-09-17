"""Evidence gates for comparison; report fiscal years are not observation dates."""

import json
from datetime import date

from scripts.normalize import Row, packed

FIRST_CYCLE_REASON = "insufficient first-cycle ED longitudinal coverage"


def comparison_flags(cycle: Row, metadata: Row, review: Row | None = None) -> Row:
    definition_ok = metadata.get("definition_verified", False) in (True, "true")
    unit_ok = definition_ok and cycle["normalized_unit"] in metadata.get("expected_units", [])
    population_ok = definition_ok and cycle["normalized_population"] in metadata.get("expected_populations", [])
    matched = cycle["match_status"] == "matched" and cycle["cycle_valid"] == "true"
    unit_ok = unit_ok and matched
    population_ok = population_ok and matched
    verified = False
    periods_comparable = False
    evidence = "No reviewed evidence establishing both observation windows for this cycle"
    dates = dict.fromkeys(["baseline_start", "baseline_end", "followup_start", "followup_end"], "")
    if review:
        source_ids = set(json.loads(cycle["workplan_source_ids"]) + json.loads(cycle["progress_source_ids"]))
        refs = json.loads(review["evidence_source_ids"])
        if not refs or not set(refs) <= source_ids or not review["evidence_note"].strip():
            raise ValueError("Comparison review requires evidence from this cycle")
        dates = {key: review[key] for key in dates}
        b0, b1, f0, f1 = [date.fromisoformat(dates[k]) for k in dates]
        if b0 > b1 or f0 > f1 or review["periods_comparable"] not in {"true", "false"}:
            raise ValueError("Invalid reviewed observation windows")
        verified = True
        periods_comparable = review["periods_comparable"] == "true"
        # Require nonoverlapping windows with comparable duration (allow leap days).
        if periods_comparable and (b1 >= f0 or abs((b1 - b0).days - (f1 - f0).days) > 1):
            raise ValueError("Overlapping or differently sized windows cannot be approved")
        evidence = review["evidence_note"]
    eligible = (
        matched
        and unit_ok
        and population_ok
        and verified
        and periods_comparable
        and metadata.get("indicator_outcome_eligible", False) in (True, "true")
        and cycle["direction"] in {"lower_is_better", "higher_is_better"}
    )
    reasons = []
    for ok, reason in [
        (unit_ok, "unit_unverified"),
        (population_ok, "population_unverified"),
        (verified, "reporting_period_unverified"),
        (not verified or periods_comparable, "reporting_periods_not_comparable"),
        (matched, "historical_match_unavailable_or_ambiguous"),
    ]:
        if not ok:
            reasons.append(reason)
    if not definition_ok or cycle["direction"] == "unknown":
        reasons.append("indicator_definition_unverified")
    in_primary = cycle["ed_scope"] == "included" and cycle["plan_fiscal_year"] == "2025/26"
    first_cycle = cycle["ed_scope"] == "included" and cycle["plan_fiscal_year"] == "2024/25"
    return dict(
        reporting_period_verified=str(verified).lower(),
        population_verified=str(population_ok).lower(),
        unit_verified=str(unit_ok).lower(),
        comparison_eligible=str(eligible).lower(),
        comparison_exclusion_reasons=packed(reasons),
        reporting_period_evidence=evidence,
        reporting_period_evidence_source_ids=review["evidence_source_ids"] if review else "[]",
        **dates,
        primary_analysis_period=str(in_primary).lower(),
        analysis_eligible=str(in_primary and eligible).lower(),
        analysis_exclusion_reason=FIRST_CYCLE_REASON
        if first_cycle
        else "outside primary ED analysis scope"
        if not in_primary
        else "; ".join(reasons),
    )
