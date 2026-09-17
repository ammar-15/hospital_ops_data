"""Build Phase 2 analytical tables. Run from any directory with Python 3.12+."""

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.classify_interventions import Classifier
from scripts.analytical_eligibility import comparison_flags
from scripts.dashboard_analytics import cycle_categories, dashboard_summary
from scripts.normalize import Row, implementation, mapping, packed, resolve_value, stable_id, write_csv
from scripts.outcomes import calculate
from scripts.source_data import read_sources

ROOT = Path(__file__).resolve().parents[1]
PAIRS = {"2024/25": "2025/26", "2025/26": "2026/27"}


def source_ids(rows: list[Row]) -> str:
    return packed(sorted(r["source_record_id"] for r in rows))


def distinct_raw(rows: list[Row], column: str) -> str:
    return packed(sorted({r["raw"].get(column, "") for r in rows}))


def partition(rows: list[Row], key: str) -> dict[str, list[Row]]:
    groups: dict[str, list[Row]] = defaultdict(list)
    for row in rows:
        groups[row[key]].append(row)
    return groups


def make_cycle(
    plan_year: str,
    rows: list[Row],
    metadata: Row,
    units: dict[str, Row],
    populations: dict[str, Row],
    comparison_review: Row | None = None,
) -> Row:
    work = [r for r in rows if r["report_type"] == "workplan"]
    progress = [r for r in rows if r["report_type"] == "progress"]
    org, ind = rows[0]["organization_id"], rows[0]["indicator_id"]
    contexts = set()
    for row in work:
        unit_raw, population_raw = row["raw"]["unit_population_Text2"].split(" / ", 1)
        unit, population = units[unit_raw], populations[population_raw]
        contexts.add(
            (unit["normalized_unit"], population["normalized_population"], unit["comparable"], population["comparable"])
        )
    unit_name = population_name = "unknown"
    compatible = False
    reasons = []
    if len(contexts) == 1:
        unit_name, population_name, unit_ok, population_ok = next(iter(contexts))
        compatible = unit_ok == population_ok == "true"
        if not compatible:
            reasons.append("unknown_unit_or_population")
        if metadata.get("expected_units") and unit_name not in metadata["expected_units"]:
            compatible = False
            reasons.append("incompatible_indicator_unit")
        if metadata.get("expected_populations") and population_name not in metadata["expected_populations"]:
            compatible = False
            reasons.append("incompatible_indicator_population")
    elif contexts:
        reasons.append("conflicting_unit_population")
    else:
        reasons.append("no_workplan_context")
    periods = {r["raw"]["datasource_period_Text2"] for r in work}
    if len(periods) > 1:
        reasons.append("conflicting_baseline_periods")
    previous, previous_status, previous_raw = resolve_value(
        [r["raw"]["current_value_text2"] for r in work] + [r["raw"]["formatted_current_value2"] for r in progress]
    )
    target, target_status, target_raw = resolve_value(
        [r["raw"]["target_value_text2"] for r in work] + [r["raw"]["formatted_target_value2"] for r in progress]
    )
    current, current_status, current_raw = resolve_value([r["raw"]["formatted_progress_value2"] for r in progress])
    for role, status in [("previous", previous_status), ("target", target_status), ("current", current_status)]:
        if status == "conflicting":
            reasons.append(f"conflicting_{role}_values")
    ambiguous = any(reason.startswith("conflicting_") for reason in reasons)
    if work and progress:
        match_status = "ambiguous" if ambiguous else "matched"
    else:
        match_status = "workplan_only" if work else "progress_only"
    if match_status != "matched":
        reasons.append(match_status)
    direction = metadata.get("direction", "unknown")
    if direction == "unknown":
        reasons.append("unknown_indicator_direction")
    comparable = compatible and match_status == "matched"
    outcomes = calculate(previous, current, target, direction, comparable)
    outcome_reasons = list(reasons)
    if previous_status != "numeric":
        outcome_reasons.append("previous_" + previous_status)
    if current_status != "numeric":
        outcome_reasons.append("current_" + current_status)
    target_reasons = list(reasons)
    if target_status != "numeric":
        target_reasons.append("target_" + target_status)
    if current_status != "numeric":
        target_reasons.append("current_" + current_status)
    raw_work_keys = {(r["raw"]["org_name_Text2"], r["raw"]["measure_header_Text2"]) for r in work}
    raw_progress_keys = {(r["raw"]["org_name_Text2"], r["raw"]["measure_header_Text2"]) for r in progress}
    method = ""
    if match_status == "matched":
        method = "exact" if raw_work_keys == raw_progress_keys else "explicit_mapping"
    notes = " ".join(r["raw"]["progress2"] for r in progress)
    partial_hint = bool(re.search(r"\b(?:YTD|FYTD|year.to.date|Q[1-3]|quarter)\b", notes, re.I))
    cycle = dict(
        cycle_id=stable_id("cycle", org, ind, plan_year),
        organization_id=org,
        indicator_id=ind,
        plan_fiscal_year=plan_year,
        progress_report_fiscal_year=PAIRS[plan_year],
        cycle_valid=str(not ambiguous).lower(),
        match_status=match_status,
        match_method=method,
        review_reasons=packed(reasons),
        ed_scope=metadata.get("ed_scope", "needs_review"),
        direction=direction,
        normalized_unit=unit_name,
        normalized_population=population_name,
        comparable=str(comparable).lower(),
        context_provenance="preceding_workplan" if work else "unavailable",
        comparison_basis="Official definition and matching source context; observation windows require cycle-specific review",
        observation_period_status="partial_period_hint" if partial_hint else "unverified",
        baseline_periods_raw=packed(sorted(periods)),
        previous_value=previous,
        previous_status=previous_status,
        previous_values_raw=packed(previous_raw),
        target_value=target,
        target_status=target_status,
        target_values_raw=packed(target_raw),
        current_value=current,
        current_status=current_status,
        current_values_raw=packed(current_raw),
        **outcomes,
        outcome_reason=packed(outcome_reasons),
        target_reason=packed(target_reasons),
        workplan_row_count=len(work),
        progress_row_count=len(progress),
        workplan_source_ids=source_ids(work),
        progress_source_ids=source_ids(progress),
        intervention_count=0,
        workplan_intervention_count=0,
        progress_only_intervention_count=0,
        implementation_status="Unknown",
        implementation_conflict_count=0,
        region_values=distinct_raw(rows, "LHIN_Label_Text2"),
        hospital_model_values=distinct_raw(rows, "OrgCategory_Label_Text2"),
    )
    cycle.update(comparison_flags(cycle, metadata, comparison_review))
    cycle["numeric_change_candidate"] = str(
        comparable and direction != "unknown" and previous_status == current_status == "numeric"
    ).lower()
    cycle.update(calculate(previous, current, target, direction, cycle["comparison_eligible"] == "true"))
    cycle["comparable"] = cycle["comparison_eligible"]
    cycle["outcome_reason"] = packed(outcome_reasons + json.loads(cycle["comparison_exclusion_reasons"]))
    cycle["target_reason"] = packed(target_reasons + json.loads(cycle["comparison_exclusion_reasons"]))
    return cycle


def make_ideas(
    rows: list[Row], parent_id: str, current: bool, classifier: Classifier, cycle_valid: str = "true"
) -> list[Row]:
    result = []
    for idea, idea_rows in sorted(partition(rows, "idea").items()):
        work = [r for r in idea_rows if r["report_type"] == "workplan"]
        progress = [r for r in idea_rows if r["report_type"] == "progress"]
        identifier = stable_id("current" if current else "intervention", parent_id, idea)
        first = idea_rows[0]
        entry = dict(
            intervention_id=identifier,
            **({"current_plan_group_id": parent_id} if current else {"cycle_id": parent_id}),
            organization_id=first["organization_id"],
            indicator_id=first["indicator_id"],
            plan_fiscal_year="2026/27" if current else first["plan_year"],
            change_idea_raw=idea,
            change_idea_normalized=" ".join(idea.split()),
            association_status="workplan_and_progress"
            if work and progress
            else "workplan_only"
            if work
            else "progress_only",
            association_review="needs_review" if cycle_valid == "false" else "source_exact_idea",
            **classifier.classify(identifier, idea),
            workplan_source_ids=source_ids(work),
            progress_source_ids=source_ids(progress),
            planned_methods_raw=distinct_raw(work, "methods2"),
            process_measures_raw=distinct_raw(work, "process_measure3"),
            process_targets_raw=distinct_raw(work, "goal2"),
            workplan_comments_raw=distinct_raw(work, "comments2"),
        )
        if not current:
            flags = [r["raw"]["methods"] for r in progress]
            entry.update(
                implementation_status=implementation(flags),
                implementation_flags_raw=packed(sorted(set(flags))),
                implementation_notes_raw=distinct_raw(progress, "process_measure"),
                progress_comments_raw=distinct_raw(progress, "progress2"),
                outcome_reference="cycle_id; shared outcome, not independent intervention evidence",
            )
        result.append(entry)
    return result


def quality_summary(cycles: list[Row], interventions: list[Row], current: list[Row], records: list[Row]) -> list[Row]:
    summary = []
    for scope in ["all_hospitals", "ed_access_flow"]:
        for year in [*PAIRS, "all_historical"]:
            cohort = [
                c
                for c in cycles
                if (year == "all_historical" or c["plan_fiscal_year"] == year)
                and (scope == "all_hospitals" or c["ed_scope"] == "included")
            ]
            ids = {c["cycle_id"] for c in cohort}
            ideas = [i for i in interventions if i["cycle_id"] in ids]
            work = [c for c in cohort if c["workplan_row_count"]]
            progress = [c for c in cohort if c["progress_row_count"]]
            matched = [c for c in cohort if c["match_status"] == "matched"]
            eligible = [c for c in cohort if c["analysis_eligible"] == c["comparison_eligible"] == "true"]
            outcome_metrics = {
                "outcome_calculable_cycles": sum(c["outcome_class"] != "Insufficient data" for c in eligible),
                "cycles_with_insufficient_data": sum(c["outcome_class"] == "Insufficient data" for c in eligible),
                "target_calculable_cycles": sum(c["target_met"] != "" for c in eligible),
            }
            metrics = {
                "workplan_rows": sum(c["workplan_row_count"] for c in cohort),
                "progress_rows": sum(c["progress_row_count"] for c in cohort),
                "total_cycles": len(cohort),
                "valid_cycles": sum(c["cycle_valid"] == "true" for c in cohort),
                "workplan_cycles": len(work),
                "progress_cycles": len(progress),
                "matched_cycles": len(matched),
                "candidate_matched_cycles": sum(
                    bool(c["workplan_row_count"] and c["progress_row_count"]) for c in cohort
                ),
                "unmatched_cycles": sum(c["match_status"] in {"workplan_only", "progress_only"} for c in cohort),
                "workplan_only_cycles": sum(c["match_status"] == "workplan_only" for c in cohort),
                "progress_only_cycles": sum(c["match_status"] == "progress_only" for c in cohort),
                "ambiguous_matches": sum(c["match_status"] == "ambiguous" for c in cohort),
                "cycles_needing_identity_review": sum(c["cycle_valid"] == "false" for c in cohort),
                "exact_matches": sum(c["match_method"] == "exact" for c in cohort),
                "normalized_matches": sum(c["match_method"] == "explicit_mapping" for c in cohort),
                "fuzzy_matches": 0,
                **outcome_metrics,
                "analysis_eligible_cycles": len(eligible),
                "cycles_containing_multiple_interventions": sum(c["intervention_count"] > 1 for c in cohort),
                "cycles_with_implementation_conflicts": sum(c["implementation_conflict_count"] > 0 for c in cohort),
                "cycles_with_mixed_implementation": sum(
                    c["implementation_status"] == "Partial/conflicting" for c in cohort
                ),
                "interventions": len(ideas),
                "interventions_classified_other": sum(i["primary_category"] == "Other" for i in ideas),
                "interventions_with_implementation_conflicts": sum(
                    i["implementation_status"] == "Partial/conflicting" for i in ideas
                ),
                "workplan_rows_in_matched_cycles": sum(c["workplan_row_count"] for c in matched),
                "progress_rows_in_matched_cycles": sum(c["progress_row_count"] for c in matched),
                "exact_idea_matched_workplan_rows": sum(
                    len(json.loads(i["workplan_source_ids"]))
                    for i in ideas
                    if i["association_status"] == "workplan_and_progress"
                ),
            }
            for name, value in metrics.items():
                summary.append(
                    dict(
                        scope=scope,
                        plan_fiscal_year=year,
                        metric=name,
                        value=value,
                        numerator=value if name in outcome_metrics else "",
                        denominator=len(eligible) if name in outcome_metrics else "",
                        sample_size=len(eligible) if name in outcome_metrics else "",
                        definition="Primary ED analysis-eligible cycles only"
                        if name in outcome_metrics
                        else "Included source records; test exclusions applied; coverage diagnostic",
                    )
                )
            for name, numerator, denominator in [
                ("workplan_cycle_match_rate_pct", len(matched), len(work)),
                ("progress_cycle_match_rate_pct", len(matched), len(progress)),
                (
                    "workplan_row_cycle_match_rate_pct",
                    metrics["workplan_rows_in_matched_cycles"],
                    metrics["workplan_rows"],
                ),
                (
                    "exact_idea_workplan_row_coverage_pct",
                    metrics["exact_idea_matched_workplan_rows"],
                    metrics["workplan_rows"],
                ),
                ("other_pct", metrics["interventions_classified_other"], len(ideas)),
            ]:
                summary.append(
                    dict(
                        scope=scope,
                        plan_fiscal_year=year,
                        metric=name,
                        value=100 * numerator / denominator if denominator else "",
                        numerator=numerator,
                        denominator=denominator,
                        sample_size=denominator,
                        definition="Accepted matches exclude ambiguity; exact idea coverage is a candidate diagnostic",
                    )
                )
    for filename, rows in sorted(partition(records, "source_file").items()):
        for metric, value in [
            ("raw_rows", len(rows)),
            ("excluded_rows", sum(bool(r["exclusion_reason"]) for r in rows)),
            ("exact_duplicate_excess", sum(bool(r["duplicate_of"]) for r in rows)),
        ]:
            summary.append(
                dict(
                    scope=filename,
                    plan_fiscal_year="",
                    metric=metric,
                    value=value,
                    numerator="",
                    denominator="",
                    sample_size="",
                    definition="Before analytical deduplication",
                )
            )
    for metric, value in [
        ("current_ideas", len(current)),
        ("current_ideas_other", sum(c["primary_category"] == "Other" for c in current)),
    ]:
        summary.append(
            dict(
                scope="all_hospitals",
                plan_fiscal_year="2026/27",
                metric=metric,
                value=value,
                numerator="",
                denominator="",
                sample_size="",
                definition="Current plans; no observed outcomes",
            )
        )
    return summary


def build(root: Path = ROOT, output: Path | None = None) -> dict[str, list[Row]]:
    output = output or root / "data" / "processed"
    output.mkdir(parents=True, exist_ok=True)
    config = root / "config"
    files, records, observations = read_sources(root)
    units = mapping(config / "unit_mappings.csv", "source_unit")
    populations = mapping(config / "population_mappings.csv", "source_population")
    org_map = mapping(config / "organization_mappings.csv", "source_name")
    ind_map = mapping(config / "indicator_mappings.csv", "source_name")
    meta_config = json.loads((config / "indicator_metadata.json").read_text())
    metadata = meta_config["indicators"]
    comparison_reviews = mapping(config / "comparison_reviews.csv", "cycle_id")
    if not set(metadata) <= ind_map.keys():
        raise ValueError("Metadata contains unknown source indicators")
    classifier = Classifier(config)
    active = []
    measurement_contexts = []
    groups: dict[tuple[str, str, str], list[Row]] = defaultdict(list)
    for record in records:
        if record["exclusion_reason"]:
            continue
        row = {**record, "raw": json.loads(record["raw_fields_json"])}
        if row["raw"]["sector_name_Text2"] != "Acute Care/Hospital":
            raise ValueError("Unexpected nonhospital sector; review scope")
        row["idea"] = row["raw"]["planned3" if row["report_type"] == "workplan" else "planned_initiative"]
        year = row["report_fiscal_year"]
        row["plan_year"] = year if row["report_type"] == "workplan" else {v: k for k, v in PAIRS.items()}[year]
        if row["report_type"] == "workplan":
            raw_unit, raw_population = row["raw"]["unit_population_Text2"].split(" / ", 1)
            unit, population = units[raw_unit], populations[raw_population]
            meta = metadata.get(row["raw"]["measure_header_Text2"], {})
            reasons = []
            if unit["comparable"] != "true" or population["comparable"] != "true":
                reasons.append("unknown_unit_or_population")
            if meta.get("expected_units") and unit["normalized_unit"] not in meta["expected_units"]:
                reasons.append("incompatible_indicator_unit")
            if (
                meta.get("expected_populations")
                and population["normalized_population"] not in meta["expected_populations"]
            ):
                reasons.append("incompatible_indicator_population")
            measurement_contexts.append(
                dict(
                    source_record_id=row["source_record_id"],
                    unit_raw=raw_unit,
                    population_raw=raw_population,
                    normalized_unit=unit["normalized_unit"],
                    normalized_population=population["normalized_population"],
                    context_compatible=str(not reasons).lower(),
                    review_reasons=packed(reasons),
                    datasource_period_raw=row["raw"]["datasource_period_Text2"],
                )
            )
        groups[(row["organization_id"], row["indicator_id"], row["plan_year"])].append(row)
        active.append(row)
    # Identity-preserving registries may not silently merge multiple source labels.
    for registry, identity in [(org_map, "organization_id"), (ind_map, "indicator_id")]:
        labels: dict[str, list[str]] = defaultdict(list)
        for raw, alias in registry.items():
            labels[alias[identity]].append(raw)
        for aliases in labels.values():
            if len(aliases) > 1:
                raise ValueError(f"Multiple aliases require explicit contextual review before merge: {aliases}")
    cycles, interventions, current, current_groups, lineage, issues = [], [], [], [], [], []
    for context in measurement_contexts:
        for reason in json.loads(context["review_reasons"]):
            issues.append(
                dict(
                    entity_type="source_measurement_context",
                    entity_id=context["source_record_id"],
                    issue_code=reason,
                    source_record_ids=packed([context["source_record_id"]]),
                )
            )
    for (org, ind, year), rows in sorted(groups.items()):
        raw_indicator = rows[0]["raw"]["measure_header_Text2"]
        meta = metadata.get(raw_indicator, {})
        is_current = year == "2026/27"
        if is_current:
            parent_id = stable_id("current_group", org, ind, year)
            ideas = make_ideas(rows, parent_id, True, classifier)
            current.extend(ideas)
            current_groups.append(
                dict(
                    current_plan_group_id=parent_id,
                    organization_id=org,
                    indicator_id=ind,
                    plan_fiscal_year=year,
                    ed_scope=meta.get("ed_scope", "needs_review"),
                    source_record_ids=source_ids(rows),
                    intervention_count=len(ideas),
                )
            )
        else:
            cycle = make_cycle(
                year, rows, meta, units, populations, comparison_reviews.get(stable_id("cycle", org, ind, year))
            )
            parent_id = cycle["cycle_id"]
            ideas = make_ideas(rows, parent_id, False, classifier, cycle["cycle_valid"])
            for idea in ideas:
                idea.update(
                    analysis_eligible=cycle["analysis_eligible"],
                    analysis_exclusion_reason=cycle["analysis_exclusion_reason"],
                )
            cycle["intervention_count"] = len(ideas)
            cycle["workplan_intervention_count"] = sum(i["association_status"] != "progress_only" for i in ideas)
            cycle["progress_only_intervention_count"] = sum(i["association_status"] == "progress_only" for i in ideas)
            cycle["implementation_status"] = implementation(
                [r["raw"]["methods"] for r in rows if r["report_type"] == "progress"]
            )
            cycle["implementation_conflict_count"] = sum(
                i["implementation_status"] == "Partial/conflicting" for i in ideas
            )
            cycles.append(cycle)
            interventions.extend(ideas)
            for reason in json.loads(cycle["review_reasons"]):
                issues.append(
                    dict(
                        entity_type="performance_cycle",
                        entity_id=parent_id,
                        issue_code=reason,
                        source_record_ids=source_ids(rows),
                    )
                )
        for idea in ideas:
            for role in ["workplan", "progress"]:
                for record_id in json.loads(idea[f"{role}_source_ids"]):
                    lineage.append(
                        dict(
                            source_record_id=record_id,
                            entity_type="current_workplan" if is_current else "intervention",
                            entity_id=idea["intervention_id"],
                            parent_id=parent_id,
                            source_role=role,
                        )
                    )
    if classifier.used_overrides != classifier.overrides.keys():
        raise ValueError("Unused classification overrides; review their IDs")
    if not comparison_reviews.keys() <= {c["cycle_id"] for c in cycles}:
        raise ValueError("Unused comparison review IDs")
    organizations = []
    for org, rows in sorted(partition(active, "organization_id").items()):
        raw = rows[0]["raw"]["org_name_Text2"]
        models = {r["raw"]["OrgCategory_Label_Text2"] for r in rows} - {"", "No type available"}
        regions = {r["raw"]["LHIN_Label_Text2"] for r in rows}
        organizations.append(
            dict(
                organization_id=org,
                normalized_organization_name=org_map[raw]["normalized_name"],
                source_names=distinct_raw(rows, "org_name_Text2"),
                entity_kind="reporting_organization",
                hospital_model=next(iter(models)) if len(models) == 1 else "",
                hospital_model_values=distinct_raw(rows, "OrgCategory_Label_Text2"),
                region=next(iter(regions)) if len(regions) == 1 else "",
                region_values=packed(sorted(regions)),
                source_record_ids=source_ids(rows),
            )
        )
    indicators = []
    for ind, rows in sorted(partition(active, "indicator_id").items()):
        raw = rows[0]["raw"]["measure_header_Text2"]
        meta = metadata.get(raw, {})
        indicators.append(
            dict(
                indicator_id=ind,
                normalized_indicator_name=ind_map[raw]["normalized_name"],
                display_name=meta.get("display_name", ind_map[raw]["normalized_name"]),
                unit=meta.get("unit", "unknown"),
                comparable_population=meta.get("comparable_population", "unknown"),
                definition_verified=str(meta.get("definition_verified", False)).lower(),
                indicator_outcome_eligible=str(meta.get("indicator_outcome_eligible", False)).lower(),
                definition_sources=packed(meta.get("definition_sources", [])),
                reporting_period_information=packed(meta.get("reporting_period_information", {})),
                source_names=distinct_raw(rows, "measure_header_Text2"),
                direction=meta.get("direction", "unknown"),
                direction_basis=meta.get("basis", "Unreviewed direction; no calculations permitted"),
                ed_scope=meta.get("ed_scope", "needs_review"),
                expected_units=packed(meta.get("expected_units", [])),
                expected_populations=packed(meta.get("expected_populations", [])),
                reported_domains=distinct_raw(rows, "objective_header_Text2"),
                indicator_type="unknown",
                metadata_version=meta_config["version"],
                source_record_ids=source_ids(rows),
            )
        )
    bridge = cycle_categories(cycles, interventions)
    tables = dict(
        cycle_categories=bridge,
        performance_cycles=cycles,
        interventions=interventions,
        organizations=organizations,
        indicators=indicators,
        current_workplans=current,
        current_plan_groups=current_groups,
        source_files=files,
        source_records=records,
        source_observations=observations,
        source_measurement_contexts=measurement_contexts,
        record_lineage=lineage,
        data_quality_issues=issues,
        data_quality_summary=quality_summary(cycles, interventions, current, records),
    )
    # Validate in memory before replacing analytical outputs.
    from scripts.validate_data import validate

    validate(tables)
    summary = dashboard_summary(tables)
    for name, table in tables.items():
        write_csv(output / f"{name}.csv", table)
    (output / "dashboard_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    fingerprints = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(config.iterdir()) if p.is_file()}
    code_fingerprints = {
        p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((root / "scripts").glob("*.py"))
    }
    (output / "build_manifest.json").write_text(
        json.dumps(
            dict(
                pipeline_version="2.0",
                config_sha256=fingerprints,
                code_sha256=code_fingerprints,
                row_counts={k: len(v) for k, v in tables.items()},
            ),
            indent=2,
        )
        + "\n"
    )
    return tables


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Alternative output directory for reproducibility checks")
    args = parser.parse_args()
    tables = build(output=args.output)
    for name, rows in tables.items():
        print(f"{name}: {len(rows):,} rows")


if __name__ == "__main__":
    main()
