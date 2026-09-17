import type { ExplorerRecord } from './types';
export const CYCLES = ['2024/25','2025/26','2026/27'] as const;
export function hospitalNames(records: ExplorerRecord[]) { return [...new Set(records.map(r=>r.hospital))].sort(); }
export function hospitalProfile(records: ExplorerRecord[], hospital: string) {
  const rows=records.filter(r=>r.hospital===hospital);
  const statuses=new Map<string,number>(); rows.forEach(r=>statuses.set(r.status,(statuses.get(r.status)??0)+1));
  const labels=(key:'model'|'region')=>[...new Set(rows.map(r=>r[key]||'Unavailable'))].sort().join(' / ')||'Unavailable';
  return {name:hospital,region:labels('region'),model:labels('model'),years:[...new Set(rows.map(r=>r.year))].sort(),indicators:[...new Set(rows.map(r=>r.indicator))].sort(),categories:[...new Set(rows.map(r=>r.category))].sort(),statuses:[...statuses].map(([name,count])=>({name,count})).sort((a,b)=>b.count-a.count)};
}
export function hospitalCycles(records: ExplorerRecord[], hospital: string) {
  return CYCLES.map(year=>{
    const rows=records.filter(r=>r.hospital===hospital&&r.year===year);
    const indicators=[...new Set(rows.map(r=>r.indicator))].sort();
    return {year,records:rows,groups:indicators.map(indicator=>({indicator,records:rows.filter(r=>r.indicator===indicator)}))};
  });
}
