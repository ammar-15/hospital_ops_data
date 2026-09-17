import { describe, expect, it } from 'vitest'
import fs from 'node:fs'
import path from 'node:path'
import {dataSchema,detailSchema} from './data'

const root = path.resolve(process.cwd(), 'public/data')
const payload = JSON.parse(fs.readFileSync(path.join(root, 'explorer.json'), 'utf8')) as {
  records: Record<string, unknown>[]; cycles: { year: string; matched: boolean; numericPair: boolean }[]
}

describe('generated explorer export contract', () => {
  it('validates complete runtime audit and source-detail contracts',()=>{
    expect(()=>dataSchema.parse(payload)).not.toThrow();
    for(const record of payload.records){
      const detail=JSON.parse(fs.readFileSync(path.join(root,'details',`${record.id}.json`),'utf8'));
      expect(()=>detailSchema.parse(detail)).not.toThrow();
      expect(detail.id).toBe(record.id);
      expect(detail.sources.length).toBeGreaterThan(0);
    }
    expect(()=>dataSchema.parse({...payload,audit:{}})).toThrow();
  });
  it('contains the expected planning and cycle coverage', () => {
    expect(payload.records.filter(r => r.current === false)).toHaveLength(488)
    expect(payload.records.filter(r => r.current === true)).toHaveLength(429)
    const primary = payload.cycles.filter(c => c.year === '2025/26')
    expect(primary).toHaveLength(206)
    expect(primary.filter(c => c.matched)).toHaveLength(130)
    expect(primary.filter(c => c.numericPair)).toHaveLength(129)
  })
  it('does not export outcome or target analytics fields', () => {
    const forbidden = ['outcome', 'outcomeClass', 'targetMet', 'target_met', 'performanceChange', 'performance_change']
    for (const record of payload.records) for (const key of forbidden) expect(record).not.toHaveProperty(key)
  })
  it('keeps IDs unique and detail source records traceable', () => {
    const ids = payload.records.map(r => r.id)
    expect(new Set(ids).size).toBe(ids.length)
    const sample = ids.find(id => fs.existsSync(path.join(root, 'details', `${id}.json`)))
    expect(sample).toBeDefined()
    const detail = JSON.parse(fs.readFileSync(path.join(root, 'details', `${sample}.json`), 'utf8')) as { sources: { id: string; raw: Record<string, string> }[] }
    expect(detail.sources.length).toBeGreaterThan(0)
    expect(detail.sources[0].id).toBeTruthy()
    expect(Object.keys(detail.sources[0].raw).length).toBeGreaterThan(0)
  })
})
