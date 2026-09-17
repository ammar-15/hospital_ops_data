import type { ExplorerData, ExplorerRecord } from './types';
export type AuditMetric = { label: string; value: number | string; detail?: string };
export function rate(value: number, denominator: number): string {
  return denominator > 0 ? `${value.toLocaleString()} / ${denominator.toLocaleString()} (${((value / denominator) * 100).toFixed(1)}%)` : 'Unavailable';
}
function selectedCycles(data:ExplorerData,records:ExplorerRecord[]) {
  const ids = new Set(records.filter(r=>!r.current).map(r=>r.cycleId));
  return data.cycles.filter(c=>ids.has(c.id));
}
export function primaryEdRate(data: ExplorerData, records: ExplorerRecord[]) {
  const cycles=selectedCycles(data,records).filter(c=>c.year==='2025/26');
  const matched=cycles.filter(c=>c.matched);
  return {matched:rate(matched.length,cycles.length),numeric:rate(matched.filter(c=>c.numericPair).length,matched.length),verified:cycles.filter(c=>c.periodVerified).length,total:cycles.length};
}
export function auditMetrics(data: ExplorerData, records: ExplorerRecord[]): AuditMetric[] {
  const a=data.audit, historical=records.filter(r=>!r.current), cycles=selectedCycles(data,records);
  const known=historical.filter(r=>['Implemented','Not implemented','Conflicting'].includes(r.status)).length;
  return [
    {label:'Source rows (fixed denominator)',value:a.totalSourceRows.toLocaleString(),detail:'All five source files, including excluded test rows'},
    {label:'Included source rows',value:a.includedSourceRows.toLocaleString(),detail:'All indicators; fixed source audit'},
    {label:'Matched cycles — all indicators',value:a.pairs.filter(p=>p.scope==='All hospital indicators').reduce((n,p)=>n+p.matched,0).toLocaleString(),detail:'Accepted matches across both historical pairs; unfiltered'},
    {label:'Excluded test records',value:a.excludedTestRows,detail:'Retained in source audit; excluded from explorer records'},
    {label:'Ambiguous matches',value:a.ambiguousMatches,detail:'All indicators; unresolved historical groups'},
    {label:'Implementation conflicts',value:a.implementationConflicts,detail:'All historical ideas with contradictory Y/N flags'},
    {label:'Historical Other — all indicators',value:rate(a.historicalOther,a.historicalIdeas),detail:'Unfiltered classification coverage'},
    {label:'Historical Other — filtered ED',value:rate(historical.filter(r=>r.category==='Other').length,historical.length),detail:'Selected historical idea associations'},
    {label:'Matched cycles (filtered ED)',value:rate(cycles.filter(c=>c.matched).length,cycles.length),detail:'Matched / selected candidate cycles; deduplicated'},
    {label:'Numeric pairs (filtered ED)',value:rate(cycles.filter(c=>c.matched&&c.numericPair).length,cycles.filter(c=>c.matched).length),detail:'Numeric availability / selected matched cycles; not comparability'},
    {label:'Reported implementation status',value:rate(known,historical.length),detail:'Implemented, Not implemented or Conflicting / selected historical ideas'},
    {label:'Analyzable outcome rate',value:'Unavailable',detail:'No verified comparable observation windows; no outcome percentage is calculated'},
  ];
}
