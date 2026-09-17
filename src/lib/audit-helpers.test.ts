import { describe, expect, it } from 'vitest';
import { auditMetrics } from './audit-helpers';
import type { ExplorerData, ExplorerRecord } from './types';

const record = (id: string, cycleId: string, current = false, category = 'Other', status = 'Unknown'): ExplorerRecord => ({ id, cycleId, hospitalId: 'h', hospital: 'Hospital', region: 'Region', model: 'Model', year: '2025/26', indicatorId: 'i', indicator: 'Indicator', category, idea: 'Idea', status, current, reportType: 'Workplan + progress' });
const data = (cycles: ExplorerData['cycles']): ExplorerData => ({ records: [], cycles, indicators: [], audit: { totalSourceRows: 10, includedSourceRows: 8, excludedTestRows: 2, ambiguousMatches: 1, implementationConflicts: 1, historicalOther: 2, historicalIdeas: 3, currentIdeas: 0, allHospitals: 1, pairs: [], sourceFiles: [] }, provenance: { scope: 'ED', inputSha256: {} } });

describe('auditMetrics', () => {
  it('deduplicates detail records at cycle grain and reports numeric availability separately', () => {
    const cycles = [{ id: 'c1', hospitalId: 'h', indicatorId: 'i', year: '2025/26', matched: true, hasWorkplan: true, numericPair: true, periodVerified: false, matchStatus: 'matched' }, { id: 'c2', hospitalId: 'h', indicatorId: 'j', year: '2025/26', matched: false, hasWorkplan: true, numericPair: false, periodVerified: false, matchStatus: 'workplan_only' }];
    const values = auditMetrics(data(cycles), [record('1', 'c1'), record('2', 'c1', false, 'Other', 'Conflicting'), record('3', 'c2')]);
    expect(values.find((m) => m.label === 'Matched cycles (filtered ED)')?.value).toBe('1 / 2 (50.0%)');
    expect(values.find((m) => m.label.startsWith('Numeric'))?.value).toBe('1 / 1 (100.0%)');
    expect(values.find(m=>m.label==='Historical Other — all indicators')?.value).toBe('2 / 3 (66.7%)');
    expect(values.find(m=>m.label==='Historical Other — filtered ED')?.value).toBe('3 / 3 (100.0%)');
  });
  it('uses Unavailable when no historical records exist', () => {
    const values = auditMetrics(data([]), []);
    expect(values.find((m) => m.label === 'Historical Other — filtered ED')?.value).toBe('Unavailable');
    expect(values.find((m) => m.label === 'Reported implementation status')?.value).toBe('Unavailable');
  });
});
