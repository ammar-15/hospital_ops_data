"""Reproduce the review of the original v1 Other cohort without an external API."""

import json
import re
import sys
from collections import Counter
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.classify_interventions import Classifier
from scripts.normalize import read_csv

ROOT = Path(__file__).resolve().parents[1]


def report() -> str:
    taxonomy = json.loads((ROOT / "config/intervention_taxonomy.json").read_text())
    classifier = Classifier(ROOT / "config")
    ideas = read_csv(ROOT / "data/processed/interventions.csv")
    baseline = [
        i
        for i in ideas
        if not any(re.search(p, i["change_idea_raw"], re.I) for c in taxonomy["categories"] for p in c["patterns"])
    ]
    phrases: Counter[str] = Counter()
    stop = set("the a an to of and in for with on by is as at be will that this our from or through".split())
    for idea in baseline:
        words = re.findall(r"[a-z]+", idea["change_idea_raw"].lower())
        phrases.update(
            {
                " ".join(words[n : n + k])
                for k in [2, 3]
                for n in range(len(words) - k + 1)
                if all(w not in stop for w in words[n : n + k])
            }
        )
    assigned = {i["intervention_id"]: classifier.classify(i["intervention_id"], i["change_idea_raw"]) for i in baseline}
    remaining = sum(i["primary_category"] == "Other" for i in ideas)
    lines = [
        "# Deterministic taxonomy review",
        "",
        "Review date: 2026-09-16. Run `python scripts/review_taxonomy.py` after rebuilding to regenerate this document.",
        "",
        f"Original historical Other: **{len(baseline):,} of {len(ideas):,} ({100 * len(baseline) / len(ideas):.2f}%)**. "
        f"Final historical Other: **{remaining:,} of {len(ideas):,} ({100 * remaining / len(ideas):.2f}%)**. "
        f"{len(baseline) - remaining:,} previously unclassified associations now have explicit rule support.",
        "",
        "The denominator is distinct historical change-idea associations across all hospital indicators and both retained cycles. It is not raw CSV rows or the primary ED outcome cohort. No outcome values, external LLM or API inform classification.",
        "",
        "## Recurring phrases in the original Other cohort",
        "",
        "Counts are associations containing a phrase, at most once per association. Lowercase alphabetic bigrams/trigrams exclude the stop words recorded in the script. Phrases overlap and are descriptive clues, not automatic categories.",
        "",
        "| Phrase | Associations |",
        "| --- | ---: |",
    ]
    lines += [f"| {phrase} | {n} |" for phrase, n in sorted(phrases.items(), key=lambda item: (-item[1], item[0]))[:30]]
    lines += [
        "",
        "## Applied rule refinements",
        "",
        "Version 1.1 preserves all existing version 1 assignments. Refinement rules run only when no original pattern matches. The largest number of matching rules wins; taxonomy order breaks ties. This limits reclassification of previously covered ideas. Manual overrides remain first priority.",
        "",
        "One category is added: **Safety & Risk Prevention**, for explicit preventive mechanisms such as risk assessment, hand hygiene and medication reconciliation. There are 15 primary categories including Other (14 substantive categories). Generic references to workplace violence or patient safety alone do not trigger this category.",
        "",
        "`Hits` counts original Other associations matching a proposed regex; `winning category` counts matching associations whose final primary category is that rule's category. Both columns can overlap across rules and must not be added. Zero-hit rules are retained only as narrow vocabulary coverage. The next table gives additive reassignment totals.",
        "",
        "| Rule ID | Category | Evidence required | Hits | Winning category |",
        "| --- | --- | --- | ---: | ---: |",
    ]
    for rule in taxonomy["refinement_rules"]:
        hits = [i for i in baseline if re.search(rule["pattern"], i["change_idea_raw"], re.I)]
        wins = sum(assigned[i["intervention_id"]]["primary_category"] == rule["category"] for i in hits)
        lines.append(f"| {rule['rule_id']} | {rule['category']} | {rule['reason']} | {len(hits)} | {wins} |")
    lines += ["", "| Final category among original Other | Associations |", "| --- | ---: |"]
    lines += [
        f"| {category} | {n} |"
        for category, n in sorted(Counter(r["primary_category"] for r in assigned.values()).items())
    ]
    lines += [
        "",
        "## Remaining unclassified concepts and deferred proposals",
        "",
        "The export includes clinical care, safety, equity and patient experience beyond ED operations. Topic mentions are not an operational mechanism. The following candidate concepts are counted in the remaining Other cohort but do not trigger new categories:",
        "",
        "| Concept / deferred category | Matching remaining Other | Decision |",
        "| --- | ---: | --- |",
    ]
    for name, pattern, decision in [
        (
            "Patient experience / engagement",
            r"\bpatient (?:experience|engagement|voice)\b",
            "Consider a co-design category only after concrete actions are reviewed; experience alone is an objective.",
        ),
        (
            "Workplace violence / safety",
            r"\bworkplace (?:violence|safety)\b",
            "Retain generic strategies in Other; classify only explicit mechanisms.",
        ),
        (
            "Clinical prevention / care",
            r"\b(?:delirium|pressure injur\w*|falls?|hand hygiene|medication)\b",
            "Do not create a catch-all clinical category from an outcome topic.",
        ),
        (
            "Equity / accessibility",
            r"\b(?:equity|inclusion|accessib\w*|anti.racism)\b",
            "A goal is insufficient to distinguish education, access redesign or policy.",
        ),
        (
            "Generic flow improvements",
            r"\b(?:patient flow|flow optimization|wait times?)\b",
            "Do not infer bed, triage or staffing mechanisms from an aim.",
        ),
    ]:
        count = sum(
            i["primary_category"] == "Other" and bool(re.search(pattern, i["change_idea_raw"], re.I)) for i in ideas
        )
        lines.append(f"| {name} | {count} | {decision} |")
    lines += [
        "",
        "Examples deliberately left unclassified include ‘Flow Optimization’, ‘Engage key stakeholders’, and ‘Same change ideas and methods as Surgical Volumes’. Bare PODS remains ambiguous without expanded discharge wording. Bundles containing several actions remain one source idea.",
        "",
        "## Review and traceability",
        "",
        "`change_idea_raw` is unchanged. Each assignment retains `classification_rule_used`, full regex evidence, `taxonomy_version`, `classification_confidence`, `classification_reason`, and source-record IDs. `rule_supported` is a qualitative evidence label, not a probability or independent human validation. Mixed concepts can still be misclassified; up to three alternative matching categories remain secondary tags. The category bridge uses primary categories only.",
        "",
        "`config/classification_overrides.csv` supports stable intervention ID, category, secondary tags and a mandatory reason. Invalid or unused overrides fail the build. Regex definitions live in `config/intervention_taxonomy.json`. Unchanged v1 rules retain their known keyword/tie-breaking limitations; the pass does not claim a fully adjudicated taxonomy.",
        "",
        "## Cohort-specific Other shares",
        "",
        "| Cohort | Other | Total | Other % |",
        "| --- | ---: | ---: | ---: |",
    ]
    cycles = {c["cycle_id"]: c for c in read_csv(ROOT / "data/processed/performance_cycles.csv")}
    current = read_csv(ROOT / "data/processed/current_workplans.csv")
    for label, cohort in [
        ("All historical", ideas),
        ("Historical defined ED", [i for i in ideas if cycles[i["cycle_id"]]["ed_scope"] == "included"]),
        ("Primary-period ED", [i for i in ideas if cycles[i["cycle_id"]]["primary_analysis_period"] == "true"]),
        ("Current 2026/27, all indicators", current),
        ("All historical + current", ideas + current),
    ]:
        count = sum(i["primary_category"] == "Other" for i in cohort)
        lines.append(f"| {label} | {count} | {len(cohort)} | {100 * count / len(cohort):.2f}% |")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    (ROOT / "docs/taxonomy-review.md").write_text(report())
    print("Wrote docs/taxonomy-review.md")
