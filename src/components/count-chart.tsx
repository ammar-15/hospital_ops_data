"use client";
import {BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend, Text} from 'recharts';
import {Card,CardHeader,CardTitle,CardDescription,CardContent} from '@/components/ui/card';
import {chartLabel,type ChartRow} from '@/lib/presentation';
const COLORS=['#163a5f','#2d737b','#657a8d','#80745b','#5b7770','#6d657f'];
type Props={title:string;description?:string;data:ChartRow[];sampleSize:number;series?:string[];onSelect?:(name:string)=>void;stacked?:boolean};
export function CountChart({title,description,data,sampleSize,series=['count'],onSelect,stacked=false}:Props){
 return <Card className="min-w-0"><CardHeader><CardTitle>{title}</CardTitle><CardDescription>{description} <span className="whitespace-nowrap">n = {sampleSize.toLocaleString()} initiatives</span></CardDescription></CardHeader><CardContent>
 {data.length===0?<p className="py-14 text-center text-sm text-slate-600">No initiatives match the selected filters.</p>:<>
 <div className="h-auto min-w-0" role="img" aria-label={`${title}. ${sampleSize} initiatives. Exact counts in the table below.`}>
 <ResponsiveContainer width="100%" height={Math.max(220,data.length*47+60)} minWidth={0}>
 <BarChart data={data} layout="vertical" margin={{top:8,right:20,left:0,bottom:8}} barSize={16}>
 <CartesianGrid horizontal={false} stroke="#e2e8f0"/><XAxis type="number" allowDecimals={false} tick={{fontSize:11,fill:'#475569'}}/><YAxis type="category" dataKey="name" width={142} tick={({x,y,payload})=><Text x={Number(x)-6} y={Number(y)} width={134} textAnchor="end" verticalAnchor="middle" fontSize={11} fill="#334155">{chartLabel(String(payload.value))}</Text>} interval={0}/>
 <Tooltip cursor={{fill:'#f1f5f9'}} contentStyle={{border:'1px solid #cbd5e1',borderRadius:4,fontSize:12,maxWidth:300,whiteSpace:'normal'}} formatter={(value,name)=>[`${value} initiatives`,name==='count'?'Count':name]} />
 {series.length>1&&<Legend wrapperStyle={{fontSize:11,paddingTop:12}}/>}
 {series.map((key,i)=><Bar key={key} dataKey={key} fill={COLORS[i%COLORS.length]} stackId={stacked?'total':undefined} isAnimationActive={false}/>)}
 </BarChart></ResponsiveContainer></div>
 <details className="mt-2 border-t border-slate-100 pt-3"><summary className="cursor-pointer text-xs font-medium text-primary">View exact counts{onSelect?' and explore records':''}</summary><div tabIndex={0} role="region" aria-label={`${title} exact counts`} className="mt-3 overflow-x-auto"><table className="w-full text-left text-xs"><thead><tr><th className="pb-2 font-medium">Category / group</th>{series.map(key=><th key={key} className="pl-3 pb-2 text-right font-medium">{key==='count'?'Initiatives':key}</th>)}</tr></thead><tbody>{data.map(row=><tr className="border-t border-slate-100" key={row.name}><td className="py-2">{onSelect?<button className="text-left text-primary underline underline-offset-2" onClick={()=>onSelect(row.name)}>{row.name}</button>:row.name}</td>{series.map(key=><td key={key} className="pl-3 text-right tabular-nums">{row[key]}</td>)}</tr>)}</tbody></table></div></details>
 </>}
 </CardContent></Card>;
}
