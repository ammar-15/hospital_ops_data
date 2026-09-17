import { countBy, filterRecords, getFilterOptions, overviewSummary } from './analytics';
import { EMPTY_FILTERS, type ExplorerData, type ExplorerFilters, type FilterKey } from './types';
export type CountRow = { name: string; count: number };
export type ChartRow = { name: string; [key: string]: string | number };
export function pageModel(data: ExplorerData, filters: ExplorerFilters, currentOnly = false) {
  const records = filterRecords(data.records, filters);
  const historical = records.filter(r => !r.current);
  const current = records.filter(r => r.current);
  const chartRecords = currentOnly ? current : historical;
  const categories = countBy(chartRecords, 'category');
  const models = countBy(chartRecords, 'model');
  const matrix = categories.map(c => ({ name:c.name, ...Object.fromEntries(models.map(m => [m.name, chartRecords.filter(r => r.category===c.name && r.model===m.name).length])) }));
  const categoryNames = [...new Set(records.map(r=>r.category))].sort();
  const comparison = categoryNames.map(name => ({name, Historical:historical.filter(r=>r.category===name).length, 'Current 2026/27':current.filter(r=>r.category===name).length}));
  const categoryHospitals = categories.map(c => ({name:c.name, hospitals:[...new Set(chartRecords.filter(r=>r.category===c.name).map(r=>r.hospital))].sort(), count:c.count}));
  return { records, historical, current, chartRecords, summary:overviewSummary(data, records), options:getFilterOptions(data.records), categories, indicators:countBy(chartRecords,'indicator'), models, regions:countBy(chartRecords,'region'), statuses:countBy(chartRecords,'status'), matrix, modelNames:models.map(r=>r.name), comparison, categoryHospitals };
}
export function parseFilters(search: string): ExplorerFilters {
  const params = new URLSearchParams(search);
  return Object.fromEntries(Object.keys(EMPTY_FILTERS).map(key=>[key,params.get(key)??''])) as ExplorerFilters;
}
export function filtersQuery(filters: ExplorerFilters): string {
  const params=new URLSearchParams();
  for (const [key,value] of Object.entries(filters)) if(value) params.set(key,value);
  const query=params.toString(); return query ? `?${query}` : '';
}
export const FILTER_LABELS: Record<FilterKey,string> = {year:'Fiscal year',region:'Region',model:'Hospital model',hospital:'Hospital',indicator:'Indicator',category:'Intervention category',status:'Implementation status',scope:'Report cohort'};
export const FILTER_KEYS=Object.keys(FILTER_LABELS) as FilterKey[];
export const formatCount=(n:number)=>n.toLocaleString('en-CA');
const chartLabels:Record<string,string>={
  'ED visits leaving without physician assessment':'Left without physician assessment',
  'Patients awaiting a bed at 8 a.m. (daily average)':'Awaiting bed at 8 a.m.',
  'Nonadmitted ED stay, CTAS 1–3 (90th percentile)':'Nonadmitted stay · CTAS 1–3',
  'Nonadmitted ED stay, CTAS 4–5 (90th percentile)':'Nonadmitted stay · CTAS 4–5',
  'Time to physician assessment (90th percentile)':'Physician assessment wait',
  'Ambulance offload (90th percentile)':'Ambulance offload time',
  'Disposition to inpatient bed (90th percentile)':'Disposition to inpatient bed',
  'Admitted ED stay (90th percentile)':'Admitted ED stay',
  'Care Coordination & Communication':'Care coordination & communication',
  'Data, Measurement & Dashboards':'Data & measurement',
  'Discharge & Transition Planning':'Discharge & transitions',
  'Emergency Department Workflow':'ED workflow',
  'Large Community Hospital':'Large community',
  'Specialty Children Hospital':'Specialty children',
  'Specialty Mental Health Hospital':'Specialty mental health',
};
export function chartLabel(label:string){return chartLabels[label]??label;}
