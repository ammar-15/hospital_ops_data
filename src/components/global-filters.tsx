"use client";
import {SlidersHorizontal,RotateCcw} from 'lucide-react';
import {FILTER_KEYS,FILTER_LABELS} from '@/lib/presentation';
import type {FilterKey} from '@/lib/types';
import {useExplorer} from './explorer-provider';
import {Button} from './ui/button';

export function GlobalFilters({options,count}:{options:Record<FilterKey,string[]>;count:number}){
 const {filters,setFilter,reset}=useExplorer();
 return <details data-tour="filters" open className="mb-6 rounded border border-slate-200 bg-white">
  <summary className="flex cursor-pointer items-center gap-2 px-4 py-3 text-sm font-semibold text-primary"><SlidersHorizontal size={15}/> Filter records <span className="ml-auto text-xs font-normal text-slate-600">{count.toLocaleString()} matching initiatives</span></summary>
  <div className="grid grid-cols-1 gap-3 border-t border-slate-100 p-4 sm:grid-cols-2 lg:grid-cols-4">{FILTER_KEYS.map(key=><label className="block min-w-0 text-xs font-medium text-slate-600" key={key} htmlFor={`filter-${key}`}>{FILTER_LABELS[key]}<select id={`filter-${key}`} value={filters[key]} onChange={e=>setFilter(key,e.target.value)} className="mt-1.5 h-10 w-full min-w-0 truncate rounded border border-slate-300 bg-white px-2 text-sm text-slate-800"><option value="">All {FILTER_LABELS[key].toLowerCase()} values</option>{options[key].map(v=><option key={v} value={v}>{v}</option>)}</select></label>)}<div className="flex items-end"><Button className="w-full" variant="outline" onClick={reset}><RotateCcw size={14}/>Reset filters</Button></div></div>
  <p className="px-4 pb-3 text-xs text-slate-600">Fiscal year refers to the workplan year. Filters persist across exploration pages; source-wide audit counts are labelled separately.</p>
 </details>;
}
