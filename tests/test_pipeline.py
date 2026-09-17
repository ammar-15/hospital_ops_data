"""Real-snapshot regressions and failure tests for analytical safety boundaries."""

import copy
import csv
import hashlib
import json
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from scripts.build_dataset import ROOT, build, make_cycle
from scripts.classify_interventions import Classifier
from scripts.normalize import Row, implementation, mapping, parse_numeric
from scripts.outcomes import calculate
from scripts.validate_data import validate
from scripts.analytical_eligibility import FIRST_CYCLE_REASON, comparison_flags
from scripts.dashboard_analytics import cycle_categories, dashboard_summary, outcome_summary
from scripts.validate_data import validate_summary


class CalculationTests(unittest.TestCase):
    def test_missing_tokens_are_not_zero(self):
        for token in ["CB", "X", "NA", "N/A", "", " ", "suppressed", "1,20", "NaN", "inf", "10%"]:
            with self.subTest(token=token):
                self.assertIsNone(parse_numeric(token)[0])
        self.assertEqual(parse_numeric("0"), (Decimal(0), "numeric"))
        self.assertEqual(parse_numeric(" 1.00 "), (Decimal(1), "numeric"))
        self.assertEqual(parse_numeric("NA")[1], "NA")

    def test_direction_and_target_are_separate(self):
        result = calculate("20", "15", "10", "lower_is_better", True)
        self.assertEqual(result["outcome_class"], "Improved")
        self.assertEqual(result["target_met"], "false")
        self.assertEqual(Decimal(result["performance_change"]), -5)
        self.assertEqual(Decimal(result["improvement_pct"]), 25)
        self.assertEqual(Decimal(result["performance_change_pct"]), -25)
        self.assertEqual(calculate("20", "15", "10", "higher_is_better", True)["outcome_class"], "Worsened")

    def test_exact_equality_only_no_material_tolerance(self):
        self.assertEqual(calculate("1.00", "1", "", "lower_is_better", True)["outcome_class"], "No material change")
        self.assertEqual(calculate("1", "1.00000001", "", "lower_is_better", True)["outcome_class"], "Worsened")

    def test_zero_baseline_and_missing_baseline(self):
        result = calculate("0", "1", "2", "higher_is_better", True)
        self.assertEqual(result["outcome_class"], "Improved")
        self.assertEqual(result["performance_change_pct"], "")
        result = calculate("", "1", "2", "lower_is_better", True)
        self.assertEqual(result["target_met"], "true")
        self.assertEqual(result["outcome_class"], "Insufficient data")

    def test_unknown_and_incompatible_block_both_calculations(self):
        for direction, compatible in [("unknown", True), ("lower_is_better", False)]:
            result = calculate("20", "15", "10", direction, compatible)
            self.assertEqual(result["outcome_class"], "Insufficient data")
            self.assertEqual(result["target_met"], "")

    def test_implementation_conflicts_and_unknown(self):
        for flags, expected in [
            (["Y", "N", "Y"], "Partial/conflicting"),
            (["Y", "Y"], "Implemented"),
            (["N"], "Not implemented"),
            ([], "Unknown"),
            (["Y", ""], "Unknown"),
        ]:
            self.assertEqual(implementation(flags), expected)

    def test_mapping_collisions_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "map.csv"
            path.write_text("source_name,organization_id\na,one\na,two\n")
            with self.assertRaisesRegex(ValueError, "Ambiguous mapping"):
                mapping(path, "source_name")

    def test_classification_rules_and_fallback(self):
        classifier = Classifier(ROOT / "config")
        self.assertEqual(
            classifier.classify("test", "Daily multidisciplinary huddles")["primary_category"],
            "Care Coordination & Communication",
        )
        self.assertEqual(classifier.classify("test", "Unspecified activity")["primary_category"], "Other")

    def test_incompatible_context_is_not_inherited(self):
        work: Row = dict(
            source_record_id="w",
            organization_id="org",
            indicator_id="ind",
            report_type="workplan",
            raw=dict(
                org_name_Text2="Hospital",
                measure_header_Text2="Wait time",
                unit_population_Text2="Hours / ED patients",
                datasource_period_Text2="Local / Other",
                current_value_text2="20",
                target_value_text2="10",
            ),
        )
        progress = dict(
            source_record_id="p",
            organization_id="org",
            indicator_id="ind",
            report_type="progress",
            raw=dict(
                org_name_Text2="Hospital",
                measure_header_Text2="Wait time",
                progress2="",
                formatted_current_value2="20.00",
                formatted_target_value2="10.00",
                formatted_progress_value2="15",
            ),
        )
        units = mapping(ROOT / "config/unit_mappings.csv", "source_unit")
        pops = mapping(ROOT / "config/population_mappings.csv", "source_population")
        for expected_unit, expected_population in [("minutes", "ed patients"), ("hours", "all inpatients")]:
            meta = dict(
                direction="lower_is_better", expected_units=[expected_unit], expected_populations=[expected_population]
            )
            result = make_cycle("2024/25", [work, progress], meta, units, pops)
            self.assertEqual(result["outcome_class"], "Insufficient data")
            self.assertEqual(result["target_met"], "")
        alternate = copy.deepcopy(work)
        alternate["raw"]["unit_population_Text2"] = "Minutes / ED patients"
        result = make_cycle("2024/25", [work, alternate, progress], {}, units, pops)
        self.assertEqual(result["cycle_valid"], "false")
        self.assertEqual(result["match_status"], "ambiguous")


class DatasetTests(unittest.TestCase):
    directory: tempfile.TemporaryDirectory[str]
    tables: dict[str, list[Row]]

    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.tables = build(output=Path(cls.directory.name))

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def test_valid_dataset(self):
        validate(self.tables)
        validate_summary(Path(self.directory.name), self.tables)

    def test_primary_window_and_verification(self):
        cycles = self.tables["performance_cycles"]
        first = [c for c in cycles if c["ed_scope"] == "included" and c["plan_fiscal_year"] == "2024/25"]
        self.assertEqual(len(first), 66)
        self.assertTrue(
            all(
                c["analysis_eligible"] == "false" and c["analysis_exclusion_reason"] == FIRST_CYCLE_REASON
                for c in first
            )
        )
        primary = [c for c in cycles if c["primary_analysis_period"] == "true"]
        self.assertEqual(len(primary), 206)
        self.assertEqual(sum(c["numeric_change_candidate"] == "true" for c in primary), 129)
        summary = dashboard_summary(self.tables)
        self.assertEqual(summary["analyzable_ed_cycles"]["numerator"], 0)
        self.assertIsNone(summary["overall"]["improved_count"]["percentage"])
        self.assertEqual(summary["fully_verified_ed_indicator_definitions"], 8)
        # Numeric availability alone must not grant a comparison.
        self.assertTrue(all(c["comparison_eligible"] == "false" for c in primary))

    def test_bridge_pairs_unique_and_complete(self):
        bridge = self.tables["cycle_categories"]
        pairs = [(b["cycle_id"], b["primary_category"]) for b in bridge]
        expected = {(i["cycle_id"], i["primary_category"]) for i in self.tables["interventions"]}
        self.assertEqual(len(pairs), len(set(pairs)))
        self.assertEqual(set(pairs), expected)
        self.rejects(lambda t: t["cycle_categories"].append(t["cycle_categories"][0]), "Duplicate cycle/category")

    def test_all_summary_sample_sizes_and_category_totals(self):
        summary = dashboard_summary(self.tables)

        def check(value):
            if isinstance(value, dict):
                if "numerator" in value:
                    self.assertEqual(value["sample_size"], value["denominator"])
                    self.assertLessEqual(value["numerator"], value["denominator"])
                    expected = 100 * value["numerator"] / value["denominator"] if value["denominator"] else None
                    self.assertEqual(value["percentage"], expected)
                for child in value.values():
                    check(child)

        check(summary)
        ids = {c["cycle_id"] for c in self.tables["performance_cycles"] if c["primary_analysis_period"] == "true"}
        expected_ideas = [i for i in self.tables["interventions"] if i["cycle_id"] in ids]
        self.assertEqual(sum(m["numerator"] for m in summary["category_counts"].values()), len(expected_ideas))
        for category, metric in summary["category_counts"].items():
            self.assertEqual(metric["numerator"], sum(i["primary_category"] == category for i in expected_ideas))

    def test_classification_reproducible_and_raw_text_preserved(self):
        classifier = Classifier(ROOT / "config")
        for idea in self.tables["interventions"] + self.tables["current_workplans"]:
            result = classifier.classify(idea["intervention_id"], idea["change_idea_raw"])
            for key, value in result.items():
                self.assertEqual(idea[key], value)
        self.rejects(lambda t: t["interventions"][0].update(change_idea_raw="invented"), "Raw intervention text")

    def rejects(self, mutate, message):
        tables = copy.deepcopy(self.tables)
        mutate(tables)
        with self.assertRaisesRegex(ValueError, message):
            validate(tables)

    def test_duplicate_cycle_ids(self):
        self.rejects(lambda t: t["performance_cycles"].append(t["performance_cycles"][0]), "Duplicate cycle IDs")

    def test_orphan_intervention(self):
        self.rejects(lambda t: t["interventions"][0].update(cycle_id="missing"), "Orphan intervention")

    def test_unknown_direction_outcome(self):
        def mutate(tables):
            row = next(c for c in tables["performance_cycles"] if c["direction"] == "unknown")
            row["outcome_class"] = "Improved"

        self.rejects(mutate, "Unknown direction")

    def test_numeric_coercion_error(self):
        def mutate(tables):
            row = next(r for r in tables["source_observations"] if r["source_status"] == "CB")
            row["numeric_value"] = "0"

        self.rejects(mutate, "Numeric coercion")

    def test_current_plans_cannot_receive_outcomes(self):
        self.rejects(lambda t: t["current_workplans"][0].update(outcome_class="Improved"), "Outcomes must exist only")

    def test_incompatible_unit_population(self):
        for field in ["normalized_unit", "normalized_population"]:

            def mutate(tables):
                row = next(c for c in tables["performance_cycles"] if c["unit_verified"] == "true")
                row[field] = "incompatible"

            with self.subTest(field=field):
                self.rejects(mutate, "Incorrect comparison eligibility")

    def test_source_traceability_required(self):
        self.rejects(lambda t: t["interventions"][0].update(workplan_source_ids='["missing"]'), "Unknown source")

    def test_exclusions_cannot_reappear(self):
        def mutate(tables):
            source_id = next(r["source_record_id"] for r in tables["source_records"] if r["exclusion_reason"])
            tables["interventions"][0]["workplan_source_ids"] = json.dumps([source_id])

        self.rejects(mutate, "Excluded test record")
        self.assertEqual(sum(bool(r["exclusion_reason"]) for r in self.tables["source_records"]), 5)

    def test_profile_regressions_and_shared_outcome_grain(self):
        metrics = {
            (r["scope"], r["plan_fiscal_year"], r["metric"]): r["value"] for r in self.tables["data_quality_summary"]
        }
        for year, rows, ideas, candidate_cycles, ed_rows in [
            ("2024/25", 1688, 1049, 478, 9),
            ("2025/26", 1742, 1194, 573, 218),
        ]:
            self.assertEqual(metrics["all_hospitals", year, "workplan_rows"], rows)
            self.assertEqual(metrics["all_hospitals", year, "exact_idea_matched_workplan_rows"], ideas)
            self.assertEqual(metrics["all_hospitals", year, "candidate_matched_cycles"], candidate_cycles)
            self.assertEqual(metrics["ed_access_flow", year, "exact_idea_matched_workplan_rows"], ed_rows)
        self.assertEqual(len(self.tables["performance_cycles"]), 1669)
        self.assertEqual(
            sum(i["implementation_status"] == "Partial/conflicting" for i in self.tables["interventions"]), 7
        )
        self.assertTrue(any(c["intervention_count"] >= 9 for c in self.tables["performance_cycles"]))
        self.assertTrue(all("outcome_class" not in i for i in self.tables["interventions"]))

    def test_lossless_all_source_fields(self):
        files = {r["source_file_id"]: r for r in self.tables["source_files"]}
        by_name: dict[str, dict[int, Row]] = {}
        for record in self.tables["source_records"]:
            by_name.setdefault(record["source_file"], {})[record["source_record_number"]] = record
        for filename, records in by_name.items():
            with (ROOT / "data" / filename).open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.reader(stream, strict=True)
                headers = next(reader)
                last_line = reader.line_num
                for number, values in enumerate(reader, 2):
                    start = last_line + 1
                    last_line = reader.line_num
                    if not values:
                        continue
                    record = records[number]
                    reconstructed = {
                        **json.loads(files[record["source_file_id"]]["constant_fields_json"]),
                        **json.loads(record["raw_fields_json"]),
                    }
                    self.assertEqual([reconstructed[h] for h in headers], values)
                    self.assertEqual(record["physical_line_start"], start)
                    self.assertEqual(record["physical_line_end"], last_line)

    def test_reproducible_outputs(self):
        # A second complete build must be byte-identical, including metadata.
        with tempfile.TemporaryDirectory() as other:
            build(output=Path(other))
            for path in Path(self.directory.name).iterdir():
                with self.subTest(file=path.name):
                    self.assertEqual(
                        hashlib.sha256(path.read_bytes()).digest(),
                        hashlib.sha256((Path(other) / path.name).read_bytes()).digest(),
                    )


class AnalyticalBoundaryTests(unittest.TestCase):
    def cycle(self, identifier, outcome="Improved"):
        return dict(
            cycle_id=identifier,
            organization_id="org",
            indicator_id="ind",
            plan_fiscal_year="2025/26",
            ed_scope="included",
            analysis_eligible="true",
            comparison_eligible="true",
            analysis_exclusion_reason="",
            outcome_class=outcome,
            target_met="true",
            hospital_model_values='["Small Hospital"]',
            region_values='["East Region"]',
        )

    def test_multiple_interventions_and_categories_do_not_multiply_cycles(self):
        cycles = [self.cycle("a"), self.cycle("b", "Worsened")]
        ideas = [
            dict(cycle_id=cid, intervention_id=str(n), primary_category=cat)
            for n, (cid, cat) in enumerate([("a", "A"), ("a", "A"), ("a", "B"), ("b", "A")])
        ]
        bridge = cycle_categories(cycles, ideas)
        self.assertEqual(len(bridge), 3)
        self.assertEqual(
            next(r for r in bridge if r["cycle_id"] == "a" and r["primary_category"] == "A")[
                "interventions_in_category"
            ],
            2,
        )
        joined = [next(c for c in cycles if c["cycle_id"] == i["cycle_id"]) for i in ideas]
        summary = outcome_summary(joined)
        self.assertEqual(summary["improved_count"]["numerator"], 1)
        self.assertEqual(summary["improved_count"]["denominator"], 2)
        self.assertEqual(summary["worsened_count"]["numerator"], 1)
        self.assertEqual(summary["target_met_count"]["sample_size"], 2)
        for category, denominator in [("A", 2), ("B", 1)]:
            cohort = [
                next(c for c in cycles if c["cycle_id"] == b["cycle_id"])
                for b in bridge
                if b["primary_category"] == category
            ]
            self.assertEqual(outcome_summary(cohort)["improved_count"]["denominator"], denominator)
        self.assertEqual(cycles[0]["multi_category_cycle"], "true")
        self.assertEqual(cycles[1]["single_classified_category_cycle"], "true")

    def test_excluded_and_current_cycles_cannot_leak_into_summaries(self):
        good = self.cycle("good")
        first = {**self.cycle("first"), "plan_fiscal_year": "2024/25", "analysis_eligible": "false"}
        current = {**self.cycle("current"), "plan_fiscal_year": "2026/27"}
        unverified = {**self.cycle("unverified"), "comparison_eligible": "false"}
        summary = outcome_summary([good, first, current, unverified])
        self.assertEqual(summary["outcome_cycle_ids"], ["good"])
        self.assertEqual(summary["improved_count"]["denominator"], 1)

    def test_reviewed_windows_require_evidence_and_comparable_duration(self):
        cycle = {
            **self.cycle("a"),
            "normalized_unit": "hours",
            "normalized_population": "ed patients",
            "match_status": "matched",
            "cycle_valid": "true",
            "direction": "lower_is_better",
            "workplan_source_ids": '["w"]',
            "progress_source_ids": '["p"]',
        }
        meta = dict(
            definition_verified=True,
            indicator_outcome_eligible=True,
            expected_units=["hours"],
            expected_populations=["ed patients"],
        )
        review = dict(
            baseline_start="2023-12-01",
            baseline_end="2024-11-30",
            followup_start="2024-12-01",
            followup_end="2025-11-30",
            periods_comparable="true",
            evidence_source_ids='["w","p"]',
            evidence_note="Synthetic test evidence, not an approved real-data review",
        )
        self.assertEqual(comparison_flags(cycle, meta)["comparison_eligible"], "false")
        self.assertEqual(comparison_flags(cycle, meta, review)["comparison_eligible"], "true")
        self.assertEqual(
            comparison_flags({**cycle, "direction": "unknown"}, meta, review)["comparison_eligible"], "false"
        )
        self.assertEqual(
            comparison_flags({**cycle, "normalized_unit": "minutes"}, meta, review)["comparison_eligible"], "false"
        )
        for changes in [
            dict(evidence_source_ids='["foreign"]'),
            dict(followup_start="2025-04-01"),
            dict(followup_start="2024-01-01"),
        ]:
            with self.assertRaises(ValueError):
                comparison_flags(cycle, meta, {**review, **changes})


if __name__ == "__main__":
    unittest.main()
