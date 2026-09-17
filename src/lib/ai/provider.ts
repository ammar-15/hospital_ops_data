export type AssistantMessage = {role:'system'|'user'|'assistant'; content:string};
export type AssistantProvider = {complete:(messages:AssistantMessage[])=>Promise<string>};
