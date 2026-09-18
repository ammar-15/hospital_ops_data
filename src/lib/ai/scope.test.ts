import {describe,expect,it} from 'vitest';
import {CLARIFICATION_RESPONSE,EFFECTIVENESS_RESPONSE,GREETING_RESPONSE,MEDICAL_RESPONSE,OUT_OF_SCOPE_RESPONSE,PROJECT_RESPONSE,scopeResponse} from './scope';
describe('assistant scope guard',()=>{
 it('blocks medical advice before provider use',()=>expect(scopeResponse('Should I go to Humber River or Sunnybrook for chest pain?')).toBe(MEDICAL_RESPONSE));
 it('blocks unrelated questions',()=>expect(scopeResponse('Write me a Python snake game.')).toBe(OUT_OF_SCOPE_RESPONSE));
 it('guards effectiveness claims',()=>expect(scopeResponse('Which intervention works best?')).toBe(EFFECTIVENESS_RESPONSE));
 it('allows dashboard questions',()=>expect(scopeResponse('Why does this say unavailable?')).toBeUndefined());
 it('uses the concise project explanation',()=>expect(scopeResponse('What is this project?')).toBe(PROJECT_RESPONSE));
 it('welcomes a greeting and recognizes the app wording',()=>{expect(scopeResponse('hello')).toBe(GREETING_RESPONSE);expect(scopeResponse('what is this app')).toBe(PROJECT_RESPONSE);});
 it('allows a plain-language follow-up only within a conversation',()=>{expect(scopeResponse('Explain in layman terms',true)).toBeUndefined();expect(scopeResponse('Explain in layman terms')).toBe(OUT_OF_SCOPE_RESPONSE);});
 it('allows a metaphor request within a conversation',()=>expect(scopeResponse('Give me a metaphor',true)).toBeUndefined());
 it('handles a frustrated clarification without rejecting the user',()=>expect(scopeResponse('bruh')).toBe(CLARIFICATION_RESPONSE));
});
