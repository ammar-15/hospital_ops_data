import { describe, expect, it } from 'vitest';
import { countBy, filterRecords, overviewSummary, toCsv } from './analytics';
import { EMPTY_FILTERS, type ExplorerData, type ExplorerRecord } from './types';

const record = (x: Partial<ExplorerRecord> = {}): ExplorerRecord => ({ id:'1',cycleId:'c1',hospitalId:'h1',hospital:'Hospital',region:'East',model:'Community',year:'2025/26',indicatorId:'i1',indicator:'Indicator',category:'Care',idea:'Improve flow',status:'Implemented',current:false,reportType:'Workplan + progress',...x });
const data = (records: ExplorerRecord[]): ExplorerData => ({ records, cycles:[{id:'c1',hospitalId:'h1',indicatorId:'i1',year:'2025/26',matched:true,hasWorkplan:true,numericPair:true,periodVerified:false,matchStatus:'matched'}], indicators:[], audit:{totalSourceRows:1,includedSourceRows:1,excludedTestRows:0,ambiguousMatches:0,implementationConflicts:0,historicalOther:0,historicalIdeas:1,currentIdeas:0,allHospitals:1,pairs:[],sourceFiles:[]}, provenance:{scope:'ED',inputSha256:{}} });
describe('analytics', () => {
  it('keeps empty denominators unavailable', () => expect(overviewSummary(data([])).implementationStatusCoverage).toBeNull());
  it('filters exact selected values and counts', () => { const rs=[record(),record({id:'2',region:'West'})]; expect(filterRecords(rs,{...EMPTY_FILTERS,region:'West'})).toHaveLength(1); expect(countBy(rs,'region')).toEqual([{name:'East',count:1},{name:'West',count:1}]); });
  it('separates current plans and does not expose outcomes', () => { const rs=[record(),record({id:'2',current:true,status:'Current plan',reportType:'Current workplan'})]; const s=overviewSummary(data(rs)); expect(s.historicalInitiatives).toBe(1); expect(s.currentInitiatives).toBe(1); expect(Object.keys(rs[0])).not.toContain('outcome'); });
  it('escapes spreadsheet formulas in CSV', () => expect(toCsv([record({idea:'=SUM(A1)'})])).toContain("'=SUM(A1)"));
  it('reports conflicting flags as coverage without resolving implementation', () => {
    const s=overviewSummary(data([record({status:'Conflicting'}),record({id:'2',status:'Unavailable'})]));
    expect(s.implementationStatusReported).toBe(1);
    expect(s.implementationStatusCoverage).toBe(50);
    expect(s.statusCounts).toContainEqual({name:'Conflicting',count:1});
    expect(s.matchedCycles).toBe(1);
  });
  it('keeps chart drill-down cohorts distinct and incompatible selections empty', () => {
    const rows=[record(),record({id:'2',current:true,year:'2026/27',status:'Current plan'})];
    expect(filterRecords(rows,{...EMPTY_FILTERS,scope:'Historical'})).toHaveLength(1);
    expect(filterRecords(rows,{...EMPTY_FILTERS,scope:'Historical',year:'2026/27'})).toHaveLength(0);
    expect(filterRecords(rows,{...EMPTY_FILTERS,scope:'Current 2026/27',status:'Implemented'})).toHaveLength(0);
  });
  it('protects whitespace-prefixed formulas and retains reported zero text', () => {
    expect(toCsv([record({idea:'\t=SUM(A1)'})])).toContain("'\t=SUM(A1)");
    expect(toCsv([record({idea:'0'})])).toContain('"0"');
  });
});
