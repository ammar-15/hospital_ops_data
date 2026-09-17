import type {ExplorerSource} from './types';
const fields:Record<string,string>={current_value_text2:'Reported workplan baseline',target_value_text2:'Reported workplan target',formatted_current_value2:'Reported previous value',formatted_target_value2:'Reported target value',formatted_progress_value2:'Reported current value',unit_population_Text2:'Reported unit / population',datasource_period_Text2:'Reported data source / period'};
export function performanceFields(source:ExplorerSource){return Object.entries(fields).filter(([key])=>key in source.raw).map(([key,label])=>({key,label,value:source.raw[key]||'Unavailable'}));}
export function rawFields(source:ExplorerSource){return Object.entries(source.raw).map(([name,value])=>({name,value:value||'Unavailable'}));}
