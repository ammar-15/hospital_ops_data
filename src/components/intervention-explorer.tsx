'use client';
import { useMemo, useRef, useState } from 'react';
import { getCoreRowModel, getSortedRowModel, useLegacyTable, type LegacyColumnDef } from '@tanstack/react-table/legacy';
import type { SortingState } from '@tanstack/table-core';
import type { ExplorerRecord, ExplorerDetail } from '@/lib/types';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Table,TableBody,TableCell,TableHead,TableHeader,TableRow } from './ui/table';
import { RecordDetail } from './record-detail';
import { downloadCsv, filterExplorerRecords } from '@/lib/explorer-helpers';
import { fetchDetail as loadDetail } from '@/lib/data';
import { DropdownMenu, DropdownMenuCheckboxItem, DropdownMenuContent, DropdownMenuTrigger } from './ui/dropdown-menu';
const FIELDS = [ ['hospital','Hospital'],['region','Region'],['model','Hospital model'],['year','Fiscal year'],['indicator','Indicator'],['idea','Change idea'],['category','Intervention category'],['status','Implementation status'],['reportType','Report type'] ] as const;
export function InterventionExplorer({records}:{records:ExplorerRecord[]}) {
  const [query,setQuery]=useState(''), [sorting,setSorting]=useState<SortingState>([]), [selected,setSelected]=useState<ExplorerRecord>();
  const [detail,setDetail]=useState<ExplorerDetail|null>(null), [loading,setLoading]=useState(false),[error,setError]=useState(''),[page,setPage]=useState(0),[visible,setVisible]=useState<Record<string,boolean>>({});
  const request=useRef(0);
  const data=useMemo(()=>filterExplorerRecords(records,query),[records,query]);
  const columns=useMemo<LegacyColumnDef<ExplorerRecord>[]>(()=>FIELDS.map(([accessorKey,header])=>({accessorKey,header})),[]);
  const table=useLegacyTable({data,columns,state:{sorting},onSortingChange:setSorting,getCoreRowModel:getCoreRowModel(),getSortedRowModel:getSortedRowModel()});
  const allRows=table.getRowModel().rows, pageSize=25, pages=Math.max(1,Math.ceil(allRows.length/pageSize)),safePage=Math.min(page,pages-1),pageRows=allRows.slice(safePage*pageSize,(safePage+1)*pageSize);
  const open=async(record:ExplorerRecord)=>{const token=++request.current;setSelected(record);setDetail(null);setError('');setLoading(true);try{const result=await loadDetail(record.id);if(token===request.current)setDetail(result)}catch(e){if(token===request.current)setError(e instanceof Error?e.message:'Unable to load source details.')}finally{if(token===request.current)setLoading(false)}};
  return <div className="space-y-4">
    <div className="flex flex-wrap gap-2"><label htmlFor="explorer-search" className="sr-only">Search interventions</label><Input id="explorer-search" className="max-w-md" placeholder="Search hospital, indicator, change idea…" value={query} onChange={e=>{setQuery(e.target.value);setPage(0)}}/><Button variant="outline" onClick={()=>downloadCsv(data)}>Export CSV</Button><DropdownMenu><DropdownMenuTrigger asChild><Button variant="outline">Columns</Button></DropdownMenuTrigger><DropdownMenuContent>{FIELDS.map(([key,label])=><DropdownMenuCheckboxItem key={key} checked={visible[key]!==false} onCheckedChange={v=>setVisible(prev=>({...prev,[key]:Boolean(v)}))}>{label}</DropdownMenuCheckboxItem>)}</DropdownMenuContent></DropdownMenu></div>
    <p className="text-sm text-slate-600" aria-live="polite">{data.length} records · Select a row to inspect source reporting. CSV exports all filtered and searched records.</p>
    <div className="min-w-0 rounded border border-slate-200 bg-white"><Table><TableHeader><TableRow>{FIELDS.map(([key,label])=>visible[key]!==false&&<TableHead key={key} aria-sort={sorting[0]?.id===key?(sorting[0].desc?'descending':'ascending'):'none'}><button className="whitespace-nowrap text-left" onClick={()=>setSorting([{id:key,desc:sorting[0]?.id===key?!sorting[0].desc:false}])}>{label}{sorting[0]?.id===key?(sorting[0].desc?' ↓':' ↑'):''}</button></TableHead>)}<TableHead>Source detail</TableHead></TableRow></TableHeader><TableBody>{pageRows.map(row=><TableRow key={row.original.id} className="cursor-pointer" onClick={()=>open(row.original)}>{FIELDS.map(([key])=>visible[key]!==false&&<TableCell key={key} className={key==='idea'?'min-w-72 max-w-96':key==='hospital'||key==='indicator'?'min-w-48 max-w-64':'min-w-32'}><span className="line-clamp-3 text-xs leading-5">{row.original[key]||'Unavailable'}</span></TableCell>)}<TableCell><Button size="sm" variant="outline" aria-label={`View source details for ${row.original.hospital}`} onClick={e=>{e.stopPropagation();open(row.original)}}>View details</Button></TableCell></TableRow>)}</TableBody></Table></div>
    {!pageRows.length&&<p className="rounded border bg-white p-6 text-center text-sm text-slate-600">No interventions match the current filters and search.</p>}
    <div className="flex items-center justify-between gap-2"><Button variant="outline" disabled={safePage===0} onClick={()=>setPage(safePage-1)}>Previous</Button><span className="text-sm text-slate-600">Page {safePage+1} of {pages}</span><Button variant="outline" disabled={safePage+1>=pages} onClick={()=>setPage(safePage+1)}>Next</Button></div>
    <RecordDetail record={selected} detail={detail} loading={loading} error={error} onRetry={()=>selected&&open(selected)} open={Boolean(selected)} onOpenChange={isOpen=>{if(!isOpen){request.current++;setSelected(undefined)}}}/>
  </div>;
}
