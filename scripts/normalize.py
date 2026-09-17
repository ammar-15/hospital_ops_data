"""Explicit mappings and strict Decimal parsing; never infer missing values."""

import csv
import hashlib
import json
import re
from decimal import Decimal
from pathlib import Path
from typing import Any

Row = dict[str, Any]


def packed(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def stable_id(prefix: str, *parts: str) -> str:
    return prefix + "_" + hashlib.sha256(packed(parts).encode()).hexdigest()[:20]


def read_csv(path: Path) -> list[Row]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def write_csv(path: Path, rows: list[Row], fields: list[str] | None = None) -> None:
    if fields is None:
        if not rows:
            raise ValueError(f"Explicit schema required for empty table: {path}")
        fields = list(rows[0])
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def mapping(path: Path, key: str) -> dict[str, Row]:
    result = {}
    for row in read_csv(path):
        if row[key] in result:
            raise ValueError(f"Ambiguous mapping in {path}: {row[key]!r}")
        if row.get("mapping_status", "accepted") != "accepted":
            raise ValueError(f"Unresolved mapping in {path}: {row[key]!r}")
        result[row[key]] = row
    return result


def parse_numeric(raw: str) -> tuple[Decimal | None, str]:
    """Only plain signed decimals; retain CB/X/NA and every other token."""
    value = raw.strip()
    if not value:
        return None, "blank"
    if re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", value):
        return Decimal(value), "numeric"
    return None, value


def numeric_key(raw: str) -> str:
    value, status = parse_numeric(raw)
    return f"numeric:{value.normalize()}" if value is not None else f"status:{status}"


def resolve_value(values: list[str]) -> tuple[str, str, list[str]]:
    """Repeated identical facts collapse, conflicting facts never do."""
    raws = sorted(set(values))
    if not raws:
        return "", "missing", raws
    if len({numeric_key(v) for v in raws}) > 1:
        return "", "conflicting", raws
    value, status = parse_numeric(raws[0])
    return str(value) if value is not None else "", status, raws


def implementation(flags: list[str]) -> str:
    values = {flag.strip() for flag in flags}
    if "Y" in values and "N" in values:
        return "Partial/conflicting"
    if values == {"Y"}:
        return "Implemented"
    if values == {"N"}:
        return "Not implemented"
    return "Unknown"
