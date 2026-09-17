import type { ExplorerData, ExplorerFilters, ExplorerRecord, FilterKey } from './types';

export function filterRecords(records: ExplorerRecord[], filters: ExplorerFilters): ExplorerRecord[] {
  const fields: Record<Exclude<FilterKey,'scope'>, keyof ExplorerRecord> = { year:'year', region:'region', model:'model', hospital:'hospital', indicator:'indicator', category:'category', status:'status' };
  return records.filter(r => (!filters.scope || (r.current?'Current 2026/27':'Historical')===filters.scope) && (Object.keys(fields) as (keyof typeof fields)[]).every(k => !filters[k] || String(r[fields[k]]) === filters[k]));
}
export function getFilterOptions(records: ExplorerRecord[]): Record<FilterKey, string[]> {
  const keys = ['year','region','model','hospital','indicator','category','status'] as FilterKey[];
  return {...Object.fromEntries(keys.map(k => [k, [...new Set(records.map(r => String(r[k as keyof ExplorerRecord])).filter(Boolean))].sort()])),scope:['Historical','Current 2026/27']} as Record<FilterKey,string[]>;
}
export function countBy(records: ExplorerRecord[], key: keyof ExplorerRecord): { name: string; count: number }[] {
  const counts = new Map<string, number>(); records.forEach(r => { const v = String(r[key] ?? 'Unavailable') || 'Unavailable'; counts.set(v, (counts.get(v) ?? 0) + 1); });
  return [...counts].map(([name,count]) => ({name,count})).sort((a,b) => b.count-a.count || a.name.localeCompare(b.name));
}
export type OverviewSummary = { hospitals: number; historicalInitiatives: number; currentInitiatives: number; categories: number; matchedCycles: number; historicalCycleCount: number; implementationStatusReported: number; implementationStatusCoverage: number | null; categoryCounts: ReturnType<typeof countBy>; indicatorCounts: ReturnType<typeof countBy>; modelCounts: ReturnType<typeof countBy>; regionCounts: ReturnType<typeof countBy>; statusCounts: ReturnType<typeof countBy>; historicalCategoryCounts: ReturnType<typeof countBy>; currentCategoryCounts: ReturnType<typeof countBy> };
export function overviewSummary(data: ExplorerData, records = data.records): OverviewSummary {
  const historical = records.filter(r => !r.current), current = records.filter(r => r.current);
  const statusKnown = historical.filter(r => ['Implemented','Not implemented','Partial/conflicting','Conflicting'].includes(r.status));
  const cycles = new Set(historical.map(r => r.cycleId));
  const matched = new Set(data.cycles.filter(c => c.matched && cycles.has(c.id)).map(c => c.id));
  return { hospitals:new Set(records.map(r=>r.hospitalId)).size, historicalInitiatives:historical.length, currentInitiatives:current.length, categories:new Set(records.map(r=>r.category)).size, matchedCycles:matched.size, historicalCycleCount:cycles.size, implementationStatusReported:statusKnown.length, implementationStatusCoverage:historical.length ? statusKnown.length/historical.length*100 : null, categoryCounts:countBy(records,'category'), indicatorCounts:countBy(records,'indicator'), modelCounts:countBy(records,'model'), regionCounts:countBy(records,'region'), statusCounts:countBy(historical,'status'), historicalCategoryCounts:countBy(historical,'category'), currentCategoryCounts:countBy(current,'category') };
}
export function hospitalRecords(records: ExplorerRecord[], hospitalId: string) { return records.filter(r => r.hospitalId === hospitalId); }
export function toCsv(records: ExplorerRecord[]): string {
  const cols: (keyof ExplorerRecord)[] = ['id','cycleId','hospitalId','hospital','region','model','year','indicatorId','indicator','category','idea','status','current','reportType'];
  const cell = (v: unknown) => { const s=String(v ?? ''); const safe=/^[\s]*[=+\-@]/.test(s) ? `'${s}` : s; return `"${safe.replaceAll('"','""')}"`; };
  return [cols.join(','), ...records.map(r=>cols.map(c=>cell(r[c])).join(','))].join('\n');
}
