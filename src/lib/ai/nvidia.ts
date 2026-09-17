import type {AssistantProvider} from './provider';

const TIMEOUT_MS = 15_000;
export function nvidiaProvider():AssistantProvider|undefined {
 const {MODEL,BASE_URL,API_KEY}=process.env;
 if (!MODEL || !BASE_URL || !API_KEY) return undefined;
 return {async complete(messages){
  const controller=new AbortController();
  const timeout=setTimeout(()=>controller.abort(),TIMEOUT_MS);
  try {
   const response=await fetch(`${BASE_URL.replace(/\/$/,'')}/chat/completions`,{method:'POST',headers:{Authorization:`Bearer ${API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({model:MODEL,messages,temperature:0.2,max_tokens:180,chat_template_kwargs:{enable_thinking:false}}),signal:controller.signal});
   if (!response.ok) throw new Error('Provider request failed');
   const body=await response.json() as {choices?:Array<{message?:{content?:string}}>};
   const answer=body.choices?.[0]?.message?.content?.trim();
   if (!answer) throw new Error('Provider returned no answer');
   // Defensive cleanup for endpoints that emit an unparsed <think> block.
   return answer.replace(/^\s*<think>[\s\S]*?<\/think>\s*/,'').slice(0,5000);
  } finally {clearTimeout(timeout);}
 }};
}
