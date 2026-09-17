"""Distinct-cycle summaries, with explicit denominators and drill-down IDs."""

import json
from collections import Counter, defaultdict

from scripts.normalize import Row, packed

OUTCOMES = {"improved": "Improved", "worsened": "Worsened", "unchanged": "No material change"}


def measure(numerator: int, denominator: int, grain: str = "cycles") -> Row:
    return dict(
        numerator=numerator,
        denominator=denominator,
        sample_size=denominator,
        percentage=100 * numerator / denominator if denominator else None,
        grain=grain,
    )


def attribute(values: str) -> str:
    present = {s.strip() for s in json.loads(values)} - {"", "No type available"}
    return next(iter(present)) if len(present) == 1 else "Unknown" if not present else "Conflicting"


def cycle_categories(cycles: list[Row], interventions: list[Row]) -> list[Row]:
    grouped: dict[str, dict[str, list[Row]]] = defaultdict(lambda: defaultdict(list))
    for idea in interventions:
        grouped[idea["cycle_id"]][idea["primary_category"]].append(idea)
    result = []
    for cycle in cycles:
        categories = grouped[cycle["cycle_id"]]
        count = len(categories)
        cycle.update(
            category_count_per_cycle=count,
            classified_category_count_per_cycle=len(set(categories) - {"Other"}),
            single_category_cycle=str(count == 1).lower(),
            multi_category_cycle=str(count > 1).lower(),
            has_unclassified_interventions=str("Other" in categories).lower(),
            single_classified_category_cycle=str(count == 1 and "Other" not in categories).lower(),
            hospital_model=attribute(cycle["hospital_model_values"]),
            region=attribute(cycle["region_values"]),
        )
        for category, ideas in sorted(categories.items()):
            result.append(
                dict(
                    cycle_id=cycle["cycle_id"],
                    primary_category=category,
                    intervention_category=category,
                    interventions_in_category=len(ideas),
                    cycle_outcome=cycle["outcome_class"],
                    target_met=cycle["target_met"],
                    **{
                        k: cycle[k]
                        for k in [
                            "organization_id",
                            "indicator_id",
                            "hospital_model",
                            "region",
                            "plan_fiscal_year",
                            "ed_scope",
                            "analysis_eligible",
                            "analysis_exclusion_reason",
                            "comparison_eligible",
                            "category_count_per_cycle",
                            "classified_category_count_per_cycle",
                            "single_category_cycle",
                            "multi_category_cycle",
                            "single_classified_category_cycle",
                            "has_unclassified_interventions",
                        ]
                    },
                    intervention_ids=packed(sorted(i["intervention_id"] for i in ideas)),
                )
            )
    return result


def outcome_summary(rows: list[Row]) -> Row:
    # Even callers presenting a joined/duplicated table cannot multiply outcomes.
    unique = {r["cycle_id"]: r for r in rows}
    eligible = [
        r
        for r in unique.values()
        if r["analysis_eligible"] == r["comparison_eligible"] == "true"
        and r["ed_scope"] == "included"
        and r["plan_fiscal_year"] == "2025/26"
    ]
    numeric = [r for r in eligible if r["outcome_class"] in OUTCOMES.values()]
    target = [r for r in eligible if r["target_met"] in {"true", "false"}]
    counts = {
        name + "_count": measure(sum(r["outcome_class"] == label for r in numeric), len(numeric))
        for name, label in OUTCOMES.items()
    }
    return dict(
        analyzable_cycles=measure(len(eligible), len(unique)),
        calculable_outcomes=measure(len(numeric), len(eligible)),
        insufficient_numeric_data=measure(len(eligible) - len(numeric), len(eligible)),
        **counts,
        target_met_count=measure(sum(r["target_met"] == "true" for r in target), len(target)),
        target_not_met_count=measure(sum(r["target_met"] == "false" for r in target), len(target)),
        target_unavailable=measure(len(eligible) - len(target), len(eligible)),
        eligible_cycle_ids=sorted(r["cycle_id"] for r in eligible),
        outcome_cycle_ids=sorted(r["cycle_id"] for r in numeric),
        target_cycle_ids=sorted(r["cycle_id"] for r in target),
    )


def dashboard_summary(tables: dict[str, list[Row]]) -> Row:
    cycles = tables["performance_cycles"]
    primary = [c for c in cycles if c["ed_scope"] == "included" and c["plan_fiscal_year"] == "2025/26"]
    primary_ids = {c["cycle_id"] for c in primary}
    ideas = [i for i in tables["interventions"] if i["cycle_id"] in primary_ids]
    names = sorted({i["primary_category"] for i in tables["interventions"] + tables["current_workplans"]})
    current_ids = {g["current_plan_group_id"] for g in tables["current_plan_groups"] if g["ed_scope"] == "included"}
    current = [i for i in tables["current_workplans"] if i["current_plan_group_id"] in current_ids]
    result: Row = dict(
        schema_version="1.0",
        scope="Eight defined ED indicators; 2025/26 Workplan → 2026/27 Progress Report",
        category_outcome_language="cycles containing this intervention category",
        outcome_grain="unique organization-indicator cycles; categories overlap and are not additive",
        zero_denominator_display="Not available; never display a null percentage as 0%",
        analysis_status="available"
        if any(c["analysis_eligible"] == "true" for c in primary)
        else "no_verified_comparisons",
        primary_ed_cycle_candidates=measure(len(primary), len(primary)),
        matched_ed_cycles=measure(sum(c["match_status"] == "matched" for c in primary), len(primary)),
        numeric_change_candidates_before_period_verification=measure(
            sum(c["numeric_change_candidate"] == "true" for c in primary), len(primary)
        ),
        analyzable_ed_cycles=outcome_summary(primary)["analyzable_cycles"],
        calculable_ed_outcomes=outcome_summary(primary)["calculable_outcomes"],
        overall=outcome_summary(primary),
        category_counts={
            name: measure(sum(i["primary_category"] == name for i in ideas), len(ideas), "historical idea associations")
            for name in names
        },
        implementation_status_counts={
            name: measure(
                sum(i["implementation_status"] == name for i in ideas), len(ideas), "historical idea associations"
            )
            for name in ["Implemented", "Not implemented", "Partial/conflicting", "Unknown"]
        },
        implementation_population="All primary-period ED idea associations, including progress-only; distinct from outcome eligibility",
        current_2026_27_plan_counts_by_category={
            name: measure(
                sum(i["primary_category"] == name for i in current), len(current), "current ED idea associations"
            )
            for name in names
        },
        outcome_counts_by_category={},
        outcome_counts_by_category_single_classified={},
        outcome_counts_by_hospital_model={},
        outcome_counts_by_region={},
        outcome_counts_by_indicator={},
        category_structure={
            name: measure(sum(c[name] == "true" for c in primary), len(primary))
            for name in [
                "single_category_cycle",
                "multi_category_cycle",
                "single_classified_category_cycle",
                "has_unclassified_interventions",
            ]
        },
        fully_verified_ed_indicator_definitions=sum(
            i["ed_scope"] == "included" and i["definition_verified"] == "true" for i in tables["indicators"]
        ),
    )
    for name in names:
        ids = {b["cycle_id"] for b in tables["cycle_categories"] if b["primary_category"] == name}
        cohort = [c for c in primary if c["cycle_id"] in ids]
        result["outcome_counts_by_category"][name] = outcome_summary(cohort)
        result["outcome_counts_by_category_single_classified"][name] = outcome_summary(
            [c for c in cohort if c["single_classified_category_cycle"] == "true"]
        )
    for dimension in ["hospital_model", "region", "indicator_id"]:
        key = "indicator" if dimension == "indicator_id" else dimension
        for value in sorted({c[dimension] for c in primary}):
            result["outcome_counts_by_" + key][value] = outcome_summary([c for c in primary if c[dimension] == value])
    counts = Counter(c["analysis_exclusion_reason"] for c in primary if c["analysis_eligible"] != "true")
    result["exclusion_counts"] = {reason: measure(n, len(primary)) for reason, n in sorted(counts.items())}
    known = [
        i
        for i in ideas
        if i["implementation_status"] in {"Implemented", "Not implemented"}
        and i["association_review"] != "needs_review"
    ]
    result["implementation_rate"] = measure(
        sum(i["implementation_status"] == "Implemented" for i in known), len(known), "historical idea associations"
    )
    return result
