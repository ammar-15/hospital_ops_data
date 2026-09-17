"""Export presentation data from processed CSVs only. No outcome calculations."""

import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def export(root: Path = ROOT) -> dict:
    processed = root / 'data/processed'
    destination = root / 'public/data'
    details_dir = destination / 'details'
    details_dir.mkdir(parents=True, exist_ok=True)

    def read(name):
        with (processed / f'{name}.csv').open(newline='', encoding='utf-8') as stream:
            return list(csv.DictReader(stream))

    def write(path, value):
        path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n')

    organizations = {r['organization_id']: r for r in read('organizations')}
    indicators = {r['indicator_id']: r for r in read('indicators')}
    sources = {r['source_record_id']: r for r in read('source_records')}
    cycles = {r['cycle_id']: r for r in read('performance_cycles')}
    groups = {r['current_plan_group_id']: r for r in read('current_plan_groups')}
    historical, current = read('interventions'), read('current_workplans')

    def attribute(ids, key):
        values = {json.loads(sources[s]['raw_fields_json'])[key].strip() for s in ids} - {'', 'No type available'}
        return next(iter(values)) if len(values) == 1 else 'Unavailable' if not values else 'Conflicting'

    entries = []
    for row in historical + current:
        indicator = indicators[row['indicator_id']]
        if indicator['ed_scope'] != 'included':
            continue
        is_current = 'current_plan_group_id' in row
        parent = groups[row['current_plan_group_id']] if is_current else cycles[row['cycle_id']]
        ids = json.loads(row['workplan_source_ids']) + json.loads(row['progress_source_ids'])
        status = 'Current plan' if is_current else {'Unknown': 'Unavailable', 'Partial/conflicting': 'Conflicting'}.get(row['implementation_status'], row['implementation_status'])
        entry = dict(id=row['intervention_id'], cycleId=parent.get('cycle_id', parent.get('current_plan_group_id')),
                     hospitalId=row['organization_id'], hospital=organizations[row['organization_id']]['normalized_organization_name'],
                     region=attribute(ids, 'LHIN_Label_Text2'), model=attribute(ids, 'OrgCategory_Label_Text2'),
                     year=row['plan_fiscal_year'], indicatorId=row['indicator_id'], indicator=indicator['display_name'],
                     category=row['primary_category'], idea=row['change_idea_raw'], status=status, current=is_current,
                     reportType='Current workplan' if is_current else {'workplan_and_progress':'Workplan + progress', 'workplan_only':'Workplan only', 'progress_only':'Progress only'}[row['association_status']])
        entries.append(entry)
        source_rows = []
        for sid in ids:
            source = sources[sid]
            raw = json.loads(source['raw_fields_json'])
            source_rows.append(dict(id=sid, file=source['source_file'], record=int(source['source_record_number']),
                                    lineStart=int(source['physical_line_start']), lineEnd=int(source['physical_line_end']),
                                    year=source['report_fiscal_year'], type=source['report_type'], raw=raw))
        detail = dict(id=entry['id'], sources=source_rows,
                      methods=json.loads(row['planned_methods_raw']), measures=json.loads(row['process_measures_raw']),
                      targets=json.loads(row['process_targets_raw']), comments=json.loads(row['workplan_comments_raw']),
                      implementationNotes=json.loads(row.get('implementation_notes_raw','[]')),
                      progressComments=json.loads(row.get('progress_comments_raw','[]')),
                      classificationReason=row['classification_reason'], classificationRules=json.loads(row['classification_rule_used']),
                      classificationVersion=row['taxonomy_version'], secondaryTags=json.loads(row['secondary_tags']))
        write(details_dir / f"{entry['id']}.json", detail)
    ed_cycles = [dict(id=c['cycle_id'], hospitalId=c['organization_id'], indicatorId=c['indicator_id'], year=c['plan_fiscal_year'],
                      matched=c['match_status']=='matched', hasWorkplan=int(c['workplan_row_count'])>0,
                      numericPair=c['previous_status']==c['current_status']=='numeric',
                      periodVerified=c['reporting_period_verified']=='true',
                      matchStatus=c['match_status']) for c in cycles.values() if c['ed_scope']=='included']
    audit_pairs = []
    for year in ['2024/25', '2025/26']:
        for scope in ['All hospital indicators', 'Reviewed ED indicators']:
            cohort = [c for c in cycles.values() if c['plan_fiscal_year']==year and (scope=='All hospital indicators' or c['ed_scope']=='included')]
            audit_pairs.append(dict(year=year, scope=scope, matched=sum(c['match_status']=='matched' for c in cohort),
                                    denominator=sum(int(c['workplan_row_count'])>0 for c in cohort),
                                    numericPairs=sum(c['previous_status']==c['current_status']=='numeric' for c in cohort)))
    payload = dict(records=entries, cycles=ed_cycles,
                   indicators=[dict(id=i['indicator_id'], name=i['display_name'], unit=i['unit'], population=i['comparable_population']) for i in indicators.values() if i['ed_scope']=='included'],
                   audit=dict(totalSourceRows=len(sources), includedSourceRows=sum(not s['exclusion_reason'] for s in sources.values()),
                              excludedTestRows=sum(bool(s['exclusion_reason']) for s in sources.values()),
                              ambiguousMatches=sum(c['match_status']=='ambiguous' for c in cycles.values()),
                              implementationConflicts=sum(i['implementation_status']=='Partial/conflicting' for i in historical),
                              historicalOther=sum(i['primary_category']=='Other' for i in historical), historicalIdeas=len(historical),
                              currentIdeas=len(current), allHospitals=len(organizations), pairs=audit_pairs,
                              sourceFiles=[dict(name=f['source_file'], rows=int(f['row_count']), sha256=f['sha256']) for f in read('source_files')]),
                   provenance=dict(scope='Eight reviewed ED indicators', inputSha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(processed.glob('*.csv'))}))
    write(destination/'explorer.json',payload)
    # Documentation is published verbatim for source/methodology audit, separately from healthcare data.
    docs_dir = root/'public/documentation'
    docs_dir.mkdir(parents=True, exist_ok=True)
    for name in ['methodology','data-profile','taxonomy-review','reporting-period-review','indicator-metadata','frontend-methodology']:
        (docs_dir/f'{name}.md').write_bytes((root/'docs'/f'{name}.md').read_bytes())
    (docs_dir/'README.md').write_bytes((root/'README.md').read_bytes())
    # Structural checks keep this export reusable as source snapshots evolve.
    assert len(entries) == len({e['id'] for e in entries})
    assert all(e['id'] and e['cycleId'] and e['hospitalId'] and e['indicatorId'] for e in entries)
    assert all('outcome' not in e and 'performanceChange' not in e for e in entries)
    assert all(s['id'] for d in destination.joinpath('details').glob('*.json') for s in json.loads(d.read_text())['sources'])
    print(f"Exported {len(entries)} ED idea associations and {len(ed_cycles)} cycles; no outcome fields.")
    return payload


if __name__ == '__main__':
    export()
