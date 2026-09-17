"""Validate generated tables independently of the build entry point."""

import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.normalize import Row, implementation, parse_numeric, resolve_value
from scripts.analytical_eligibility import comparison_flags
from scripts.dashboard_analytics import dashboard_summary
from scripts.outcomes import calculate


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(tables: dict[str, list[Row]]) -> None:
    cycles = tables["performance_cycles"]
    interventions = tables["interventions"]
    current = tables["current_workplans"]
    records = {r["source_record_id"]: r for r in tables["source_records"]}
    files = {r["source_file_id"]: r for r in tables["source_files"]}
    orgs = {r["organization_id"] for r in tables["organizations"]}
    indicators = {r["indicator_id"]: r for r in tables["indicators"]}
    cycle_map = {r["cycle_id"]: r for r in cycles}
    current_map = {r["current_plan_group_id"]: r for r in tables["current_plan_groups"]}
    allowed_outcomes = {"Improved", "No material change", "Worsened", "Insufficient data"}
    allowed_implementation = {"Implemented", "Not implemented", "Partial/conflicting", "Unknown"}
    require(len(cycle_map) == len(cycles), "Duplicate cycle IDs")
    require(
        len({(r["organization_id"], r["indicator_id"], r["plan_fiscal_year"]) for r in cycles}) == len(cycles),
        "Duplicate organization/indicator/cycle grain",
    )
    require(len(records) == len(tables["source_records"]), "Duplicate source IDs")
    for table, key in [
        (interventions, "intervention_id"),
        (current, "intervention_id"),
        (tables["current_plan_groups"], "current_plan_group_id"),
        (tables["organizations"], "organization_id"),
        (tables["indicators"], "indicator_id"),
    ]:
        require(len({r[key] for r in table}) == len(table), f"Duplicate {key}")
    for record in records.values():
        require(record["source_file_id"] in files, "Orphan source file")
        raw = json.loads(record["raw_fields_json"])
        constants = json.loads(files[record["source_file_id"]]["constant_fields_json"])
        require(
            set(raw) | set(constants) == set(json.loads(files[record["source_file_id"]]["headers_json"])),
            "Incomplete source traceability",
        )
        if record["duplicate_of"]:
            require(record["duplicate_of"] in records, "Orphan duplicate")
            require(
                records[record["duplicate_of"]]["row_sha256"] == record["row_sha256"], "Incorrect duplicate grouping"
            )
    for observation in tables["source_observations"]:
        require(observation["source_record_id"] in records, "Orphan observation")
        raw = json.loads(records[observation["source_record_id"]]["raw_fields_json"])
        require(raw[observation["source_column"]] == observation["raw_value"], "Source value overwritten")
        value, status = parse_numeric(observation["raw_value"])
        require(observation["numeric_value"] == (str(value) if value is not None else ""), "Numeric coercion error")
        require(observation["source_status"] == status, "Missing source status")
    observation_keys = Counter((o["source_record_id"], o["source_column"]) for o in tables["source_observations"])
    expected_observations: Counter[tuple[str, str]] = Counter()
    for record in records.values():
        columns = (
            ["current_value_text2", "target_value_text2"]
            if record["report_type"] == "workplan"
            else ["formatted_current_value2", "formatted_target_value2", "formatted_progress_value2"]
        )
        expected_observations.update((record["source_record_id"], col) for col in columns)
    require(observation_keys == expected_observations, "Missing or duplicate source observations")
    contexts = {c["source_record_id"]: c for c in tables["source_measurement_contexts"]}
    require(
        set(contexts)
        == {k for k, r in records.items() if r["report_type"] == "workplan" and not r["exclusion_reason"]},
        "Measurement context coverage incomplete",
    )
    for context in contexts.values():
        raw = json.loads(records[context["source_record_id"]]["raw_fields_json"])
        require(
            context["unit_raw"] + " / " + context["population_raw"] == raw["unit_population_Text2"],
            "Context source overwritten",
        )
    forbidden = {
        "outcome_class",
        "current_value",
        "performance_change",
        "performance_change_pct",
        "target_met",
        "improvement_pct",
    }
    for row in interventions + current:
        require(not (forbidden & row.keys()), "Outcomes must exist only at historical cycle grain")
        require(row["organization_id"] in orgs and row["indicator_id"] in indicators, "Orphan dimension reference")
        parent = (
            current_map.get(row.get("current_plan_group_id", ""))
            if "current_plan_group_id" in row
            else cycle_map.get(row["cycle_id"])
        )
        require(parent is not None, "Orphan intervention record")
        assert parent is not None
        require(
            all(row[k] == parent[k] for k in ["organization_id", "indicator_id", "plan_fiscal_year"]),
            "Intervention parent mismatch",
        )
        source_ids = json.loads(row["workplan_source_ids"]) + json.loads(row["progress_source_ids"])
        require(bool(source_ids), "Missing source traceability")
        for source_id in source_ids:
            require(source_id in records, "Unknown source reference")
            require(not records[source_id]["exclusion_reason"], "Excluded test record reappeared")
            raw = json.loads(records[source_id]["raw_fields_json"])
            column = "planned3" if records[source_id]["report_type"] == "workplan" else "planned_initiative"
            require(row["change_idea_raw"] == raw[column], "Raw intervention text overwritten")
        if "current_plan_group_id" in row:
            require(
                row["plan_fiscal_year"] == "2026/27" and not json.loads(row["progress_source_ids"]),
                "Current plans receiving progress",
            )
            require("implementation_status" not in row, "Current plans receiving implementation results")
        else:
            require(row["implementation_status"] in allowed_implementation, "Unknown implementation class")
            require(
                all(row[k] == parent[k] for k in ["analysis_eligible", "analysis_exclusion_reason"]),
                "Intervention analysis eligibility mismatch",
            )
            flags = [
                json.loads(records[s]["raw_fields_json"])["methods"] for s in json.loads(row["progress_source_ids"])
            ]
            require(row["implementation_status"] == implementation(flags), "Implementation conflict lost")
    for cycle in cycles:
        require(cycle["plan_fiscal_year"] in {"2024/25", "2025/26"}, "Current plan receiving outcomes")
        require(cycle["organization_id"] in orgs and cycle["indicator_id"] in indicators, "Orphan cycle dimensions")
        require(cycle["outcome_class"] in allowed_outcomes, "Invalid outcome class")
        indicator = indicators[cycle["indicator_id"]]
        require(cycle["direction"] == indicator["direction"], "Cycle direction disagrees with metadata")
        calculated = cycle["outcome_class"] != "Insufficient data"
        target_calculated = cycle["target_met"] != ""
        work_ids = json.loads(cycle["workplan_source_ids"])
        progress_ids = json.loads(cycle["progress_source_ids"])
        require(
            all(s in records and not records[s]["exclusion_reason"] for s in work_ids + progress_ids),
            "Missing or excluded cycle source",
        )
        work_raw = [json.loads(records[s]["raw_fields_json"]) for s in work_ids]
        progress_raw = [json.loads(records[s]["raw_fields_json"]) for s in progress_ids]
        for role, raws in [
            (
                "previous",
                [r["current_value_text2"] for r in work_raw] + [r["formatted_current_value2"] for r in progress_raw],
            ),
            (
                "target",
                [r["target_value_text2"] for r in work_raw] + [r["formatted_target_value2"] for r in progress_raw],
            ),
            ("current", [r["formatted_progress_value2"] for r in progress_raw]),
        ]:
            resolved_value, status, source_values = resolve_value(raws)
            require(
                (cycle[role + "_value"], cycle[role + "_status"], json.loads(cycle[role + "_values_raw"]))
                == (resolved_value, status, source_values),
                "Cycle values do not reconcile to source",
            )
        if calculated or target_calculated:
            require(
                cycle["direction"] in {"lower_is_better", "higher_is_better"}, "Unknown direction used in calculation"
            )
            require(
                cycle["comparable"] == "true" and cycle["match_status"] == "matched" and cycle["cycle_valid"] == "true",
                "Incompatible or ambiguous comparison",
            )
            require(
                cycle["normalized_unit"] != "unknown" and cycle["normalized_population"] != "unknown",
                "Unknown measurement context",
            )
            for field, expected in [
                ("normalized_unit", "expected_units"),
                ("normalized_population", "expected_populations"),
            ]:
                allowed = json.loads(indicator[expected])
                require(not allowed or cycle[field] in allowed, "Incompatible unit/population comparison")
            require(parse_numeric(cycle["current_value"])[1] == "numeric", "Nonnumeric current value used")
            require(
                bool(work_ids) and all(contexts[s]["context_compatible"] == "true" for s in work_ids),
                "Source unit/population incompatible",
            )
        if calculated:
            require(parse_numeric(cycle["previous_value"])[1] == "numeric", "Nonnumeric baseline used")
            require(cycle["performance_change"] != "", "Missing numeric outcome")
            b, c = Decimal(cycle["previous_value"]), Decimal(cycle["current_value"])
            require(Decimal(cycle["performance_change"]) == c - b, "Incorrect absolute change")
            improved = c < b if cycle["direction"] == "lower_is_better" else c > b
            expected_class = "No material change" if b == c else "Improved" if improved else "Worsened"
            require(cycle["outcome_class"] == expected_class, "Incorrect outcome direction")
            if b == 0:
                require(
                    cycle["performance_change_pct"] == cycle["improvement_pct"] == "", "Zero baseline relative change"
                )
            else:
                relative = 100 * (c - b) / abs(b)
                require(Decimal(cycle["performance_change_pct"]) == relative, "Incorrect percentage change")
                sign = -1 if cycle["direction"] == "lower_is_better" else 1
                require(Decimal(cycle["improvement_pct"]) == sign * relative, "Incorrect improvement percentage")
        else:
            require(
                all(cycle[k] == "" for k in ["performance_change", "performance_change_pct", "improvement_pct"]),
                "Ineligible change values",
            )
        if target_calculated:
            require(parse_numeric(cycle["target_value"])[1] == "numeric", "Nonnumeric target used")
            target, actual = Decimal(cycle["target_value"]), Decimal(cycle["current_value"])
            expected_met = actual <= target if cycle["direction"] == "lower_is_better" else actual >= target
            require(cycle["target_met"] == str(expected_met).lower(), "Incorrect target attainment")
        meta = {
            **indicator,
            "expected_units": json.loads(indicator["expected_units"]),
            "expected_populations": json.loads(indicator["expected_populations"]),
        }
        review = None
        if cycle["reporting_period_verified"] == "true":
            review = {k: cycle[k] for k in ["baseline_start", "baseline_end", "followup_start", "followup_end"]}
            review.update(
                periods_comparable="false"
                if "reporting_periods_not_comparable" in json.loads(cycle["comparison_exclusion_reasons"])
                else "true",
                evidence_source_ids=cycle["reporting_period_evidence_source_ids"],
                evidence_note=cycle["reporting_period_evidence"],
            )
        expected_flags = comparison_flags(cycle, meta, review)
        for key, value in expected_flags.items():
            require(cycle[key] == value, f"Incorrect comparison eligibility: {key}")
        expected_outcome = calculate(
            cycle["previous_value"],
            cycle["current_value"],
            cycle["target_value"],
            cycle["direction"],
            cycle["comparison_eligible"] == "true",
        )
        require(all(cycle[k] == v for k, v in expected_outcome.items()), "Unverified or missing calculated outcome")
        ideas = [r for r in interventions if r["cycle_id"] == cycle["cycle_id"]]
        require(int(cycle["intervention_count"]) == len(ideas), "Incorrect intervention denominator")
        require(
            int(cycle["implementation_conflict_count"])
            == sum(i["implementation_status"] == "Partial/conflicting" for i in ideas),
            "Incorrect implementation conflict count",
        )
        refs = json.loads(cycle["workplan_source_ids"]) + json.loads(cycle["progress_source_ids"])
        idea_refs = [
            s for i in ideas for col in ["workplan_source_ids", "progress_source_ids"] for s in json.loads(i[col])
        ]
        require(Counter(refs) == Counter(idea_refs), "Cycle lineage does not reconcile")
    bridge = tables["cycle_categories"]
    pairs = [(b["cycle_id"], b["primary_category"]) for b in bridge]
    require(len(pairs) == len(set(pairs)), "Duplicate cycle/category pair")
    counts = Counter((i["cycle_id"], i["primary_category"]) for i in interventions)
    require(set(pairs) == counts.keys(), "Category coverage does not reconcile")
    for row in bridge:
        parent = cycle_map[row["cycle_id"]]
        require(
            int(row["interventions_in_category"]) == counts[row["cycle_id"], row["primary_category"]],
            "Category count does not reconcile",
        )
        ideas_in_category = sorted(
            i["intervention_id"]
            for i in interventions
            if (i["cycle_id"], i["primary_category"]) == (row["cycle_id"], row["primary_category"])
        )
        require(json.loads(row["intervention_ids"]) == ideas_in_category, "Category lineage mismatch")
        require(row["cycle_outcome"] == parent["outcome_class"], "Bridge outcome mismatch")
        for key in [
            "target_met",
            "organization_id",
            "indicator_id",
            "hospital_model",
            "region",
            "analysis_eligible",
            "comparison_eligible",
            "plan_fiscal_year",
            "ed_scope",
            "analysis_exclusion_reason",
            "category_count_per_cycle",
            "classified_category_count_per_cycle",
            "single_category_cycle",
            "multi_category_cycle",
            "single_classified_category_cycle",
            "has_unclassified_interventions",
        ]:
            require(row[key] == parent[key], f"Bridge parent mismatch: {key}")
    for cycle in cycles:
        categories = {category for cid, category in counts if cid == cycle["cycle_id"]}
        require(int(cycle["category_count_per_cycle"]) == len(categories), "Incorrect category denominator")
        require(
            int(cycle["classified_category_count_per_cycle"]) == len(categories - {"Other"}),
            "Incorrect classified categories",
        )
        for key, expected_flag in [
            ("single_category_cycle", len(categories) == 1),
            ("multi_category_cycle", len(categories) > 1),
            ("has_unclassified_interventions", "Other" in categories),
            ("single_classified_category_cycle", len(categories) == 1 and "Other" not in categories),
        ]:
            require(cycle[key] == str(expected_flag).lower(), "Incorrect category flags")
    lineage = tables["record_lineage"]
    active_ids = {k for k, r in records.items() if not r["exclusion_reason"]}
    require(
        Counter(r["source_record_id"] for r in lineage) == Counter({s: 1 for s in active_ids}),
        "Source reconciliation failed or excluded records reappeared",
    )
    idea_map = {r["intervention_id"]: r for r in interventions + current}
    for link in lineage:
        require(link["entity_id"] in idea_map, "Orphan lineage entity")
        idea = idea_map[link["entity_id"]]
        require(
            link["source_record_id"] in json.loads(idea[link["source_role"] + "_source_ids"]),
            "Lineage reference mismatch",
        )
        require(link["parent_id"] == idea.get("cycle_id", idea.get("current_plan_group_id")), "Lineage parent mismatch")


def load_tables(directory: Path) -> dict[str, list[Row]]:
    # Explicit string loading prevents pandas' default NA/CB interpretation.
    import pandas as pd

    return {
        path.stem: pd.read_csv(path, dtype=str, keep_default_na=False, na_filter=False).to_dict("records")
        for path in directory.glob("*.csv")
    }


def validate_summary(directory: Path, tables: dict[str, list[Row]]) -> None:
    summary = json.loads((directory / "dashboard_summary.json").read_text())
    require(summary == dashboard_summary(tables), "Dashboard summary does not reconcile to eligible cycles")


if __name__ == "__main__":
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / "data" / "processed"
    loaded = load_tables(output)
    validate(loaded)
    validate_summary(output, loaded)
    print("All processed dataset validation checks passed.")
