"use client";
import {useMemo} from 'react';
import Link from 'next/link';
import {ArrowRight,HelpCircle,Map} from 'lucide-react';
import {useExplorer} from './explorer-provider';
import {GlobalFilters} from './global-filters';
import {Overview} from './overview';
import {CurrentPlans} from './current-plans';
import {InterventionExplorer} from './intervention-explorer';
import {HospitalExplorer} from './hospital-explorer';
import {ReportingQuality} from './reporting-quality';
import {Methodology} from './methodology';
import {pageModel} from '@/lib/presentation';
import {Button} from './ui/button';
export type View='overview'|'interventions'|'hospitals'|'current-plans'|'reporting-quality'|'methodology';
const copy:Record<Exclude<View,'overview'>,[string,string]>={interventions:['Intervention Explorer','Inspect planned changes, implementation reporting and original source records.'],hospitals:['Hospital Explorer','Explore a hospital’s improvement priorities, reported implementation and current plans.'],'current-plans':['Current 2026/27 Plans','What are Ontario hospitals planning to do next?'],'reporting-quality':['Reporting & Data Quality','An audit of source coverage, matching, classification and reporting limitations.'],methodology:['Methodology','How source reports become a traceable, descriptive exploration of quality improvement activity.']};
const openTour=()=>window.dispatchEvent(new Event('open-guided-tour'));
const openAssistant=()=>window.dispatchEvent(new Event('open-project-assistant'));
export function ExplorerPage({view}:{view:View}){
 const {data,error,filters,retry,drill}=useExplorer();
 const model=useMemo(()=>data?pageModel(data,filters,view==='current-plans'):null,[data,filters,view]);
 const overview=view==='overview';
 const [title,subtitle]=overview?['Ontario Hospital Quality Improvement Explorer',"See what Ontario hospitals say they're trying to improve, the operational changes they're making, and what they're planning next."]:copy[view as Exclude<View,'overview'>];
 return <div className="min-w-0 space-y-6"><div data-tour={overview?'project-introduction':undefined}><p className="mb-2 text-[11px] font-semibold uppercase tracking-wider text-secondary">Quality improvement plans · Ontario</p><h1 className="text-2xl font-semibold tracking-tight text-primary sm:text-[28px]">{title}</h1><p className="mt-2 max-w-4xl text-sm leading-6 text-slate-600">{subtitle}</p>{overview&&<><p className="mt-1 max-w-4xl text-xs leading-5 text-slate-500">Built from Ontario Health Quality Improvement Plan reports, with a focus on emergency-department access and patient flow.</p><div className="mt-3 flex flex-wrap gap-2"><Button variant="outline" size="sm" onClick={openTour}><Map size={14}/>Take a quick tour</Button><Button variant="outline" size="sm" onClick={openAssistant}><HelpCircle size={14}/>Ask about this project</Button><Button variant="outline" size="sm" asChild><Link href="/methodology"><ArrowRight size={14}/>Methodology</Link></Button></div></>}</div>{view==='methodology'?<Methodology/>:error?<div role="alert" className="rounded border bg-white p-6"><h2 className="font-semibold">Data unavailable</h2><p className="my-3">{error}</p><Button onClick={retry}>Try again</Button></div>:!model||!data?<div role="status" className="border bg-white p-8">Loading processed reporting data…</div>:<><GlobalFilters options={model.options} count={view==='current-plans'?model.current.length:model.records.length}/>{view==='overview'&&<Overview model={model} onDrill={drill}/>} {view==='current-plans'&&<CurrentPlans model={model} onDrill={(k,v)=>drill(k,v,true)}/>} {view==='interventions'&&<InterventionExplorer records={model.records}/>} {view==='hospitals'&&<HospitalExplorer records={model.records}/>} {view==='reporting-quality'&&<ReportingQuality data={data} records={model.records}/>}</>}</div>;
}
