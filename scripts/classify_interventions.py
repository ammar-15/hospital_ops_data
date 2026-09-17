"""Deterministic classification of documented ideas, not invented projects."""

import json
import re
from pathlib import Path

from scripts.normalize import Row, mapping, packed


class Classifier:
    def __init__(self, config: Path):
        taxonomy = json.loads((config / "intervention_taxonomy.json").read_text())
        self.version = taxonomy["version"]
        self.categories = taxonomy["categories"]
        self.refinements = taxonomy.get("refinement_rules", [])
        self.names = {category["name"] for category in self.categories}
        self.overrides = mapping(config / "classification_overrides.csv", "intervention_id")
        self.used_overrides: set[str] = set()
        for category in self.categories:
            for pattern in category["patterns"]:
                re.compile(pattern)
        for rule in self.refinements:
            re.compile(rule["pattern"])
            if rule["category"] not in self.names:
                raise ValueError("Unknown refinement category")

    def classify(self, identifier: str, idea: str) -> Row:
        scores = []
        evidence = {}
        for priority, category in enumerate(self.categories):
            hits = [p for p in category["patterns"] if re.search(p, idea, re.IGNORECASE)]
            if hits:
                evidence[category["name"]] = hits
                scores.append((-len(hits), priority, category["name"]))
        scores.sort()
        rule_ids = [f"v1:{name}:{pattern}" for name, hits in evidence.items() for pattern in hits]
        if not scores:
            hits = [r for r in self.refinements if re.search(r["pattern"], idea, re.IGNORECASE)]
            for priority, category in enumerate(self.categories):
                matched = [r for r in hits if r["category"] == category["name"]]
                if matched:
                    evidence[category["name"]] = [r["pattern"] for r in matched]
                    scores.append((-len(matched), priority, category["name"]))
            scores.sort()
            rule_ids = [r["rule_id"] for r in hits]
        primary = scores[0][2] if scores else "Other"
        tags = [score[2] for score in scores[1:4]]
        method = "rule" if scores else "fallback"
        reason = ""
        if identifier in self.overrides:
            override = self.overrides[identifier]
            primary = override["primary_category"]
            tags = json.loads(override["secondary_tags"] or "[]")
            reason = override["reason"]
            if primary not in self.names or len(tags) > 3 or not reason.strip():
                raise ValueError(f"Invalid classification override: {identifier}")
            if not all(tag in self.names and tag != primary for tag in tags):
                raise ValueError(f"Invalid secondary tags: {identifier}")
            self.used_overrides.add(identifier)
            method = "override"
        return dict(
            primary_category=primary,
            secondary_tags=packed(tags),
            classification_method=method,
            classification_rule_used=packed(rule_ids) if method != "override" else packed(["manual_override"]),
            classification_confidence="manual_review"
            if method == "override"
            else "rule_supported"
            if scores
            else "unclassified",
            classification_reason=reason
            if method == "override"
            else "Explicit text pattern evidence; not a probability or validated label"
            if scores
            else "No specific operational mechanism matched",
            taxonomy_version=self.version,
            classification_evidence=packed(evidence),
            override_reason=reason,
            classification_review="unreviewed_rules" if method != "override" else "override",
        )
