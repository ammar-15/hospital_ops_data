import {z} from 'zod';
import {PROJECT_CONTEXT} from '@/lib/ai/context';
import {nvidiaProvider} from '@/lib/ai/nvidia';
import type {AssistantMessage} from '@/lib/ai/provider';
import {scopeResponse} from '@/lib/ai/scope';
import {SYSTEM_PROMPT} from '@/lib/ai/system-prompt';

export const runtime='nodejs';
const requestSchema=z.object({
 message:z.string().trim().min(1).max(2000),
 history:z.array(z.object({role:z.enum(['user','assistant']),content:z.string().trim().min(1).max(2000)})).max(8).default([]),
 pageContext:z.object({pathname:z.string().max(160),filters:z.record(z.string(),z.string().max(200)).optional()}).optional(),
});
const buckets=new Map<string,{count:number;reset:number}>();
function rateLimited(request:Request){
 const key=request.headers.get('x-forwarded-for')?.split(',')[0]?.trim()||'anonymous'; const now=Date.now(); const bucket=buckets.get(key);
 if (!bucket||bucket.reset<now){buckets.set(key,{count:1,reset:now+60_000});return false;}
 bucket.count++; return bucket.count>12;
}
export async function POST(request:Request){
 if(rateLimited(request)) return Response.json({answer:'Project assistant is receiving too many requests. Please try again shortly.'},{status:429});
 const parsed=requestSchema.safeParse(await request.json().catch(()=>null));
 if(!parsed.success) return Response.json({error:'Invalid assistant request.'},{status:400});
 const {message,history,pageContext}=parsed.data;
 const guarded=scopeResponse(message,history.length>0);
 if(guarded) return Response.json({answer:guarded});
 const provider=nvidiaProvider();
 if(!provider) return Response.json({answer:'Project assistant is currently unavailable.'},{status:503});
 const context=pageContext?`Current page context: ${JSON.stringify(pageContext)}`:'Current page context: not supplied.';
 const messages:AssistantMessage[]=[{role:'system',content:`${SYSTEM_PROMPT}\n\nPROJECT CONTEXT:\n${PROJECT_CONTEXT}\n\n${context}`} ,...history,{role:'user',content:message}];
 try{return Response.json({answer:await provider.complete(messages)});}catch{return Response.json({answer:"I couldn't answer that right now. The dashboard itself is still available."},{status:502});}
}
