"use client";
import {useEffect,useState} from 'react';
import {Dialog} from 'radix-ui';
import {Button} from './ui/button';

const steps=[
 ['project-introduction','What is this?',"Ontario hospitals publish Quality Improvement Plans describing areas they want to improve and the changes they plan to make. This explorer organizes those reports, focusing on emergency-department access and patient flow."],
 ['filters','Narrow the data','Use these filters to focus on a fiscal year, region, hospital type, hospital, indicator, intervention category, implementation status, or report cohort.'],
 ['kpi-summary','Understand the summary','These cards summarize the records currently selected. They show activity and data coverage, not hospital scores or rankings.'],
 ['improvement-activity','Explore improvement activity','These charts show which ED problems hospitals focus on and the types of operational changes they report, such as discharge planning, staffing, patient flow, or technology.'],
 ['reporting-limitation','Know what cannot be concluded','The reporting periods are not consistently comparable, so this project does not calculate which interventions worked, rank hospitals, or measure intervention effectiveness.'],
] as const;
const storage={completed:'tourCompleted',dismissed:'tourDismissed'};
export function GuidedTour(){
 const [open,setOpen]=useState(false); const [step,setStep]=useState(0); const [showNotice,setShowNotice]=useState(false);
 useEffect(()=>{const start=()=>{setStep(0);setOpen(true)};window.addEventListener('open-guided-tour',start);const timer=location.pathname==='/'&&!localStorage.getItem(storage.completed)&&!localStorage.getItem(storage.dismissed)?window.setTimeout(()=>setShowNotice(true),0):undefined;return()=>{window.removeEventListener('open-guided-tour',start);if(timer)window.clearTimeout(timer);};},[]);
 useEffect(()=>{if(!open)return;document.querySelector(`[data-tour="${steps[step][0]}"]`)?.scrollIntoView({block:'center',behavior:'auto'});},[open,step]);
 const close=(complete=false)=>{if(complete)localStorage.setItem(storage.completed,'true');else localStorage.setItem(storage.dismissed,'true');setOpen(false);setShowNotice(false);};
 return <>
  {showNotice&&<aside aria-label="Dashboard tour" className="fixed bottom-5 left-4 z-30 max-w-sm rounded border border-slate-300 bg-white p-4 shadow-sm sm:left-auto sm:right-5"><p className="text-sm leading-5 text-slate-700">New here? Take a 60-second tour to learn how to read this dashboard.</p><div className="mt-3 flex gap-2"><Button size="sm" onClick={()=>{setShowNotice(false);setStep(0);setOpen(true);}}>Take tour</Button><Button size="sm" variant="ghost" onClick={()=>close(false)}>Dismiss</Button></div></aside>}
  <Dialog.Root open={open} onOpenChange={next=>{if(!next)close(false)}}><Dialog.Portal><Dialog.Overlay className="fixed inset-0 z-40 bg-slate-950/20"/><Dialog.Content aria-describedby="tour-description" className="fixed bottom-4 left-4 z-50 w-[calc(100%-2rem)] max-w-md rounded border border-slate-300 bg-white p-5 shadow-lg sm:bottom-6 sm:left-6"><p className="text-xs font-medium text-secondary">Quick tour · {step+1} of 5</p><Dialog.Title className="mt-1 text-lg font-semibold text-primary">{steps[step][1]}</Dialog.Title><Dialog.Description id="tour-description" className="mt-2 text-sm leading-6 text-slate-600">{steps[step][2]}</Dialog.Description><div className="mt-5 flex items-center justify-between gap-2"><Button variant="ghost" size="sm" onClick={()=>close(false)}>Skip</Button><div className="flex gap-2">{step>0&&<Button variant="outline" size="sm" onClick={()=>setStep(step-1)}>Back</Button>}{step===4?<Button size="sm" onClick={()=>close(true)}>Start exploring</Button>:<Button size="sm" onClick={()=>setStep(step+1)}>Next</Button>}</div></div></Dialog.Content></Dialog.Portal></Dialog.Root>
 </>;
}
