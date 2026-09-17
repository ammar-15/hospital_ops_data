"""Strict source inventory with lossless metadata factoring and lineage."""

import csv
import hashlib
import json
from pathlib import Path

from scripts.normalize import Row, mapping, packed, parse_numeric, read_csv, stable_id


def read_sources(root: Path) -> tuple[list[Row], list[Row], list[Row]]:
    config = root / "config"
    manifest = json.loads((config / "sources.json").read_text())
    organizations = mapping(config / "organization_mappings.csv", "source_name")
    indicators = mapping(config / "indicator_mappings.csv", "source_name")
    exclusion_rows = read_csv(config / "exclusions.csv")
    exclusions = {(e["source_file"], int(e["source_record_number"])): e for e in exclusion_rows}
    if len(exclusions) != len(exclusion_rows):
        raise ValueError("Duplicate exclusion key")
    seen_exclusions = set()
    files: list[Row] = []
    records: list[Row] = []
    observations: list[Row] = []
    for spec in manifest:
        path = root / "data" / spec["filename"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != spec["sha256"]:
            raise ValueError(f"Source changed; reprofile and review config/sources.json: {path}")
        file_id = "file_" + digest
        workplan = spec["report_type"] == "workplan"
        constants = None
        duplicates: dict[str, str] = {}
        row_count = 0
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.reader(stream, strict=True)
            headers = next(reader)
            if headers != spec["headers"]:
                raise ValueError(f"Schema changed: {path}")
            previous_line = reader.line_num
            for number, values in enumerate(reader, 2):
                end = reader.line_num
                start = previous_line + 1
                previous_line = end
                if not values:
                    continue
                if len(values) != len(headers):
                    raise ValueError(f"Malformed row: {path}:{number}")
                raw = dict(zip(headers, values, strict=True))
                metadata = {h: raw[h] for h in headers[:8]}
                if constants is not None and metadata != constants:
                    raise ValueError(f"Export metadata not constant: {path}")
                constants = metadata
                fields = {h: raw[h] for h in headers[8:]}
                row_id = f"{file_id}:record_{number}"
                row_hash = hashlib.sha256(packed(raw).encode()).hexdigest()
                exclusion = exclusions.get((path.name, number))
                if exclusion:
                    if exclusion["source_organization"] != raw["org_name_Text2"]:
                        raise ValueError("Exclusion source identity changed")
                    seen_exclusions.add((path.name, number))
                org = organizations[raw["org_name_Text2"]]
                ind = indicators[raw["measure_header_Text2"]]
                record = dict(
                    source_record_id=row_id,
                    source_file_id=file_id,
                    source_file=path.name,
                    source_record_number=number,
                    physical_line_start=start,
                    physical_line_end=end,
                    row_sha256=row_hash,
                    duplicate_of=duplicates.get(row_hash, ""),
                    exclusion_reason=exclusion["reason"] if exclusion else "",
                    report_type=spec["report_type"],
                    report_fiscal_year=spec["report_fiscal_year"],
                    organization_id=org["organization_id"],
                    indicator_id=ind["indicator_id"],
                    raw_fields_json=packed(fields),
                )
                records.append(record)
                duplicates.setdefault(row_hash, row_id)
                row_count += 1
                columns = (
                    {"previous": "current_value_text2", "target": "target_value_text2"}
                    if workplan
                    else {
                        "previous": "formatted_current_value2",
                        "target": "formatted_target_value2",
                        "current": "formatted_progress_value2",
                    }
                )
                for role, column in columns.items():
                    value, status = parse_numeric(raw[column])
                    observations.append(
                        dict(
                            observation_id=stable_id("obs", row_id, column),
                            source_record_id=row_id,
                            role=role,
                            source_column=column,
                            raw_value=raw[column],
                            numeric_value=str(value) if value is not None else "",
                            source_status=status,
                        )
                    )
        if row_count != spec["expected_rows"]:
            raise ValueError(f"Source row count changed: {path}")
        files.append(
            dict(
                source_file_id=file_id,
                source_file=path.name,
                sha256=digest,
                report_type=spec["report_type"],
                report_fiscal_year=spec["report_fiscal_year"],
                encoding="utf-8-sig",
                row_count=row_count,
                byte_count=path.stat().st_size,
                headers_json=packed(spec["headers"]),
                constant_fields_json=packed(constants),
            )
        )
    if seen_exclusions != exclusions.keys():
        raise ValueError("Unused exclusions; source identity may have changed")
    return files, records, observations
