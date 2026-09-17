"use client";
import {createContext,useContext,useEffect,useState,type ReactNode} from 'react';
import {useRouter} from 'next/navigation';
import {fetchExplorer} from '@/lib/data';
import {EMPTY_FILTERS,type ExplorerData,type ExplorerFilters,type FilterKey} from '@/lib/types';
import {filtersQuery,parseFilters} from '@/lib/presentation';
type Context={data:ExplorerData|null;error:string;filters:ExplorerFilters;setFilter:(key:FilterKey,value:string)=>void;reset:()=>void;retry:()=>void;drill:(key:FilterKey,value:string,current?:boolean)=>void};
const ExplorerContext=createContext<Context|null>(null);
export function ExplorerProvider({children}:{children:ReactNode}){
 const [data,setData]=useState<ExplorerData|null>(null),[error,setError]=useState(''),[attempt,setAttempt]=useState(0),[filters,setFilters]=useState<ExplorerFilters>(EMPTY_FILTERS);
 const router=useRouter();
 useEffect(()=>{let active=true;fetchExplorer().then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e instanceof Error?e.message:'Data unavailable')});return()=>{active=false}},[attempt]);
 useEffect(()=>{const sync=()=>setFilters(parseFilters(window.location.search));sync();window.addEventListener('popstate',sync);return()=>window.removeEventListener('popstate',sync)},[]);
 const update=(next:ExplorerFilters)=>{setFilters(next);window.history.replaceState(null,'',`${window.location.pathname}${filtersQuery(next)}`)};
 return <ExplorerContext.Provider value={{data,error,filters,setFilter:(key,value)=>update({...filters,[key]:value}),reset:()=>update({...EMPTY_FILTERS}),retry:()=>{setError('');setAttempt(v=>v+1)},drill:(key,value,current=false)=>{const next={...filters,[key]:value,scope:current?'Current 2026/27':'Historical',...(current?{year:'2026/27'}:{})};setFilters(next);router.push(`/interventions${filtersQuery(next)}`)}}}>{children}</ExplorerContext.Provider>;
}
export function useExplorer(){const context=useContext(ExplorerContext);if(!context)throw new Error('Explorer provider missing');return context;}
