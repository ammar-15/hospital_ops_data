import type { ExplorerRecord } from '@/lib/types'
import {toCsv} from './analytics'

export const EXPLORER_NOTICE = 'Reported values are shown as submitted. Reporting periods have not been verified as directly comparable, so no performance change is calculated.'

export function filterExplorerRecords(records: ExplorerRecord[], query: string) {
  const q = query.trim().toLowerCase()
  if (!q) return records
  return records.filter((r) => [r.hospital, r.region, r.model, r.year, r.indicator, r.category, r.idea, r.status, r.reportType].some((v) => v.toLowerCase().includes(q)))
}

export function downloadCsv(records: ExplorerRecord[], filename = 'interventions.csv') {
  const csv = toCsv(records)
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' }); const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = filename; a.click(); URL.revokeObjectURL(url)
}

export function cycleLabel(year: string) {
  if (year === '2024/25') return '2024/25 Workplan → 2025/26 Progress Report'
  if (year === '2025/26') return '2025/26 Workplan → 2026/27 Progress Report'
  return '2026/27 Current Workplan'
}
