export const OUT_OF_SCOPE_RESPONSE = 'I’m here to help with the Ontario Hospital Quality Improvement Explorer and its data. Ask me about the hospitals, indicators, intervention categories, methodology, filters, or how to use the dashboard.';
export const MEDICAL_RESPONSE = 'This explorer analyzes public hospital quality-improvement reporting and is not a medical decision tool. I can explain the hospital data or indicators shown here, but I can’t provide medical advice.';
export const LIVE_DATA_RESPONSE = 'No. This project uses Ontario Quality Improvement Plan reporting. It shows reported plans, implementation information, and historical reporting, not live hospital conditions.';
export const EFFECTIVENESS_RESPONSE = 'The project can show what hospitals reported trying and whether those changes were implemented, but it cannot reliably compare intervention effectiveness because the reporting periods are not consistently comparable.';
export const RANKING_RESPONSE = 'This project does not rank hospitals. It is designed to help users inspect reported plans, implementation information, and reporting quality without creating performance league tables.';
export const PROJECT_RESPONSE = 'This dashboard shows what Ontario hospitals say they are doing to improve emergency-department flow. It shows plans and reported implementation—not live wait times, hospital rankings, or proof that a change worked.';
export const GREETING_RESPONSE = 'Hi — I can explain this dashboard, its hospital reporting data, filters, indicators, and methodology.';

const medical = /\b(medication|medicine|diagnos(?:is|e)|do i have|should i go to (?:the )?(?:er|emergency)|which hospital should i go|chest pain|treatment|symptoms?)\b/i;
const allowed = /\b(dashboard|project|hospital|qip|quality improvement|emergency|\bed\b|indicator|intervention|implementation|filter|methodology|reporting|dataset|workplan|progress report|ambulance|offload|wait|flow|category|chart|metric|unavailable|compare|this mean|what am i looking at|live data)\b/i;
const followUp = /\b(explain|simple|simpler|plain|layman|layperson|tell me more|that mean|this mean)\b/i;
const greeting = /^\s*(?:hi|hello|hey|good (?:morning|afternoon|evening))[!. ]*$/i;
const projectQuestion = /^\s*(?:what(?:'s| is) (?:this |the )?(?:project|app|dashboard)|what does (?:this |the )?(?:project|app|dashboard) mean)(?:\s+(?:in )?(?:simple|plain|layman(?:'s)?|everyday) terms)?\??\s*$/i;
export function scopeResponse(message:string,hasHistory=false):string|undefined {
 if (medical.test(message)) return MEDICAL_RESPONSE;
 if (/\b(live|real[ -]?time|today(?:'s)?|current (?:er|emergency|wait))/i.test(message)) return LIVE_DATA_RESPONSE;
 if (/\b(which|what).{0,50}\b(best|most effective|works best|worked best|successful)\b|\beffectiveness\b/i.test(message)) return EFFECTIVENESS_RESPONSE;
 if (/\b(best|worst|rank|ranking|top hospital)\b/i.test(message)) return RANKING_RESPONSE;
 if (greeting.test(message)) return GREETING_RESPONSE;
 if (projectQuestion.test(message)) return PROJECT_RESPONSE;
 if (hasHistory && followUp.test(message)) return undefined;
 if (!allowed.test(message)) return OUT_OF_SCOPE_RESPONSE;
 return undefined;
}
