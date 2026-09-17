export type ExplorerRecord = {
  id: string; cycleId: string; hospitalId: string; hospital: string; region: string;
  model: string; year: string; indicatorId: string; indicator: string;
  category: string; idea: string; status: string; current: boolean; reportType: string;
};

export type ExplorerCycle = {
  id: string; hospitalId: string; indicatorId: string; year: string;
  matched: boolean; hasWorkplan: boolean; numericPair: boolean;
  periodVerified: boolean; matchStatus: string;
};

export type ExplorerIndicator = { id: string; name: string; unit: string; population: string };
export type AuditPair = { year: string; scope: string; matched: number; denominator: number; numericPairs: number };
export type ExplorerAudit = {
  totalSourceRows: number; includedSourceRows: number; excludedTestRows: number;
  ambiguousMatches: number; implementationConflicts: number; historicalOther: number;
  historicalIdeas: number; currentIdeas: number; allHospitals: number; pairs: AuditPair[];
  sourceFiles: { name: string; rows: number; sha256: string }[];
};
export type ExplorerData = {
  records: ExplorerRecord[]; cycles: ExplorerCycle[]; indicators: ExplorerIndicator[];
  audit: ExplorerAudit; provenance: { scope: string; inputSha256: Record<string, string> };
};
export type ExplorerSource = { id: string; file: string; record: number; lineStart: number; lineEnd: number; year: string; type: string; raw: Record<string,string> };
export type ExplorerDetail = { id: string; sources: ExplorerSource[]; methods: string[]; measures: string[]; targets: string[]; comments: string[]; implementationNotes: string[]; progressComments: string[]; classificationReason: string; classificationRules: string[]; classificationVersion: string; secondaryTags: string[] };
export type FilterKey = 'year'|'region'|'model'|'hospital'|'indicator'|'category'|'status'|'scope';
export type ExplorerFilters = Record<FilterKey, string>;
export const EMPTY_FILTERS: ExplorerFilters = { year:'', region:'', model:'', hospital:'', indicator:'', category:'', status:'', scope:'' };
